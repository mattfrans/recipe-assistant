from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from recipe_assistant import RecipeAssistant

app = Flask(__name__)
CORS(app)

# Initialize the recipe assistant
assistant = None

def init_assistant():
    global assistant
    try:
        with open('data/recipes.json', 'r') as file:
            recipes = json.load(file)['recipes']
        assistant = RecipeAssistant(recipes)
        print("Recipe Assistant initialized successfully!")
    except Exception as e:
        print(f"Error initializing assistant: {str(e)}")

@app.route('/api/search', methods=['POST'])
def search_recipes():
    if not assistant:
        return jsonify({"error": "Assistant not initialized"}), 500
    
    data = request.json
    query = data.get('query', '')
    
    try:
        result = assistant.search_recipes(query)
        return jsonify({"recipes": result if isinstance(result, list) else [result] if result else []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/substitute', methods=['POST'])
def get_substitution():
    if not assistant:
        return jsonify({"error": "Assistant not initialized"}), 500
    
    data = request.json
    ingredient = data.get('ingredient', '')
    
    try:
        result = assistant.get_substitution(ingredient)
        return jsonify({"substitution": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    if not assistant:
        return jsonify({"error": "Assistant not initialized"}), 500
    
    data = request.json
    question = data.get('question', '')
    
    try:
        result = assistant.answer_question(question)
        return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_assistant()
    app.run(port=5000)
