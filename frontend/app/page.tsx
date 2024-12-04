'use client'

import { useState } from 'react'
import ChatInterface from './components/chat-interface'
import RecipeList from './components/recipe-list'
import { Recipe } from './types/recipe'

export default function RecipeAssistant() {
  const [expandedRecipe, setExpandedRecipe] = useState<Recipe | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white">
      {/* Hero Section - More compact */}
      <div className="w-full bg-amber-100 py-4 px-4 shadow-sm">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold text-amber-900 mb-1">AI Recipe Assistant</h1>
          <p className="text-amber-700 text-sm">Your personal cooking companion! Ask for recipes, ingredient substitutions, or cooking advice.</p>
          <div className="mt-2 text-xs text-amber-800">
            <p className="mb-1">Try asking:</p>
            <ul className="list-disc list-inside space-y-0.5 ml-2">
              <li>What can I cook with chicken and mushrooms?</li>
              <li>I need a substitute for heavy cream</li>
              <li>Show me some easy pasta recipes</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Main Content - Adjusted height */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="h-[calc(100vh-12rem)] flex flex-col">
            <ChatInterface onRecipeSelected={setExpandedRecipe} />
          </div>
          <div className="h-[calc(100vh-12rem)] overflow-y-auto">
            <RecipeList 
              expandedRecipe={expandedRecipe}
              onRecipeClick={setExpandedRecipe}
              onSubstituteClick={(ingredient) => {
                // This will trigger the chat interface to ask about substitution
                const chatInterface = document.querySelector('input[type="text"]') as HTMLInputElement
                if (chatInterface) {
                  chatInterface.value = `What can I substitute for ${ingredient}?`
                  chatInterface.form?.requestSubmit()
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
