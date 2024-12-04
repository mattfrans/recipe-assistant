export interface Recipe {
  name: string
  cuisine?: string
  prep_time?: string
  cook_time?: string
  servings?: number
  ingredients: string[]
  instructions: string[]
}
