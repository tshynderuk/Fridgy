package com.example.fridgy

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.fridgy.data.RecipeResponse
import com.example.fridgy.data.local.HistoryEntity
import com.example.fridgy.ui.DetailsState
import com.example.fridgy.ui.HistoryViewModel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private val HDarkGreen = Color(0xFF206748)
private val HBackground = Color(0xFFF7F6EE)
private val HDarkText = Color(0xFF20392B)
private val HSecondaryText = Color(0xFF617268)
private val HLightGreen = Color(0xFFE7F4E9)

private fun formatDate(millis: Long): String =
    SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault()).format(Date(millis))

// ЕКРАН ІСТОРІЇ

@Composable
fun HistoryScreen(
    viewModel: HistoryViewModel,
    onBack: () -> Unit,
    onOpen: (Long) -> Unit
) {
    val entries by viewModel.entries.collectAsState()

    var entryToDelete by remember { mutableStateOf<HistoryEntity?>(null) }
    var showClearDialog by remember { mutableStateOf(false) }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = HBackground
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .navigationBarsPadding()
                .padding(horizontal = 22.dp, vertical = 18.dp)
        ) {

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                TextButton(onClick = onBack) {
                    Text("← Назад", color = HDarkGreen)
                }

                TextButton(
                    onClick = { showClearDialog = true },
                    enabled = !entries.isNullOrEmpty()
                ) {
                    Text("Очистити історію", color = HDarkGreen)
                }
            }

            Text(
                text = "📖 Історія рецептів",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = HDarkText
            )

            Spacer(modifier = Modifier.height(14.dp))

            val list = entries

            when {
                // Завантаження
                list == null -> {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 40.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator(color = HDarkGreen)
                    }
                }

                // Порожня історія
                list.isEmpty() -> {
                    Text(
                        text = "Історія поки порожня. Згенеруй рецепти на головному екрані, і вони з'являться тут.",
                        fontSize = 14.sp,
                        lineHeight = 21.sp,
                        color = HSecondaryText
                    )
                }

                // Список (нові зверху — порядок задає запит до бази)
                else -> {
                    LazyColumn(
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        items(list, key = { it.id }) { entry ->
                            HistoryItem(
                                entry = entry,
                                onClick = { onOpen(entry.id) },
                                onDelete = { entryToDelete = entry }
                            )
                        }
                    }
                }
            }
        }
    }

    // Підтвердження видалення одного запису
    entryToDelete?.let { entry ->
        AlertDialog(
            onDismissRequest = { entryToDelete = null },
            title = { Text("Видалити запис?") },
            text = {
                Text("Запис від ${formatDate(entry.createdAt)} буде видалено без можливості відновлення.")
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.delete(entry.id)
                        entryToDelete = null
                    }
                ) {
                    Text("Видалити")
                }
            },
            dismissButton = {
                TextButton(onClick = { entryToDelete = null }) {
                    Text("Скасувати")
                }
            }
        )
    }

    // Підтвердження очищення всієї історії
    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = { Text("Очистити всю історію?") },
            text = {
                Text("Усі збережені результати будуть видалені з пристрою без можливості відновлення.")
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.clearAll()
                        showClearDialog = false
                    }
                ) {
                    Text("Очистити")
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) {
                    Text("Скасувати")
                }
            }
        )
    }
}

@Composable
private fun HistoryItem(
    entry: HistoryEntity,
    onClick: () -> Unit,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = "🕒 ${formatDate(entry.createdAt)}",
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
                color = HSecondaryText
            )

            Text(
                text = "Продукти: ${entry.inputSummary}",
                fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = HDarkText,
                maxLines = 2
            )

            Text(
                text = "Ліміт часу: ${entry.maxTimeMinutes} хв",
                fontSize = 12.sp,
                color = HSecondaryText
            )

            Text(
                text = entry.resultSummary,
                fontSize = 13.sp,
                lineHeight = 19.sp,
                color = HDarkGreen,
                maxLines = 3
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(onClick = onDelete) {
                    Text("Видалити", color = Color(0xFFB3261E))
                }
            }
        }
    }
}

// ЕКРАН ДЕТАЛЕЙ

@Composable
fun DetailsScreen(
    viewModel: HistoryViewModel,
    id: Long,
    onBack: () -> Unit
) {
    LaunchedEffect(id) {
        viewModel.loadDetails(id)
    }

    val state by viewModel.details.collectAsState()

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = HBackground
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .navigationBarsPadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 22.dp, vertical = 18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {

            TextButton(onClick = onBack) {
                Text("← До історії", color = HDarkGreen)
            }

            when (val s = state) {

                DetailsState.Loading -> {
                    CircularProgressIndicator(color = HDarkGreen)
                }

                DetailsState.NotFound -> {
                    Text(
                        text = "Запис не знайдено або його не вдалося прочитати.",
                        fontSize = 14.sp,
                        color = HSecondaryText
                    )
                }

                is DetailsState.Loaded -> {

                    // Позначка, що це історичний результат, а не новий запуск AI
                    Surface(
                        color = HLightGreen,
                        shape = RoundedCornerShape(50.dp)
                    ) {
                        Text(
                            text = "🕒 Збережений результат від ${formatDate(s.entry.createdAt)}",
                            modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = HDarkGreen
                        )
                    }

                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(18.dp),
                        colors = CardDefaults.cardColors(containerColor = Color.White)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            Text(
                                text = "Твій запит",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = HDarkGreen
                            )
                            Text(
                                text = "Продукти: ${s.entry.inputSummary}",
                                fontSize = 14.sp,
                                color = HDarkText
                            )
                            Text(
                                text = "Ліміт часу: ${s.entry.maxTimeMinutes} хв",
                                fontSize = 14.sp,
                                color = HDarkText
                            )
                        }
                    }

                    s.recipes.forEachIndexed { index, recipe ->
                        SavedRecipeCard(recipe = recipe, index = index)
                    }

                    Text(
                        text = "Це збережений результат, а не новий запуск AI.",
                        fontSize = 11.sp,
                        color = HSecondaryText
                    )
                }
            }
        }
    }
}

@Composable
private fun SavedRecipeCard(
    recipe: RecipeResponse,
    index: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(containerColor = HLightGreen)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text(
                text = "🍽 ВАРІАНТ ${index + 1} ІЗ 3",
                fontSize = 12.sp,
                fontWeight = FontWeight.ExtraBold,
                color = HDarkGreen
            )

            Text(
                text = recipe.recipe_name,
                fontSize = 20.sp,
                lineHeight = 26.sp,
                fontWeight = FontWeight.Bold,
                color = HDarkText
            )

            Text(
                text = "⏱ ${recipe.cooking_time_minutes} хвилин",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = HDarkGreen
            )

            Text(
                text = "Інгредієнти",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = HDarkGreen
            )

            recipe.ingredients.forEach { ingredient ->
                Text(
                    text = "•  $ingredient",
                    fontSize = 13.sp,
                    color = HDarkText
                )
            }

            Text(
                text = "Приготування",
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
                color = HDarkGreen
            )

            recipe.instructions.forEachIndexed { stepIndex, instruction ->
                Text(
                    text = "${stepIndex + 1}. $instruction",
                    fontSize = 14.sp,
                    lineHeight = 21.sp,
                    color = HDarkText
                )
            }
        }
    }
}