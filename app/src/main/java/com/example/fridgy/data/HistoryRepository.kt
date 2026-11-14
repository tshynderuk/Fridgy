package com.example.fridgy.data

import com.example.fridgy.data.local.HistoryDao
import com.example.fridgy.data.local.HistoryEntity
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.Flow

class HistoryRepository(
    private val dao: HistoryDao
) {

    private val gson = Gson()

    // Список історії: нові зверху, оновлюється автоматично
    fun observeAll(): Flow<List<HistoryEntity>> = dao.observeAll()

    suspend fun getById(id: Long): HistoryEntity? = dao.getById(id)

    // Єдине місце збереження. Викликається ЛИШЕ після валідного результату.
    // Кожен виклик додає новий запис, старі не змінюються.
    suspend fun saveSuccessful(
        ingredients: List<String>,
        maxTimeMinutes: Int,
        recipes: List<RecipeResponse>
    ) {
        val entry = HistoryEntity(
            createdAt = System.currentTimeMillis(),
            inputSummary = ingredients.joinToString(", ").take(150),
            maxTimeMinutes = maxTimeMinutes,
            resultSummary = recipes.joinToString(" • ") { it.recipe_name },
            recipesJson = gson.toJson(recipes),
            status = "ready"
        )
        dao.insert(entry)
    }

    suspend fun delete(id: Long) = dao.deleteById(id)

    suspend fun clearAll() = dao.clearAll()

    // Перетворення збереженого JSON назад у список рецептів (для екрана деталей)
    fun parseRecipes(json: String): List<RecipeResponse> {
        val type = object : TypeToken<List<RecipeResponse>>() {}.type
        return gson.fromJson(json, type) ?: emptyList()
    }
}