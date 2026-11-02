
package com.example.fridgy.data

import com.example.fridgy.network.RetrofitClient

class RecipeRepository {

    private val api = RetrofitClient.api

    suspend fun getRecipe(
        ingredients: List<String>,
        maxTimeMinutes: Int
    ): List<RecipeResponse> {

        val request = RecipeRequest(
            ingredients = ingredients,
            max_time_minutes = maxTimeMinutes
        )

        return api.getRecipe(request)
    }
}
