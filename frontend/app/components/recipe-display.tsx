'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Recipe } from '../types/recipe'

interface RecipeDisplayProps {
  recipe: Recipe | null
}

export default function RecipeDisplay({ recipe }: RecipeDisplayProps) {
  if (!recipe) {
    return (
      <Card>
        <CardContent className="p-6">
          <p className="text-center text-gray-500">No recipe selected. Ask for a recipe in the chat!</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{recipe.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <h3 className="font-semibold mb-2">Ingredients:</h3>
        <ul className="list-disc pl-5 mb-4">
          {recipe.ingredients.map((ingredient, index) => (
            <li key={index} className="mb-1">
              {ingredient}
              <Button variant="ghost" size="sm" className="ml-2">
                Find Substitutes
              </Button>
            </li>
          ))}
        </ul>
        <h3 className="font-semibold mb-2">Instructions:</h3>
        <ol className="list-decimal pl-5">
          {recipe.instructions.map((step, index) => (
            <li key={index} className="mb-2">{step}</li>
          ))}
        </ol>
      </CardContent>
    </Card>
  )
}
