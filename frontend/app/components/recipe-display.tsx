'use client'

import { Button } from '@/components/ui/button'
import { Recipe } from '../types/recipe'

interface RecipeDisplayProps {
  recipe: Recipe | null
  onSubstituteClick: (ingredient: string) => void
}

export default function RecipeDisplay({ recipe, onSubstituteClick }: RecipeDisplayProps) {
  if (!recipe) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-amber-100 rounded-full flex items-center justify-center">
          <span className="text-2xl">🍳</span>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Recipe Selected</h3>
        <p className="text-gray-500">
          You can:
          <br />
          1. Browse all recipes using the button above
          <br />
          2. Search for specific recipes
          <br />
          3. Ask me to recommend something!
        </p>
      </div>
    )
  }

  // Ensure recipe has all required properties with defaults
  const safeRecipe = {
    ...recipe,
    ingredients: recipe.ingredients || [],
    instructions: recipe.instructions || []
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {/* Recipe Header */}
      <div className="bg-amber-100 p-6">
        <h2 className="text-2xl font-bold text-amber-900 mb-2">{safeRecipe.name}</h2>
        {safeRecipe.cuisine && (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-200 text-amber-800">
            {safeRecipe.cuisine}
          </span>
        )}
      </div>

      <div className="p-6">
        {/* Recipe Info */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {safeRecipe.prep_time && (
            <div className="text-center">
              <span className="block text-gray-500 text-sm">Prep Time</span>
              <span className="block font-medium">{safeRecipe.prep_time}</span>
            </div>
          )}
          {safeRecipe.cook_time && (
            <div className="text-center">
              <span className="block text-gray-500 text-sm">Cook Time</span>
              <span className="block font-medium">{safeRecipe.cook_time}</span>
            </div>
          )}
          {safeRecipe.servings && (
            <div className="text-center">
              <span className="block text-gray-500 text-sm">Servings</span>
              <span className="block font-medium">{safeRecipe.servings}</span>
            </div>
          )}
        </div>

        {/* Ingredients */}
        {safeRecipe.ingredients.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              <span className="mr-2">📝</span>
              Ingredients
            </h3>
            <ul className="space-y-3">
              {safeRecipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                  <span>{ingredient}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-amber-600 hover:text-amber-700 hover:bg-amber-50"
                    onClick={() => onSubstituteClick(ingredient)}
                  >
                    Find Substitute
                  </Button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Instructions */}
        {safeRecipe.instructions.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              <span className="mr-2">👩‍🍳</span>
              Instructions
            </h3>
            <ol className="space-y-4">
              {safeRecipe.instructions.map((step, index) => (
                <li key={index} className="flex">
                  <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-amber-100 text-amber-800 font-medium mr-3">
                    {index + 1}
                  </span>
                  <p className="text-gray-700 pt-1">{step}</p>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
