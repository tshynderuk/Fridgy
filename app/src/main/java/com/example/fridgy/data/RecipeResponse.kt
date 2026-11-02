
package com.example.fridgy.data

data class RecipeResponse(
    val recipe_name: String,
    val cooking_time_minutes: Int,
    val ingredients: List<String>,
    val instructions: List<String>,
    val source: String
)
