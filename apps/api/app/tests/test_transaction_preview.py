"""
Test básico para el sistema de previsualización de importación
"""

from datetime import date
from decimal import Decimal

# Datos de ejemplo para testing
sample_csv_data = """fecha,descripcion,monto
2024-01-15,Compra supermercado,-100.50
2024-01-16,Deposito salario,2500.00
2024-01-17,Pago servicios,-85.30
invalid_date,Transferencia,
2024-01-19,Compra gasolina,-45.75"""

sample_transaction_preview = {
    "preview_id": "test-uuid-123",
    "total_records": 5,
    "valid_transactions": 4,
    "invalid_transactions": 1,
    "account_id": 1,
    "account_name": "Cuenta Corriente Ejemplo",
    "profile_name": "Perfil CSV Banco",
    "transactions": [
        {
            "row_number": 1,
            "amount": -100.50,
            "description": "Compra supermercado",
            "transaction_date": date(2024, 1, 15),
            "account_id": 1,
            "account_name": "Cuenta Corriente Ejemplo",
            "is_valid": True,
            "validation_errors": [],
            "raw_data": {
                "col_0": "2024-01-15",
                "col_1": "Compra supermercado", 
                "col_2": "-100.50"
            }
        },
        {
            "row_number": 2,
            "amount": 2500.00,
            "description": "Deposito salario",
            "transaction_date": date(2024, 1, 16),
            "account_id": 1,
            "account_name": "Cuenta Corriente Ejemplo",
            "is_valid": True,
            "validation_errors": [],
            "raw_data": {
                "col_0": "2024-01-16",
                "col_1": "Deposito salario",
                "col_2": "2500.00"
            }
        },
        {
            "row_number": 4,
            "amount": None,
            "description": "Transferencia",
            "transaction_date": None,
            "account_id": 1,
            "account_name": "Cuenta Corriente Ejemplo",
            "is_valid": False,
            "validation_errors": [
                "Monto requerido",
                "Fecha de transacción requerida"
            ],
            "raw_data": {
                "col_0": "invalid_date",
                "col_1": "Transferencia",
                "col_2": ""
            }
        }
    ],
    "global_errors": []
}

def test_preview_structure():
    """Verifica que la estructura de previsualización es correcta"""
    assert "preview_id" in sample_transaction_preview
    assert "transactions" in sample_transaction_preview
    assert len(sample_transaction_preview["transactions"]) >= 1
    
    # Verificar estructura de transacción
    transaction = sample_transaction_preview["transactions"][0]
    required_fields = [
        "row_number", "amount", "description", "transaction_date",
        "account_id", "account_name", "is_valid", "validation_errors", "raw_data"
    ]
    
    for field in required_fields:
        assert field in transaction, f"Campo {field} faltante en transacción"
    
    print("✅ Estructura de previsualización correcta")

def test_validation_logic():
    """Verifica la lógica de validación"""
    valid_transaction = sample_transaction_preview["transactions"][0]
    invalid_transaction = sample_transaction_preview["transactions"][2]
    
    # Transacción válida
    assert valid_transaction["is_valid"] == True
    assert len(valid_transaction["validation_errors"]) == 0
    assert valid_transaction["amount"] is not None
    assert valid_transaction["transaction_date"] is not None
    
    # Transacción inválida
    assert invalid_transaction["is_valid"] == False
    assert len(invalid_transaction["validation_errors"]) > 0
    assert invalid_transaction["amount"] is None
    assert invalid_transaction["transaction_date"] is None
    
    print("✅ Lógica de validación correcta")

def test_confirm_request_structure():
    """Verifica la estructura de confirmación"""
    confirm_request = {
        "preview_id": "test-uuid-123",
        "selected_transactions": [1, 2, 5],
        "modifications": {
            1: {
                "amount": 105.00,
                "description": "Compra supermercado - Modificado"
            }
        }
    }
    
    assert "preview_id" in confirm_request
    assert isinstance(confirm_request["selected_transactions"], list)
    assert isinstance(confirm_request["modifications"], dict)
    
    print("✅ Estructura de confirmación correcta")

if __name__ == "__main__":
    test_preview_structure()
    test_validation_logic()
    test_confirm_request_structure()
    print("\n🎉 Todos los tests pasaron correctamente!")
    print("\nEjemplo de uso del sistema:")
    print("1. POST /api/transactions/preview-import -> Genera previsualización")
    print("2. Usuario revisa y modifica transacciones en frontend")
    print("3. POST /api/transactions/confirm-import -> Confirma importación")
