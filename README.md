# Recipe Assistant

An AI-powered recipe management and assistance system optimized for CPU usage and local execution.

## Features

- Store and retrieve recipes using FAISS vector database
- Answer questions about recipes and cooking techniques
- Suggest ingredient substitutions
- Scale recipe portions
- Find similar recipes based on ingredients or cooking methods

## Technical Stack

- Python 3.11
- LangChain for orchestration
- Local AI Models (optimized for CPU)
- FAISS for vector storage
- Sentence Transformers for embeddings

## System Requirements

- Python 3.11.7
- 8GB RAM minimum
- CPU: Intel Core i5/i7 or equivalent
- Storage: 2GB free space

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/recipe_assistant.git
cd recipe_assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
recipe_assistant/
├── src/
│   ├── core/
│   │   ├── model.py       # Model initialization and text generation
│   │   ├── vector_store.py # Recipe storage and retrieval
│   │   └── assistant.py   # Main assistant logic
│   └── example.py         # Usage examples
├── requirements.txt
└── README.md
```

## Memory Optimization

This application is optimized for systems with limited resources:
- Uses CPU-optimized PyTorch build
- Implements model quantization via bitsandbytes
- Efficient vector storage with FAISS-CPU
- Memory-conscious data handling

## Usage

1. Initialize the recipe assistant:
   ```python
   from recipe_assistant.core import RecipeAssistant
   
   assistant = RecipeAssistant()
   ```

2. Ask questions or get recipe assistance:
   ```python
   response = assistant.query("How do I make a chocolate cake?")
   print(response)
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your chosen license]
