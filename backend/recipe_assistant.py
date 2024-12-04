import faiss
import numpy as np
from typing import List, Dict
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
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
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

    def initialize(self):
        try:
            print(f"Loading {self.model_name} model...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Simple model loading configuration
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float32,  # Use float32 for CPU
                device_map="auto"
            )
            
            # Move model to CPU
            self.model = self.model.to("cpu")
            
            print(f"{self.model_name} model loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False

    def is_available(self):
        return self.model is not None and self.tokenizer is not None

    def generate_text(self, prompt: str, max_length: int = 100) -> str:
        if not self.is_available():
            return None
            
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to("cpu") for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the prompt from the response
            response = response[len(prompt):].strip()
            return response
        except Exception as e:
            print(f"Error generating text: {str(e)}")
            return None

    def get_embedding(self, text: str) -> np.ndarray:
        """Get text embedding using the model's hidden states."""
        if not self.is_available():
            return None
            
        try:
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
            
            # Use the last hidden state's [CLS] token as the embedding
            embedding = outputs.hidden_states[-1][0, 0].cpu().numpy()
            return embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
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
        query = query.lower()
        scored_recipes = []
        
        for recipe in self.recipes:
            # Ensure recipe has required fields
            if not recipe.get('name') or not recipe.get('ingredients') or not recipe.get('instructions'):
                continue
                
            score = 0
            
            # Check recipe name
            if any(word in recipe['name'].lower() for word in query.split()):
                score += 3
            
            # Check ingredients
            for ingredient in recipe['ingredients']:
                if any(word in ingredient.lower() for word in query.split()):
                    score += 2
            
            # Check cuisine
            if 'cuisine' in recipe and any(word in recipe['cuisine'].lower() for word in query.split()):
                score += 1
            
            if score > 0:
                # Ensure recipe format is consistent
                formatted_recipe = {
                    'name': recipe['name'],
                    'cuisine': recipe.get('cuisine', ''),
                    'prep_time': recipe.get('prep_time', ''),
                    'cook_time': recipe.get('cook_time', ''),
                    'servings': recipe.get('servings', 0),
                    'ingredients': recipe['ingredients'],
                    'instructions': recipe['instructions']
                }
                scored_recipes.append((score, formatted_recipe))
        
        # Sort by score and return top k
        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        return [recipe for score, recipe in scored_recipes[:k]]

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
            prompt = f"""You are a helpful cooking assistant. Suggest a healthy substitution for {ingredient} in cooking.
            Consider common dietary restrictions and provide a practical alternative.
            Response format: Just return the substitute ingredient name, nothing else.
            For example:
            - butter -> olive oil
            - eggs -> flax eggs
            - beef -> mushrooms
            
            {ingredient} ->"""
            
            suggestion = self.model_manager.generate_text(prompt, max_length=50)
            if suggestion:
                # Clean up the response
                suggestion = suggestion.split('\n')[0].strip()
                suggestion = suggestion.split('->')[0].strip()
                return suggestion
            
            return self.default_substitutions.get(ingredient.lower(), 
                f"No substitution found for {ingredient}. Try an online search for alternatives.")
        except Exception as e:
            print(f"Error generating substitution: {str(e)}")
            return self.default_substitutions.get(ingredient.lower(), 
                f"No substitution found for {ingredient}. Try an online search for alternatives.")

class RecipeVectorStore:
    def __init__(self, recipes: List[Dict], model_manager: ModelManager):
        self.recipes = recipes
        self.model_manager = model_manager
        self.dimension = 2560  # Phi-2's hidden size
        self.index = None
        self.fallback_search = SimpleRecipeSearch(recipes)
        self._initialize_index()

    def _initialize_index(self):
        if not self.model_manager.is_available():
            print("Model not available, using fallback search...")
            return

        try:
            print("Building recipe search index...")
            self.index = faiss.IndexFlatL2(self.dimension)
            self._build_index()
            print("Recipe search index built successfully!")
        except Exception as e:
            print(f"Error initializing index: {str(e)}")
            self.index = None

    def _build_index(self):
        if not self.model_manager.is_available() or not self.index:
            return

        embeddings = []
        for recipe in tqdm(self.recipes, desc="Building recipe embeddings"):
            # Create a searchable text representation of the recipe
            recipe_text = f"{recipe['name']} - {recipe.get('cuisine', '')}. "
            recipe_text += f"Ingredients: {', '.join(recipe['ingredients'])}. "
            recipe_text += f"Instructions: {' '.join(recipe['instructions'])}"
            
            embedding = self.model_manager.get_embedding(recipe_text)
            if embedding is not None:
                embeddings.append(embedding)

        if embeddings:
            embeddings_array = np.array(embeddings)
            self.index.add(embeddings_array)

    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for recipes using embeddings if available, otherwise fall back to text search."""
        if not self.model_manager.is_available() or self.index is None:
            print("Using fallback text search...")
            return self.fallback_search.search(query, k)

        try:
            # Get query embedding
            query_embedding = self.model_manager.get_embedding(query)
            if query_embedding is None:
                return self.fallback_search.search(query, k)

            # Search using FAISS
            distances, indices = self.index.search(np.array([query_embedding]), k)
            
            # Format and return results
            results = []
            for idx in indices[0]:
                if idx < len(self.recipes):
                    recipe = self.recipes[idx]
                    # Ensure recipe format is consistent
                    formatted_recipe = {
                        'name': recipe['name'],
                        'cuisine': recipe.get('cuisine', ''),
                        'prep_time': recipe.get('prep_time', ''),
                        'cook_time': recipe.get('cook_time', ''),
                        'servings': recipe.get('servings', 0),
                        'ingredients': recipe['ingredients'],
                        'instructions': recipe['instructions']
                    }
                    results.append(formatted_recipe)
            
            return results
        except Exception as e:
            print(f"Error in vector search: {str(e)}")
            return self.fallback_search.search(query, k)

class RecipeAssistant:
    def __init__(self, recipes):
        self.recipes = recipes
        self.model_manager = ModelManager()
        self.model_manager.initialize()
        self.vector_store = RecipeVectorStore(recipes, self.model_manager)
        self.substitution = IngredientSubstitution(self.model_manager)

    def search_recipes(self, query: str) -> List[Dict]:
        """Search for recipes based on the query."""
        if not self.model_manager.is_available():
            return self.vector_store.fallback_search.search(query)
        return self.vector_store.search(query)

    def get_substitution(self, ingredient: str) -> str:
        """Get substitution for an ingredient."""
        return self.substitution.suggest_substitution(ingredient)

    def answer_question(self, question: str) -> str:
        """Answer general cooking questions."""
        if not self.model_manager.is_available():
            return "I'm sorry, but I'm currently operating in fallback mode and can only help with recipe searches and basic substitutions. Please try again later for more complex questions."
        
        prompt = f"""You are a helpful cooking assistant. Answer the following cooking-related question:
        Question: {question}
        
        Please provide a clear and concise answer focused on cooking techniques, food science, or kitchen tips.
        Answer: """
        
        try:
            response = self.model_manager.generate_text(prompt, max_length=200)
            return response if response else "I'm sorry, I couldn't generate a response. Please try rephrasing your question."
        except Exception as e:
            print(f"Error generating answer: {str(e)}")
            return "I'm sorry, I encountered an error while trying to answer your question. Please try again."

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
