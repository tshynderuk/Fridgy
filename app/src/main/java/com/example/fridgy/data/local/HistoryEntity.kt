package com.example.fridgy.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Один запис історії = один успішний запит до AI (одразу з трьома рецептами).
 * Зберігаємо факти: вхід, результат, час. Усе інше (формат дати, підписи) рахується під час показу.
 */
@Entity(tableName = "history_entries")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val createdAt: Long,          // час отримання результату (мілісекунди)
    val inputSummary: String,     // коротко: які продукти ввів користувач
    val maxTimeMinutes: Int,      // ліміт часу з запиту
    val resultSummary: String,    // назви трьох страв для списку
    val recipesJson: String,      // повний результат (3 рецепти) у форматі JSON
    val status: String = "ready"  // стан запису; у базу потрапляють лише готові результати
)