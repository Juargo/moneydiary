package com.moneydiary.app

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import com.moneydiary.app.api.RetrofitClient
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    // Ejemplo de cómo hacer una llamada API
    lifecycleScope.launch {
      try {
        val transactions = RetrofitClient.apiService.getTransactions()
        // Haz algo con los datos...
      } catch (e: Exception) {
        // Maneja errores
      }
    }
  }
}
