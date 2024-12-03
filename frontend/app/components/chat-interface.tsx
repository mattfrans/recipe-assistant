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
        const assistantMessage: ChatMessage = { 
          role: 'assistant', 
          content: 'Here are some recipes you might like:' 
        }
        setMessages((prev) => [...prev, assistantMessage])
        
        // Pass the first recipe to the parent component
        onRecipeSelected(data.recipes[0])
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
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-4 rounded-lg ${
              message.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            {message.content}
          </div>
        ))}
        {error && (
          <div className="p-4 rounded-lg bg-red-100 text-red-700">{error}</div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask for a recipe or ingredient substitution..."
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? <Loader2 className="animate-spin" /> : 'Send'}
        </Button>
      </form>
    </div>
  )
}
