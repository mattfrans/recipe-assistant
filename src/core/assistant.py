"""
Main Recipe Assistant class that coordinates between the model, vector store, and tools.
"""

from typing import List, Dict, Optional, Union
import logging
from pathlib import Path
import torch
import numpy as np

from .model import ModelManager
from .vector_store import RecipeVectorStore

logger = logging.getLogger(__name__)

class RecipeAssistant:
    def __init__(
        self,
        vector_store_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize the Recipe Assistant.
        
        Args:
            vector_store_path: Optional path to existing vector store
            device: Optional device specification for models
        """
        # Initialize components
        self.model_manager = ModelManager(device=device)
        self.vector_store = RecipeVectorStore(
            dimension=384,  # Dimension for all-MiniLM-L6-v2
            index_path=vector_store_path
        )
        
        # Define prompt templates
        self.qa_template = """
        Answer the following cooking or recipe related question. Use the provided context if relevant.
        
        Context: {context}
        
        Question: {question}
        
        Answer: """
        
        logger.info("Recipe Assistant initialized successfully")

    def add_recipe(self, recipe_data: Dict) -> int:
        """
        Add a new recipe to the assistant's knowledge base.
        
        Args:
            recipe_data: Dictionary containing recipe information
            
        Returns:
            Recipe ID
        """
        try:
            # Create recipe text representation for embedding
            recipe_text = self._create_recipe_text(recipe_data)
            
            # Generate embedding
            embedding = self.model_manager.get_embeddings([recipe_text])[0]
            
            # Add to vector store
            recipe_id = self.vector_store.add_recipe(
                recipe_data,
                embedding.cpu().numpy()
            )
            
            return recipe_id
            
        except Exception as e:
            logger.error(f"Error adding recipe: {str(e)}")
            raise

    def query(self, question: str, k: int = 3) -> str:
        """
        Answer a cooking or recipe related question.
        
        Args:
            question: User's question
            k: Number of relevant recipes to consider
            
        Returns:
            Assistant's response
        """
        try:
            # Generate question embedding
            question_embedding = self.model_manager.get_embeddings([question])[0]
            
            # Search for relevant recipes
            results = self.vector_store.search_recipes(
                question_embedding.cpu().numpy(),
                k=k
            )
            
            # Create context from relevant recipes
            context = self._create_context(results)
            
            # Generate response using Phi-2
            prompt = self.qa_template.format(
                context=context,
                question=question
            )
            
            response = self.model_manager.generate_text(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def find_similar_recipes(
        self,
        recipe_id: Optional[int] = None,
        recipe_text: Optional[str] = None,
        k: int = 5
    ) -> List[Dict]:
        """
        Find similar recipes based on a reference recipe or description.
        
        Args:
            recipe_id: Optional ID of reference recipe
            recipe_text: Optional text description to search with
            k: Number of similar recipes to return
            
        Returns:
            List of similar recipes with their similarity scores
        """
        try:
            if recipe_id is not None:
                # Get reference recipe
                recipe = self.vector_store.get_recipe(recipe_id)
                if not recipe:
                    raise ValueError(f"Recipe with ID {recipe_id} not found")
                query_text = self._create_recipe_text(recipe)
            elif recipe_text is not None:
                query_text = recipe_text
            else:
                raise ValueError("Either recipe_id or recipe_text must be provided")
            
            # Generate embedding
            query_embedding = self.model_manager.get_embeddings([query_text])[0]
            
            # Search vector store
            results = self.vector_store.search_recipes(
                query_embedding.cpu().numpy(),
                k=k
            )
            
            return [
                {
                    'recipe': recipe_data,
                    'similarity_score': 1 - (distance / 2)  # Convert L2 distance to similarity
                }
                for _, distance, recipe_data in results
            ]
            
        except Exception as e:
            logger.error(f"Error finding similar recipes: {str(e)}")
            raise

    def _create_recipe_text(self, recipe_data: Dict) -> str:
        """Create a text representation of a recipe for embedding."""
        parts = [
            recipe_data.get('title', ''),
            recipe_data.get('description', ''),
            'Ingredients: ' + '; '.join(recipe_data.get('ingredients', [])),
            'Instructions: ' + ' '.join(recipe_data.get('instructions', [])),
            'Tags: ' + ', '.join(recipe_data.get('tags', []))
        ]
        return ' '.join(filter(None, parts))

    def _create_context(self, results: List[tuple]) -> str:
        """Create a context string from search results."""
        context_parts = []
        for _, _, recipe_data in results:
            context_parts.append(
                f"Recipe: {recipe_data.get('title', '')}\n"
                f"Description: {recipe_data.get('description', '')}\n"
                f"Ingredients: {'; '.join(recipe_data.get('ingredients', []))}\n"
                f"Instructions: {' '.join(recipe_data.get('instructions', []))}\n"
            )
        return '\n'.join(context_parts)

    def save_state(self, path: str):
        """Save the assistant's state to disk."""
        try:
            self.vector_store.save(path)
            logger.info(f"Saved assistant state to {path}")
        except Exception as e:
            logger.error(f"Error saving assistant state: {str(e)}")
            raise

    def load_state(self, path: str):
        """Load the assistant's state from disk."""
        try:
            self.vector_store.load(path)
            logger.info(f"Loaded assistant state from {path}")
        except Exception as e:
            logger.error(f"Error loading assistant state: {str(e)}")
            raise
