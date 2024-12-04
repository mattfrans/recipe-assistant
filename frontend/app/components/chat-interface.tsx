'use client'

import { useState } from 'react'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Loader2 } from 'lucide-react'
import { Recipe } from '../types/recipe'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface ChatInterfaceProps {
  onRecipeSelected: (recipe: Recipe) => void
}

export default function ChatInterface({ onRecipeSelected }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setIsLoading(true)
    setError(null)

    const userMessage: ChatMessage = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')

    try {
      // Check if it's a substitution query
      const isSubstitutionQuery = input.toLowerCase().includes('substitute') || 
                                 input.toLowerCase().includes('replacement') ||
                                 input.toLowerCase().includes('instead of')
      
      let response
      if (isSubstitutionQuery) {
        // Extract the ingredient from the query
        const ingredient = input.replace(/.*substitute for |.*replacement for |.*instead of /i, '').trim()
        response = await fetch('http://localhost:5000/api/substitute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ingredient })
        })
      } else {
        // Assume it's a recipe search
        response = await fetch('http://localhost:5000/api/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: input })
        })
      }

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      if (isSubstitutionQuery) {
        const assistantMessage: ChatMessage = { 
          role: 'assistant', 
          content: `You can substitute with: ${data.substitution}` 
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else if (data.recipes && data.recipes.length > 0) {
        const recipe = data.recipes[0];
        // Ensure recipe has all required fields
        if (recipe && recipe.name && Array.isArray(recipe.ingredients) && Array.isArray(recipe.instructions)) {
          const assistantMessage: ChatMessage = { 
            role: 'assistant', 
            content: 'Here are some recipes you might like:' 
          }
          setMessages((prev) => [...prev, assistantMessage])
          
          // Pass the validated recipe to the parent component
          onRecipeSelected(recipe)
        } else {
          const assistantMessage: ChatMessage = { 
            role: 'assistant', 
            content: 'Sorry, there was an issue with the recipe format.' 
          }
          setMessages((prev) => [...prev, assistantMessage])
        }
      } else {
        const assistantMessage: ChatMessage = { 
          role: 'assistant', 
          content: 'Sorry, I couldn\'t find any matching recipes.' 
        }
        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (err) {
      setError('An error occurred. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Example queries */}
      <div className="bg-white rounded-lg p-4 mb-4 shadow-sm">
        <h3 className="font-medium text-gray-700 mb-2">Try asking:</h3>
        <div className="space-y-2">
          {[
            "What can I cook with chicken and mushrooms?",
            "I need a substitute for heavy cream",
            "Show me some easy pasta recipes",
          ].map((suggestion, i) => (
            <button
              key={i}
              onClick={() => {
                setInput(suggestion)
                const form = document.querySelector('form')
                form?.dispatchEvent(new Event('submit', { cancelable: true }))
              }}
              className="block w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-amber-50 rounded-md transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-amber-500 text-white'
                  : 'bg-white shadow-sm'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center mb-2">
                  👩‍🍳
                </div>
              )}
              <p className={message.role === 'user' ? 'text-white' : 'text-gray-700'}>
                {message.content}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-lg p-3 bg-white shadow-sm">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="relative">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about recipes, ingredients, or cooking tips..."
          className="pr-24 bg-white shadow-sm border-amber-200 focus:border-amber-500 focus:ring-amber-500"
        />
        <Button
          type="submit"
          disabled={isLoading}
          className="absolute right-1.5 top-1.5 bg-amber-500 hover:bg-amber-600"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Send'}
        </Button>
      </form>

      {error && (
        <div className="mt-2 text-red-500 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}
