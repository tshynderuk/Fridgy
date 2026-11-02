package com.example.fridgy.data

data class RecipeRequest(
    val ingredients: List<String>,
    val max_time_minutes: Int
)
