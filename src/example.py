"""
Example usage of the Recipe Assistant.
"""

from core.assistant import RecipeAssistant
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Initialize the assistant
    assistant = RecipeAssistant()
    
    # Example recipe data
    chocolate_cake = {
        'title': 'Classic Chocolate Cake',
        'description': 'A rich and moist chocolate cake perfect for any occasion.',
        'ingredients': [
            '2 cups all-purpose flour',
            '2 cups sugar',
            '3/4 cup unsweetened cocoa powder',
            '2 teaspoons baking soda',
            '1 teaspoon salt',
            '2 eggs',
            '1 cup milk',
            '1/2 cup vegetable oil',
            '2 teaspoons vanilla extract',
            '1 cup boiling water'
        ],
        'instructions': [
            'Preheat oven to 350°F (175°C)',
            'Mix dry ingredients in a large bowl',
            'Add eggs, milk, oil, and vanilla',
            'Stir in boiling water',
            'Pour into greased 9x13 inch baking pan',
            'Bake for 30-35 minutes'
        ],
        'tags': ['dessert', 'chocolate', 'cake', 'baking']
    }
    
    # Add recipe to assistant
    recipe_id = assistant.add_recipe(chocolate_cake)
    print(f"Added recipe with ID: {recipe_id}")
    
    # Example queries
    questions = [
        "How do I make a chocolate cake?",
        "What can I substitute for eggs in the chocolate cake recipe?",
        "How would I adjust the recipe to make a smaller portion?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        response = assistant.query(question)
        print(f"Response: {response}")
    
    # Find similar recipes
    similar_recipes = assistant.find_similar_recipes(recipe_id=recipe_id)
    print("\nSimilar recipes:")
    for recipe in similar_recipes:
        print(f"- {recipe['recipe']['title']} (Similarity: {recipe['similarity_score']:.2f})")
    
    # Save the assistant's state
    assistant.save_state("recipe_assistant_state")

if __name__ == "__main__":
    main()
