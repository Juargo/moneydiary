import hashlib
from typing import Optional
from decimal import Decimal
from datetime import date

def generate_transaction_hash(
    user_id: int,
    account_id: int,
    amount: Decimal,
    description: str,
    transaction_date: date,
    external_id: Optional[str] = None
) -> str:
    """
    Genera un hash único para una transacción basado en sus datos principales.
    Esto ayuda a detectar duplicados incluso si el external_id no está disponible.
    """
    # Normalizar la descripción (quitar espacios extra, convertir a minúsculas)
    normalized_description = ' '.join(description.strip().lower().split()) if description else ''
    
    # Crear string único combinando los campos principales
    hash_string = f"{user_id}|{account_id}|{amount}|{normalized_description}|{transaction_date}"
    
    # Si hay external_id, incluirlo también
    if external_id:
        hash_string += f"|{external_id}"
    
    # Generar hash SHA256
    return hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

def check_transaction_exists(
    db, 
    user_id: int,
    account_id: int,
    amount: Decimal,
    description: str,
    transaction_date: date,
    external_id: Optional[str] = None,
    content_hash: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Verifica si una transacción ya existe usando múltiples estrategias.
    Retorna (existe, razon_duplicado)
    """
    from ..models.transactions import Transaction
    
    # 1. Verificar por external_id si está disponible
    if external_id:
        existing = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.external_id == external_id
        ).first()
        
        if existing:
            return True, f"external_id duplicado: {external_id}"
    
    # 2. Verificar por content_hash si está disponible
    if content_hash:
        existing = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.content_hash == content_hash
        ).first()
        
        if existing:
            return True, f"content_hash duplicado: {content_hash[:16]}..."
    
    # 3. Verificar por combinación de campos principales (duplicados exactos)
    existing = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.account_id == account_id,
        Transaction.amount == amount,
        Transaction.transaction_date == transaction_date,
        Transaction.description == description
    ).first()
    
    if existing:
        return True, f"transacción idéntica encontrada (ID: {existing.id})"
    
    # 4. Verificar duplicados "similares" (misma fecha, cuenta y monto, descripción similar)
    # Esto es útil para detectar la misma transacción con pequeñas variaciones en la descripción
    similar_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.account_id == account_id,
        Transaction.amount == amount,
        Transaction.transaction_date == transaction_date
    ).all()
    
    if similar_transactions:
        normalized_desc = ' '.join(description.strip().lower().split()) if description else ''
        
        for similar in similar_transactions:
            existing_desc = ' '.join(similar.description.strip().lower().split()) if similar.description else ''
            
            # Calcular similitud simple (puede mejorarse con algoritmos más sofisticados)
            if normalized_desc and existing_desc:
                similarity = len(set(normalized_desc.split()) & set(existing_desc.split())) / max(len(normalized_desc.split()), len(existing_desc.split()))
                
                if similarity > 0.8:  # 80% de similitud
                    return True, f"transacción similar encontrada (ID: {similar.id}, similitud: {similarity:.0%})"
    
    return False, None