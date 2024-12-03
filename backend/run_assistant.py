import json
from recipe_assistant import RecipeAssistant

def main():
    try:
        # Load recipes
        with open('data/recipes.json', 'r') as file:
            recipes = json.load(file)['recipes']
            
        assistant = RecipeAssistant(recipes)
        
        # Test recipe search
        print("\nSearching for recipes with chicken and garlic:")
        print("-" * 50)
        result = assistant.process_query("What can I cook with chicken and garlic?")
        print(result)
        
        print("\nFinding substitution for soy sauce:")
        print("-" * 50)
        result = assistant.process_query("What can I substitute for soy sauce?")
        print(result)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Don't worry! The assistant will use fallback methods when the model is rate-limited.")

if __name__ == "__main__":
    main()
