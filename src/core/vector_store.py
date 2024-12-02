"""
Vector store implementation using FAISS for recipe storage and retrieval.
"""

import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RecipeVectorStore:
    def __init__(self, dimension: int = 384, index_path: Optional[str] = None):
        """
        Initialize the FAISS vector store for recipes.
        
        Args:
            dimension: Dimension of the embedding vectors (384 for all-MiniLM-L6-v2)
            index_path: Optional path to load existing index
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.recipes: Dict[int, Dict] = {}  # Map IDs to recipe data
        
        if index_path and os.path.exists(index_path):
            self.load(index_path)

    def add_recipe(self, recipe_data: Dict, embedding: np.ndarray) -> int:
        """
        Add a recipe and its embedding to the vector store.
        
        Args:
            recipe_data: Dictionary containing recipe information
            embedding: Recipe embedding vector
            
        Returns:
            Recipe ID
        """
        try:
            # Ensure embedding is the correct shape
            embedding = embedding.reshape(1, -1)
            if embedding.shape[1] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.dimension}, got {embedding.shape[1]}")
            
            # Add to FAISS index
            recipe_id = len(self.recipes)
            self.index.add(embedding)
            
            # Store recipe data
            self.recipes[recipe_id] = {
                **recipe_data,
                'added_at': datetime.now().isoformat()
            }
            
            logger.info(f"Added recipe '{recipe_data.get('title', 'Untitled')}' with ID {recipe_id}")
            return recipe_id
            
        except Exception as e:
            logger.error(f"Error adding recipe: {str(e)}")
            raise

    def search_recipes(
        self, 
        query_embedding: np.ndarray, 
        k: int = 5
    ) -> List[Tuple[int, float, Dict]]:
        """
        Search for similar recipes using the query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of tuples containing (recipe_id, distance, recipe_data)
        """
        try:
            # Reshape query embedding
            query_embedding = query_embedding.reshape(1, -1)
            
            # Search the FAISS index
            distances, indices = self.index.search(query_embedding, k)
            
            # Format results
            results = []
            for idx, (distance, recipe_idx) in enumerate(zip(distances[0], indices[0])):
                if recipe_idx >= 0:  # FAISS returns -1 for empty slots
                    recipe_data = self.recipes.get(int(recipe_idx))
                    if recipe_data:
                        results.append((int(recipe_idx), float(distance), recipe_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching recipes: {str(e)}")
            raise

    def save(self, path: str):
        """
        Save the vector store to disk.
        
        Args:
            path: Path to save the index and metadata
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{path}.index")
            
            # Save recipe metadata
            with open(f"{path}.metadata", 'wb') as f:
                pickle.dump(self.recipes, f)
                
            logger.info(f"Saved vector store to {path}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise

    def load(self, path: str):
        """
        Load the vector store from disk.
        
        Args:
            path: Path to load the index and metadata from
        """
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{path}.index")
            
            # Load recipe metadata
            with open(f"{path}.metadata", 'rb') as f:
                self.recipes = pickle.load(f)
                
            logger.info(f"Loaded vector store from {path} with {len(self.recipes)} recipes")
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise

    def get_recipe(self, recipe_id: int) -> Optional[Dict]:
        """
        Get recipe data by ID.
        
        Args:
            recipe_id: Recipe ID
            
        Returns:
            Recipe data dictionary or None if not found
        """
        return self.recipes.get(recipe_id)
