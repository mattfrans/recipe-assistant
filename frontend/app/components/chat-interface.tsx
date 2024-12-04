'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-react'
import { Recipe } from '../types/recipe'

interface ChatInterfaceProps {
  onRecipeSelected: (recipe: Recipe | null) => void
}

export default function ChatInterface({ onRecipeSelected }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { text: userMessage, isUser: true }])
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:5000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      })

      const data = await response.json()

      if (response.ok && data.recipes) {
        const recipes = data.recipes
        if (recipes.length > 0) {
          setMessages(prev => [...prev, { 
            text: `I found some recipes that might interest you! Check them out in the list on the right.`, 
            isUser: false 
          }])
          onRecipeSelected(recipes[0])
        } else {
          setMessages(prev => [...prev, { 
            text: "I couldn't find any recipes matching your request. Try different ingredients or a broader search.", 
            isUser: false 
          }])
        }
      } else {
        throw new Error(data.error || 'Failed to get response')
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, {
        text: "I'm sorry, I encountered an error. Please try again.",
        isUser: false
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm p-2">
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto mb-2 space-y-2">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg p-2 ${
                message.isUser
                  ? 'bg-amber-500 text-white'
                  : 'bg-gray-100'
              }`}
            >
              {!message.isUser && (
                <div className="w-6 h-6 rounded-full bg-amber-100 flex items-center justify-center mb-1">
                  👩‍🍳
                </div>
              )}
              <p className={`${message.isUser ? 'text-white' : 'text-gray-700'} text-sm`}>
                {message.text}
              </p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-lg p-2 bg-gray-100">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-gray-500 text-sm">Looking for recipes...</span>
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
          className="pr-20 bg-white shadow-sm border-amber-200 focus:border-amber-500 focus:ring-amber-500 text-sm"
          disabled={isLoading}
        />
        <Button
          type="submit"
          disabled={isLoading}
          className="absolute right-1 top-1 bg-amber-500 hover:bg-amber-600 h-7 text-sm px-3"
        >
          {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Send'}
        </Button>
      </form>
    </div>
  )
}
