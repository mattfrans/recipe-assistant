"""
Model initialization and management for the Recipe Assistant.
Handles the setup of the local Phi-2 model and embeddings model.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, device: Optional[str] = None):
        """
        Initialize the model manager with Phi-2 and sentence transformer models.
        
        Args:
            device: Optional device specification ('cuda' or 'cpu'). If None, automatically detects.
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._init_phi2_model()
        self._init_embedding_model()

    def _init_phi2_model(self):
        """Initialize the Phi-2 model for text generation."""
        try:
            model_name = "microsoft/phi-2"
            logger.info(f"Loading {model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                device_map="auto",
                trust_remote_code=True
            )
            
            logger.info(f"Successfully loaded {model_name}")
        except Exception as e:
            logger.error(f"Error loading Phi-2 model: {str(e)}")
            raise

    def _init_embedding_model(self):
        """Initialize the sentence transformer model for embeddings."""
        try:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"Loading {model_name}...")
            
            self.embedding_model = SentenceTransformer(model_name)
            self.embedding_model.to(self.device)
            
            logger.info(f"Successfully loaded {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise

    def generate_text(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate text using the Phi-2 model.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            
        Returns:
            Generated text response
        """
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error in text generation: {str(e)}")
            raise

    def get_embeddings(self, texts: List[str]) -> torch.Tensor:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            Tensor of embeddings
        """
        try:
            return self.embedding_model.encode(texts, convert_to_tensor=True)
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
