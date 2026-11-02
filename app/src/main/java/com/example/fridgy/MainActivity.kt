
package com.example.fridgy

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.fridgy.data.RecipeResponse
import com.example.fridgy.ui.RecipeUiState
import com.example.fridgy.ui.RecipeViewModel

private val DarkGreen = Color(0xFF206748)
private val Background = Color(0xFFF7F6EE)
private val DarkText = Color(0xFF20392B)
private val SecondaryText = Color(0xFF617268)
private val LightGreen = Color(0xFFE7F4E9)

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            MaterialTheme {
                FridgyStartScreen()
            }
        }
    }
}

@Composable
fun FridgyStartScreen(
    viewModel: RecipeViewModel = viewModel()
) {

    var ingredientsText by rememberSaveable {
        mutableStateOf("")
    }

    var maxTimeText by rememberSaveable {
        mutableStateOf("30")
    }

    val uiState by viewModel.uiState.collectAsState()

    val keyboardController = LocalSoftwareKeyboardController.current

    fun generateRecipe() {
        keyboardController?.hide()

        viewModel.findRecipe(
            ingredientsText = ingredientsText
                .replace("\n", ",")
                .replace(";", ","),
            maxTimeText = maxTimeText
        )
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Background
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .imePadding()
                .navigationBarsPadding()
                .verticalScroll(rememberScrollState())
                .padding(
                    horizontal = 22.dp,
                    vertical = 18.dp
                ),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {

            Spacer(modifier = Modifier.height(8.dp))

            // LOGO

            Text(
                text = "fridgy.",
                fontSize = 38.sp,
                fontWeight = FontWeight.ExtraBold,
                color = DarkGreen
            )

            Text(
                text = "Твоя кухня тепер має власний інтелект.",
                fontSize = 14.sp,
                color = SecondaryText
            )

            Spacer(modifier = Modifier.height(12.dp))

            // MAIN TITLE

            Text(
                text = "Що смачненького\nприготуємо сьогодні?",
                fontSize = 27.sp,
                lineHeight = 34.sp,
                fontWeight = FontWeight.Bold,
                color = DarkText
            )

            Text(
                text = "Введи продукти, які маєш вдома, а Fridgy допоможе знайти ідею для страви.",
                fontSize = 14.sp,
                lineHeight = 21.sp,
                color = SecondaryText
            )

            // INGREDIENTS CARD

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(22.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White
                ),
                elevation = CardDefaults.cardElevation(
                    defaultElevation = 2.dp
                )
            ) {

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {

                    Text(
                        text = "🥗 У твоєму холодильнику",
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        color = DarkGreen
                    )

                    Text(
                        text = "Додай будь-які продукти, які маєш.",
                        fontSize = 13.sp,
                        color = SecondaryText
                    )

                    OutlinedTextField(
                        value = ingredientsText,
                        onValueChange = {
                            ingredientsText = it
                        },
                        modifier = Modifier.fillMaxWidth(),
                        label = {
                            Text("Мої продукти")
                        },
                        placeholder = {
                            Text("Наприклад: курка, рис, морква...")
                        },
                        minLines = 3,
                        maxLines = 5,
                        keyboardOptions = KeyboardOptions(
                            capitalization = KeyboardCapitalization.Sentences,
                            imeAction = ImeAction.Default
                        ),
                        shape = RoundedCornerShape(14.dp)
                    )

                    Text(
                        text = "Можна розділяти продукти комами або вводити кожен з нового рядка.",
                        fontSize = 11.sp,
                        color = Color.Gray,
                        lineHeight = 16.sp
                    )

                    TextButton(
                        onClick = {
                            ingredientsText = ""
                        },
                        enabled = ingredientsText.isNotEmpty()
                    ) {
                        Text(
                            text = "Очистити продукти",
                            color = DarkGreen
                        )
                    }

                    Spacer(modifier = Modifier.height(4.dp))

                    // COOKING TIME

                    Text(
                        text = "⏱ Скільки часу маєш?",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = DarkGreen
                    )

                    OutlinedTextField(
                        value = maxTimeText,
                        onValueChange = {
                            maxTimeText = it.filter { char ->
                                char.isDigit()
                            }.take(3)
                        },
                        modifier = Modifier.fillMaxWidth(),
                        label = {
                            Text("Час приготування (хв)")
                        },
                        placeholder = {
                            Text("30")
                        },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(
                            keyboardType = KeyboardType.Number,
                            imeAction = ImeAction.Done
                        ),
                        keyboardActions = KeyboardActions(
                            onDone = {
                                keyboardController?.hide()
                            }
                        ),
                        shape = RoundedCornerShape(14.dp)
                    )
                }
            }

            // GENERATE BUTTON

            Button(
                onClick = {
                    generateRecipe()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(58.dp),
                enabled = ingredientsText.isNotBlank() &&
                        maxTimeText.isNotBlank() &&
                        uiState !is RecipeUiState.Loading,
                colors = ButtonDefaults.buttonColors(
                    containerColor = DarkGreen,
                    disabledContainerColor = Color(0xFF9BAFA3)
                ),
                shape = RoundedCornerShape(18.dp)
            ) {

                Text(
                    text = if (uiState is RecipeUiState.Loading) {
                        "Готуємо ідеї..."
                    } else {
                        "Запропонуй 3 страви ✨"
                    },
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            // RESULT STATES

            when (val state = uiState) {

                RecipeUiState.Idle -> {

                    Text(
                        text = "Твоя наступна улюблена страва починається тут.",
                        color = SecondaryText,
                        fontSize = 13.sp
                    )
                }

                RecipeUiState.Loading -> {

                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = LightGreen
                        )
                    ) {

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(24.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {

                            CircularProgressIndicator(
                                color = DarkGreen
                            )

                            Text(
                                text = "Fridgy підбирає три страви...",
                                color = DarkGreen,
                                fontWeight = FontWeight.Bold
                            )

                            Text(
                                text = "Зачекай трохи, ми шукаємо три смачні ідеї.",
                                color = SecondaryText,
                                fontSize = 13.sp
                            )
                        }
                    }
                }

                is RecipeUiState.Success -> {

                    Text(
                        text = "✨ ТРИ ІДЕЇ ДЛЯ ТВОЄЇ КУХНІ",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.ExtraBold,
                        color = DarkGreen
                    )

                    Text(
                        text = "Обирай страву, яка тобі найбільше до смаку.",
                        fontSize = 13.sp,
                        color = SecondaryText
                    )

                    state.recipes.forEachIndexed { index, recipe ->

                        RecipeCard(
                            recipe = recipe,
                            index = index
                        )
                    }
                }

                is RecipeUiState.Error -> {

                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(20.dp),
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFFFE9E7)
                        )
                    ) {

                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(20.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp)
                        ) {

                            Text(
                                text = "⚠️ Не вдалося отримати рецепти",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFFB3261E)
                            )

                            Text(
                                text = state.message,
                                color = Color(0xFF84251F),
                                fontSize = 14.sp,
                                lineHeight = 20.sp
                            )

                            Button(
                                onClick = {
                                    generateRecipe()
                                },
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = DarkGreen
                                ),
                                shape = RoundedCornerShape(14.dp)
                            ) {

                                Text("Спробувати ще раз")
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "FRIDGY · YOUR KITCHEN, REIMAGINED",
                fontSize = 11.sp,
                color = Color(0xFF83958A)
            )

            Spacer(modifier = Modifier.height(12.dp))
        }
    }
}

