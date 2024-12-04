'use client'

import { useState, useEffect } from 'react'
import { Recipe } from '../types/recipe'

interface RecipeBrowserProps {
  onRecipeSelected: (recipe: Recipe) => void
}

export default function RecipeBrowser({ onRecipeSelected }: RecipeBrowserProps) {
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

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

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm p-4">
      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search recipes by name, cuisine, or ingredients..."
          className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-amber-500"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Recipe List */}
      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {filteredRecipes.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              No recipes found. Try a different search term.
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredRecipes.map((recipe, index) => (
                <button
                  key={index}
                  onClick={() => onRecipeSelected(recipe)}
                  className="text-left p-4 rounded-lg border border-gray-100 hover:border-amber-200 hover:bg-amber-50 transition-colors"
                >
                  <h3 className="font-medium text-gray-900 mb-1">{recipe.name}</h3>
                  <div className="flex items-center text-sm text-gray-500 space-x-4">
                    {recipe.cuisine && (
                      <span className="inline-flex items-center">
                        🌍 {recipe.cuisine}
                      </span>
                    )}
                    {recipe.prep_time && (
                      <span className="inline-flex items-center">
                        ⏱️ {recipe.prep_time}
                      </span>
                    )}
                    <span className="inline-flex items-center">
                      📝 {recipe.ingredients.length} ingredients
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
} 