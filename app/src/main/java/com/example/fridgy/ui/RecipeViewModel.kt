
package com.example.fridgy.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.fridgy.data.RecipeRepository
import com.example.fridgy.data.RecipeResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

sealed interface RecipeUiState {

    data object Idle : RecipeUiState

    data object Loading : RecipeUiState

    data class Success(
        val recipes: List<RecipeResponse>
    ) : RecipeUiState

    data class Error(
        val message: String
    ) : RecipeUiState
}

class RecipeViewModel : ViewModel() {

    private val repository = RecipeRepository()

    private val _uiState =
        MutableStateFlow<RecipeUiState>(RecipeUiState.Idle)

    val uiState: StateFlow<RecipeUiState> =
        _uiState.asStateFlow()

    fun findRecipe(
        ingredientsText: String,
        maxTimeText: String
    ) {
        if (_uiState.value is RecipeUiState.Loading) {
            return
        }

        val ingredients = ingredientsText
            .split(",")
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        val maxTime = maxTimeText.trim().toIntOrNull()

        // Перевірка продуктів

        if (ingredients.isEmpty()) {
            _uiState.value = RecipeUiState.Error(
                "Введіть хоча б один продукт."
            )
            return
        }

        if (ingredients.size > 30 ||
            ingredients.any { it.length > 50 }
        ) {
            _uiState.value = RecipeUiState.Error(
                "Вкажіть до 30 продуктів, не більше 50 символів кожен."
            )
            return
        }

        // Перевірка часу

        if (maxTime == null || maxTime !in 5..180) {
            _uiState.value = RecipeUiState.Error(
                "Вкажіть час приготування від 5 до 180 хвилин."
            )
            return
        }

        viewModelScope.launch {

            _uiState.value = RecipeUiState.Loading

            try {

                // Отримання трьох рецептів

                val recipes = repository.getRecipe(
                    ingredients = ingredients,
                    maxTimeMinutes = maxTime
                )

                if (recipes.size != 3) {
                    throw IllegalStateException(
                        "Сервер повернув некоректну кількість рецептів."
                    )
                }

                _uiState.value = RecipeUiState.Success(
                    recipes = recipes
                )

            } catch (e: HttpException) {

                // Обробка HTTP-помилок

                val message = when (e.code()) {

                    422 -> "Не знайдено рецептів для цих продуктів і часу."

                    429 -> "Вичерпано денний ліміт AI-запитів. Спробуйте пізніше."

                    503 -> "AI-сервіс тимчасово недоступний. Спробуйте пізніше."

                    504 -> "AI занадто довго відповідає. Спробуйте ще раз."

                    else -> "Помилка сервера. Спробуйте ще раз."
                }

                _uiState.value = RecipeUiState.Error(message)

            } catch (e: IOException) {

                // Помилка мережі

                _uiState.value = RecipeUiState.Error(
                    "Немає з'єднання із сервером. Перевірте мережу."
                )

            } catch (e: Exception) {

                // Інші помилки

                _uiState.value = RecipeUiState.Error(
                    e.message ?: "Не вдалося обробити відповідь сервера."
                )
            }
        }
    }
}
