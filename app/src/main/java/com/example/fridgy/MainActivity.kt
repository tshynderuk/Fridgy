package com.example.fridgy

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MaterialTheme { FridgyStartScreen() } }
    }
}

@Composable
private fun FridgyStartScreen() {
    var showDemoResult by remember { mutableStateOf(false) }
    val darkGreen = Color(0xFF206748)
    val background = Color(0xFFF7F6EE)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(background)
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Spacer(modifier = Modifier.height(20.dp))
        Text("fridgy.", fontSize = 36.sp, fontWeight = FontWeight.ExtraBold, color = darkGreen)
        Text("Твоя кухня тепер має власний інтелект.", color = Color(0xFF5D7164))
        Spacer(modifier = Modifier.height(12.dp))
        Text("Що смачненького\nприготуємо сьогодні?", fontSize = 26.sp, lineHeight = 32.sp, fontWeight = FontWeight.Bold, color = Color(0xFF20392B))

        Card(colors = CardDefaults.cardColors(containerColor = Color.White), shape = RoundedCornerShape(20.dp)) {
            Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                Text("У твоєму холодильнику", color = Color(0xFF6D8073), fontSize = 14.sp)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    IngredientChip("🥚 Яйця")
                    IngredientChip("🍅 Помідори")
                }
                IngredientChip("🧀 Сир")
                Text("Приклад інгредієнтів для демонстрації першої лабораторної.", fontSize = 12.sp, color = Color.Gray)
            }
        }

        Button(
            onClick = { showDemoResult = !showDemoResult },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            colors = ButtonDefaults.buttonColors(containerColor = darkGreen),
            shape = RoundedCornerShape(18.dp)
        ) {
            Text(if (showDemoResult) "Приховати приклад" else "Що приготувати?  ✨", fontSize = 16.sp)
        }

        if (showDemoResult) {
            Card(colors = CardDefaults.cardColors(containerColor = Color(0xFFE7F4E9)), shape = RoundedCornerShape(20.dp)) {
                Column(Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Рецепт (демо)", color = darkGreen, fontWeight = FontWeight.Bold)
                    Text("Омлет із помідорами та сиром", fontWeight = FontWeight.Bold, fontSize = 19.sp)
                    Text("≈ 10–15 хв  •  1 порція")
                    Text("1. Наріж помідори.\n2. Збий яйця.\n3. Обсмаж та додай сир.")
                    Text("Це статичний приклад. Справжній AI і сервер буде додано в ЛР №2.", fontSize = 12.sp, color = Color(0xFF617268))
                }
            }
        }
        Spacer(modifier = Modifier.height(12.dp))
        Text("FRIDGY · Concept Demo · Lab 1", fontSize = 12.sp, color = Color(0xFF83958A))
    }
}

@Composable
private fun IngredientChip(name: String) {
    Surface(color = Color(0xFFE9F4E7), shape = RoundedCornerShape(50.dp)) {
        Text(name, modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp), fontSize = 13.sp, color = Color(0xFF276247))
    }
}
