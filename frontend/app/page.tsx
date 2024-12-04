'use client'

import { useState } from 'react'
import ChatInterface from './components/chat-interface'
import RecipeDisplay from './components/recipe-display'
import { Recipe } from './types/recipe'

export default function RecipeAssistant() {
  const [currentRecipe, setCurrentRecipe] = useState<Recipe | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white">
      {/* Hero Section */}
      <div className="w-full bg-amber-100 py-8 px-4 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold text-amber-900 mb-2">AI Recipe Assistant</h1>
          <p className="text-amber-700 text-lg">Your personal cooking companion! Ask for recipes, ingredient substitutions, or cooking advice.</p>
          <div className="mt-4 space-x-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-200 text-amber-800">
              🔍 Find Recipes
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-200 text-amber-800">
              🔄 Get Substitutions
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-amber-200 text-amber-800">
              ❓ Ask Questions
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[calc(100vh-16rem)] flex flex-col">
            <ChatInterface onRecipeSelected={setCurrentRecipe} />
          </div>
          <div className="h-[calc(100vh-16rem)] overflow-y-auto">
            <RecipeDisplay recipe={currentRecipe} />
          </div>
        </div>
      </div>
    </div>
  )
}
