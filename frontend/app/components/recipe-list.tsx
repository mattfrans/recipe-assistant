'use client'

import { useState, useEffect } from 'react'
import { Recipe } from '../types/recipe'

interface RecipeListProps {
  expandedRecipe: Recipe | null
  onRecipeClick: (recipe: Recipe | null) => void
  onSubstituteClick: (ingredient: string) => void
}

export default function RecipeList({ expandedRecipe, onRecipeClick, onSubstituteClick }: RecipeListProps) {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    // Load all recipes on component mount
    fetch('http://localhost:5000/api/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '' }) // Empty query to get all recipes
    })
      .then(res => res.json())
      .then(data => {
        if (data.recipes) {
          setRecipes(data.recipes)
        }
        setLoading(false)
      })
      .catch(error => {
        console.error('Error loading recipes:', error)
        setLoading(false)
      })
  }, [])

  // Filter recipes based on search term
  const filteredRecipes = recipes.filter(recipe =>
    recipe.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    recipe.cuisine?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    recipe.ingredients.some(i => i.toLowerCase().includes(searchTerm.toLowerCase()))
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-white rounded-lg shadow-sm p-2">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-500"></div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-2">
      {/* Search Bar */}
      <input
        type="text"
        placeholder="Filter recipes..."
        className="w-full px-3 py-1.5 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-amber-500 mb-2 text-sm"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      {/* Recipe List */}
      <div className="space-y-2 overflow-y-auto">
        {filteredRecipes.length === 0 ? (
          <div className="text-center text-gray-500 py-4 text-sm">
            No recipes found. Try a different search term.
          </div>
        ) : (
          filteredRecipes.map((recipe, index) => (
            <div 
              key={index}
              className="border border-gray-100 rounded-lg overflow-hidden"
            >
              {/* Recipe Header - Always visible */}
              <button
                onClick={() => onRecipeClick(recipe === expandedRecipe ? null : recipe)}
                className="w-full text-left p-2 hover:bg-amber-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900 text-sm">{recipe.name}</h3>
                  <span className="text-amber-600 text-xs">
                    {recipe === expandedRecipe ? '▼' : '▶'}
                  </span>
                </div>
                <div className="flex items-center text-xs text-gray-500 space-x-3 mt-0.5">
                  {recipe.cuisine && (
                    <span>🌍 {recipe.cuisine}</span>
                  )}
                  {recipe.prep_time && (
                    <span>⏱️ {recipe.prep_time}</span>
                  )}
                  <span>📝 {recipe.ingredients.length} ingredients</span>
                </div>
              </button>

              {/* Expanded Recipe Details */}
              {recipe === expandedRecipe && (
                <div className="border-t border-gray-100 p-2">
                  {/* Recipe Info */}
                  <div className="grid grid-cols-3 gap-2 mb-3 text-sm">
                    {recipe.prep_time && (
                      <div className="text-center">
                        <span className="block text-gray-500 text-xs">Prep Time</span>
                        <span className="block font-medium">{recipe.prep_time}</span>
                      </div>
                    )}
                    {recipe.cook_time && (
                      <div className="text-center">
                        <span className="block text-gray-500 text-xs">Cook Time</span>
                        <span className="block font-medium">{recipe.cook_time}</span>
                      </div>
                    )}
                    {recipe.servings && (
                      <div className="text-center">
                        <span className="block text-gray-500 text-xs">Servings</span>
                        <span className="block font-medium">{recipe.servings}</span>
                      </div>
                    )}
                  </div>

                  {/* Ingredients */}
                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-gray-900 mb-1.5">
                      <span className="mr-1">📝</span>
                      Ingredients
                    </h4>
                    <ul className="space-y-1">
                      {recipe.ingredients.map((ingredient, idx) => (
                        <li key={idx} className="flex items-center justify-between bg-gray-50 p-1.5 rounded-lg text-sm">
                          <span>{ingredient}</span>
                          <button
                            onClick={() => onSubstituteClick(ingredient)}
                            className="text-xs text-amber-600 hover:text-amber-700 hover:bg-amber-50 px-2 py-0.5 rounded"
                          >
                            Find Substitute
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Instructions */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 mb-1.5">
                      <span className="mr-1">👩‍🍳</span>
                      Instructions
                    </h4>
                    <ol className="space-y-2">
                      {recipe.instructions.map((step, idx) => (
                        <li key={idx} className="flex">
                          <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-full bg-amber-100 text-amber-800 font-medium mr-2 text-xs">
                            {idx + 1}
                          </span>
                          <p className="text-gray-700 text-sm">{step}</p>
                        </li>
                      ))}
                    </ol>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
} 