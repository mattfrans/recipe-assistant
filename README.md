# AI Recipe Assistant

A smart recipe assistant powered by Phi-2 that helps you find recipes, suggest ingredient substitutions, and answer cooking-related questions.

## Features

- 🔍 **Recipe Search**: Find recipes based on available ingredients
- 🔄 **Ingredient Substitutions**: Get smart suggestions for ingredient replacements
- ❓ **Cooking Q&A**: Ask questions about cooking techniques and recipes
- 💡 **Smart Recommendations**: Uses AI to understand context and provide relevant suggestions
- ⚡ **Local Processing**: Runs entirely locally using the Phi-2 model
- 🔋 **Fallback Mechanisms**: Built-in fallbacks when model is rate-limited

## Tech Stack

### Backend
- **AI Model**: Microsoft Phi-2 (2.7B parameters)
- **Vector Store**: FAISS for efficient recipe search
- **Framework**: LangChain for agent and tool management
- **API**: Flask with CORS support
- **Language**: Python 3.x

### Frontend
- **Framework**: Next.js 14
- **UI**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Components**: Custom UI components with Radix UI

## Project Structure

```
recipe-assistant/
├── backend/
│   ├── data/
│   │   └── recipes.json         # Recipe database
│   ├── recipe_assistant.py      # Main assistant implementation
│   ├── run_assistant.py         # Test script
│   └── requirements.txt         # Python dependencies
│
└── frontend/
    ├── app/                     # Next.js app directory
    ├── components/              # React components
    ├── lib/                     # Utility functions
    └── package.json             # Node.js dependencies
```

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the backend server:
```bash
python run_assistant.py
```

The server will start on `http://localhost:5000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Finding Recipes**
   - Enter ingredients you have
   - Ask for specific types of dishes
   - Get recipe suggestions with instructions

2. **Ingredient Substitutions**
   - Ask "What can I substitute for [ingredient]?"
   - Get context-aware substitution suggestions
   - Learn about substitution ratios

3. **Cooking Questions**
   - Ask about cooking techniques
   - Get help with recipe modifications
   - Learn about ingredient combinations

## Note on Rate Limits

The Phi-2 model may occasionally hit rate limits. When this happens, the assistant automatically falls back to:
- Pre-defined ingredient substitutions
- Simple text-based recipe search
- Basic cooking advice

Wait about an hour before trying AI-powered features again when rate-limited.

## Development

- Backend API endpoints are CORS-enabled for local development
- The frontend communicates with the backend via REST API
- Recipe data is stored in a JSON format for easy updates
- Vector embeddings are generated on startup for efficient search

## Initial Dataset

The system comes with a curated set of 10-20 recipes to demonstrate core functionality. You can expand this by adding more recipes to `backend/data/recipes.json`.

## License

This project is open-source and available under the MIT License.
