package com.moneydiary.app.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
  private const val BASE_URL = "http://10.0.2.2:8000/" // Para emulador
  // private const val BASE_URL = "https://api.moneydiary.com/" // Para producción

  val apiService: ApiService by lazy {
    Retrofit.Builder()
      .baseUrl(BASE_URL)
      .addConverterFactory(GsonConverterFactory.create())
      .build()
      .create(ApiService::class.java)
  }
}
