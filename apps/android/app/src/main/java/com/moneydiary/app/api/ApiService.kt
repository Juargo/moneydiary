package com.moneydiary.app.api

import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Path

interface ApiService {
  @GET("transactions")
  suspend fun getTransactions(): List<Transaction>

  @POST("transactions")
  suspend fun createTransaction(@Body transaction: Transaction): Transaction

  // Añade más endpoints según necesites
}

// Modelo de ejemplo
data class Transaction(
  val id: String,
  val amount: Double,
  val description: String,
  val date: String,
  val category: String
)
