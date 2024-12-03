'use client'

import { useState } from 'react'
import ChatInterface from './components/chat-interface'
import RecipeDisplay from './components/recipe-display'
import { Recipe } from './types/recipe'

export default function RecipeAssistant() {
  const [currentRecipe, setCurrentRecipe] = useState<Recipe | null>(null)

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-50">
      <div className="w-full md:w-1/2 p-4 overflow-y-auto">
        <ChatInterface onRecipeSelected={setCurrentRecipe} />
      </div>
      <div className="w-full md:w-1/2 p-4 overflow-y-auto">
        <RecipeDisplay recipe={currentRecipe} />
      </div>
    </div>
  )
}
