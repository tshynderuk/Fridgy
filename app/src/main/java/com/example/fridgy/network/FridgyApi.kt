
package com.example.fridgy.network

import com.example.fridgy.data.RecipeRequest
import com.example.fridgy.data.RecipeResponse
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface FridgyApi {

    @GET("health")
    suspend fun checkHealth(): HealthResponse

    @POST("recipe")
    suspend fun getRecipe(
        @Body request: RecipeRequest
    ): List<RecipeResponse>
}

data class HealthResponse(
    val status: String
)
