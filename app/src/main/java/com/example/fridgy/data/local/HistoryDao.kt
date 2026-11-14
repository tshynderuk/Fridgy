package com.example.fridgy.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {

    // Список для екрана історії: нові записи зверху, оновлюється автоматично
    @Query("SELECT * FROM history_entries ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<HistoryEntity>>

    // Один запис для екрана деталей
    @Query("SELECT * FROM history_entries WHERE id = :id LIMIT 1")
    suspend fun getById(id: Long): HistoryEntity?

    // Звичайний @Insert без REPLACE: кожен запуск AI додає НОВИЙ рядок
    @Insert
    suspend fun insert(entry: HistoryEntity): Long

    @Query("DELETE FROM history_entries WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("DELETE FROM history_entries")
    suspend fun clearAll()
}