// RECIPE CARD

@Composable
private fun RecipeCard(
    recipe: RecipeResponse,
    index: Int
) {

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(
            containerColor = LightGreen
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 2.dp
        )
    ) {

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(13.dp)
        ) {

            Text(
                text = "🍽 ВАРІАНТ ${index + 1} ІЗ 3",
                fontSize = 12.sp,
                fontWeight = FontWeight.ExtraBold,
                color = DarkGreen
            )

            Text(
                text = recipe.recipe_name,
                fontSize = 22.sp,
                lineHeight = 28.sp,
                fontWeight = FontWeight.Bold,
                color = DarkText
            )

            Surface(
                color = Color.White,
                shape = RoundedCornerShape(50.dp)
            ) {

                Text(
                    text = "⏱ ${recipe.cooking_time_minutes} хвилин",
                    modifier = Modifier.padding(
                        horizontal = 14.dp,
                        vertical = 8.dp
                    ),
                    color = DarkGreen,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "Інгредієнти",
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = DarkGreen
            )

            recipe.ingredients.forEach { ingredient ->

                IngredientChip(ingredient)
            }

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "Приготування",
                fontSize = 17.sp,
                fontWeight = FontWeight.Bold,
                color = DarkGreen
            )

            recipe.instructions.forEachIndexed {
                    index, instruction ->

                Text(
                    text = "${index + 1}. $instruction",
                    fontSize = 14.sp,
                    lineHeight = 21.sp,
                    color = DarkText
                )
            }

            Text(
                text = when (recipe.source.lowercase()) {
                    "gemini" -> "Згенеровано за допомогою AI"
                    "rule-based" -> "Демонстраційний алгоритм підбору"
                    else -> "Джерело: ${recipe.source}"
                },
                fontSize = 11.sp,
                color = SecondaryText
            )
        }
    }
}

@Composable
private fun IngredientChip(name: String) {

    Surface(
        color = Color.White,
        shape = RoundedCornerShape(50.dp)
    ) {

        Text(
            text = "•  $name",
            modifier = Modifier.padding(
                horizontal = 14.dp,
                vertical = 9.dp
            ),
            fontSize = 13.sp,
            color = DarkGreen
        )
    }
}
