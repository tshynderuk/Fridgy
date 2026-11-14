package com.example.fridgy.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.fridgy.data.HistoryRepository
import com.example.fridgy.data.RecipeResponse
import com.example.fridgy.data.local.AppDatabase
import com.example.fridgy.data.local.HistoryEntity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

sealed interface DetailsState {

    data object Loading : DetailsState

    data object NotFound : DetailsState

    data class Loaded(
        val entry: HistoryEntity,
        val recipes: List<RecipeResponse>
    ) : DetailsState
}

class HistoryViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = HistoryRepository(
        AppDatabase.getInstance(application).historyDao()
    )

    // null = ще завантажується; порожній список = історія порожня
    val entries: StateFlow<List<HistoryEntity>?> = repository.observeAll()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = null
        )

    private val _details = MutableStateFlow<DetailsState>(DetailsState.Loading)
    val details: StateFlow<DetailsState> = _details.asStateFlow()

    fun loadDetails(id: Long) {
        viewModelScope.launch {
            _details.value = DetailsState.Loading

            val entry = repository.getById(id)

            _details.value = if (entry == null) {
                DetailsState.NotFound
            } else {
                val recipes = try {
                    repository.parseRecipes(entry.recipesJson)
                } catch (e: Exception) {
                    emptyList()
                }

                if (recipes.isEmpty()) {
                    DetailsState.NotFound
                } else {
                    DetailsState.Loaded(entry, recipes)
                }
            }
        }
    }

    fun delete(id: Long) {
        viewModelScope.launch {
            repository.delete(id)
        }
    }

    fun clearAll() {
        viewModelScope.launch {
            repository.clearAll()
        }
    }
}