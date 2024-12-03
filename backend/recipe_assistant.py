import faiss
import numpy as np
from typing import List, Dict
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain_community.llms import HuggingFacePipeline
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
import torch
import json
import time
from functools import lru_cache
from tqdm import tqdm
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

print("Loading recipes...")
with open('data/recipes.json', 'r') as file:
    recipes = json.load(file)['recipes']

class ModelManager:
    def __init__(self, model_name="microsoft/phi-2"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        print("Model loading disabled for testing")

    def initialize(self):
        # Temporarily disable model loading for testing
        return False

    def is_available(self):
        return False

    def get_embedding(self, text):
        return None

class SimpleRecipeSearch:
    """Fallback search when embeddings are not available"""
    def __init__(self, recipes: List[Dict]):
        self.recipes = recipes

    def _score_recipe(self, recipe: Dict, query: str) -> float:
        """Score a recipe based on query match."""
        query = query.lower()
        score = 0
        
        # Check recipe name
        if query in recipe['name'].lower():
            score += 3
            
        # Check ingredients
        for ingredient in recipe['ingredients']:
            if query in ingredient.lower():
                score += 2
                
        # Check cuisine
        if 'cuisine' in recipe and query in recipe['cuisine'].lower():
            score += 1
            
        return score

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for recipes using simple text matching."""
        scored_recipes = [
            (self._score_recipe(recipe, query), recipe)
            for recipe in self.recipes
        ]
        
        # Sort by score and return top k
        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        return [recipe for score, recipe in scored_recipes[:k] if score > 0]

class RecipeVectorStore:
    def __init__(self, recipes: List[Dict], model_manager: ModelManager):
        self.recipes = recipes
        self.model_manager = model_manager
        self.dimension = 2560  # Phi-2's hidden size
        self.index = None
        self.fallback_search = SimpleRecipeSearch(recipes)
        self._initialize_index()

    def _initialize_index(self):
        if self.model_manager.is_available():
            print("\nInitializing recipe vector store...")
            self.index = faiss.IndexFlatL2(self.dimension)
            self._build_index()

    def _build_index(self):
        if not self.model_manager.is_available():
            return

        print("Building recipe index...")
        vectors = []
        for recipe in tqdm(self.recipes, desc="Processing recipes"):
            text = f"{recipe['name']} {' '.join(recipe['ingredients'])} {recipe['instructions']}"
            vector = self.model_manager.get_embedding(text)
            if vector is not None:
                vectors.append(vector)
        
        if vectors:
            vectors = np.vstack(vectors)
            self.index.add(vectors)
            print("Recipe index built successfully!")

    def search(self, query: str, k: int = 3):
        try:
            # First try the fallback search
            results = self.fallback_search.search(query, k)
            if results:
                return results
            
            # If no results, try vector search if available
            if self.model_manager.is_available() and self.index is not None:
                query_embedding = self.model_manager.get_embedding(query)
                if query_embedding is not None:
                    D, I = self.index.search(query_embedding.reshape(1, -1), k)
                    return [self.recipes[i] for i in I[0] if i >= 0]
            
            return results
        except Exception as e:
            print(f"Search error: {str(e)}")
            # Always fall back to simple search
            return self.fallback_search.search(query, k)

class IngredientSubstitution:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        # Fallback substitutions when model is not available
        self.default_substitutions = {
            'chicken breast': 'tofu',
            'beef': 'mushrooms',
            'milk': 'almond milk',
            'cream': 'coconut cream',
            'soy sauce': 'coconut aminos',
            'eggs': 'flax eggs',
            'butter': 'olive oil',
            'cheese': 'nutritional yeast',
            'heavy cream': 'coconut cream',
            'ground beef': 'lentils',
            'fish sauce': 'coconut aminos',
            'oyster sauce': 'mushroom sauce',
            'worcestershire sauce': 'soy sauce'
        }

    def suggest_substitution(self, ingredient: str) -> str:
        if not self.model_manager.is_available():
            print("Using fallback substitutions (model not available)...")
            return self.default_substitutions.get(ingredient.lower(), 
                f"No substitution found for {ingredient}. Try an online search for alternatives.")

        try:
            prompt = f"Suggest a healthy substitution for {ingredient} in cooking. Return only the substitute ingredient name, nothing else."
            inputs = self.model_manager.tokenizer(prompt, return_tensors="pt", max_length=512)
            with torch.no_grad():
                outputs = self.model_manager.model.generate(**inputs, max_length=100, num_return_sequences=1)
            suggestion = self.model_manager.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            return suggestion if suggestion else self.default_substitutions.get(ingredient.lower(), 
                f"No substitution found for {ingredient}. Try an online search for alternatives.")
        except Exception as e:
            print(f"Error generating substitution: {str(e)}")
            return self.default_substitutions.get(ingredient.lower(), 
                f"No substitution found for {ingredient}. Try an online search for alternatives.")

class RecipeAssistant:
    def __init__(self, recipes):
        print("\nInitializing Recipe Assistant...")
        self.model_manager = ModelManager()
        self.model_manager.initialize()
        
        self.vector_store = RecipeVectorStore(recipes, self.model_manager)
        self.substitution = IngredientSubstitution(self.model_manager)
        
        # Create tools
        self.tools = [
            Tool(
                name="Recipe Search",
                func=lambda q: str(self.vector_store.search(q)),
                description="Search for recipes based on ingredients or description"
            ),
            Tool(
                name="Ingredient Substitution",
                func=lambda i: self.substitution.suggest_substitution(i),
                description="Suggest substitutions for ingredients"
            )
        ]
        print("\nRecipe Assistant is ready!")

    def process_query(self, query: str) -> str:
        try:
            if "substitute" in query.lower() or "substitution" in query.lower():
                # Extract ingredient from query
                words = query.lower().split()
                try:
                    idx = words.index("substitute") if "substitute" in words else words.index("substitution")
                    ingredient = " ".join(words[idx+1:]).strip("?.,! for")
                    return self.substitution.suggest_substitution(ingredient)
                except ValueError:
                    return "Please specify an ingredient for substitution."
            else:
                # Assume it's a recipe search
                results = self.vector_store.search(query)
                if not results:
                    return "No matching recipes found. Try different ingredients or a broader search."
                
                response = "Here are some recipes you might like:\n\n"
                for i, recipe in enumerate(results, 1):
                    response += f"{i}. {recipe['name']}\n"
                    response += f"   Ingredients: {', '.join(recipe['ingredients'])}\n"
                    response += f"   Instructions: {recipe['instructions']}\n\n"
                return response
        except Exception as e:
            return f"An error occurred: {str(e)}\nPlease try again with a different query."

# Initialize the recipe assistant
recipe_assistant = None

def init_assistant():
    global recipe_assistant
    if recipe_assistant is None:
        print("Loading recipes...")
        with open('data/recipes.json', 'r') as f:
            recipes = json.load(f)['recipes']
        
        print("\nInitializing Recipe Assistant...")
        recipe_assistant = RecipeAssistant(recipes)

@app.route('/api/search', methods=['POST'])
def search_recipes():
    try:
        init_assistant()
        data = request.json
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Use the simple search directly
        search = SimpleRecipeSearch(recipes)
        found_recipes = search.search(query)
        
        if not found_recipes:
            return jsonify({'recipes': [], 'message': 'No recipes found'}), 200
            
        return jsonify({'recipes': found_recipes})
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/substitute', methods=['POST'])
def get_substitution():
    try:
        init_assistant()
        data = request.json
        ingredient = data.get('ingredient', '')
        if not ingredient:
            return jsonify({'error': 'Ingredient is required'}), 400
        
        substitution = recipe_assistant.substitution.suggest_substitution(ingredient)
        return jsonify({'substitution': substitution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
