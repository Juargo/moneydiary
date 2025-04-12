"""Módulo para manejar operaciones relacionadas con transacciones"""

import logging
import os
import sys
import tempfile
import math
import json
from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime

import pandas as pd
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Body, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import calendar

from app.db.models.transaction import Transaction
# from app.db.schemas.transaction import TransactionPydantic, TransactionInPydantic

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("contable")

# Define router with consistent tag
router = APIRouter(prefix="/transactions", tags=["Transactions"])

# @router.get("/", response_model=List[TransactionPydantic])
# async def get_all_transactions():
#     """Obtiene todas las transacciones de la base de datos"""
#     return await TransactionPydantic.from_queryset(Transaction.all())

# @router.get("/{transaction_id}", response_model=TransactionPydantic)
# async def get_transaction(transaction_id: int):
#     """Obtiene una transacción por su ID"""
#     transaction = await Transaction.get_or_none(id=transaction_id)
#     if not transaction:
#         raise HTTPException(status_code=404, detail="Transacción no encontrada")
#     return await TransactionPydantic.from_tortoise_orm(transaction)

# @router.post("/", response_model=TransactionPydantic)
# async def create_transaction(transaction: TransactionInPydantic):
#     """Crea una nueva transacción"""
#     transaction_obj = await Transaction.create(**transaction.dict(exclude_unset=True))
#     return await TransactionPydantic.from_tortoise_orm(transaction_obj)

def sanitize_json_data(obj: Any) -> Any:
    """
    Convierte valores no serializables en JSON (como NaN, Infinity) a valores compatibles.
    También convierte numpy.int64/float64 a tipos Python nativos para serialización.
    """
    if isinstance(obj, dict):
        return {k: sanitize_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_data(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        num = float(obj)
        if math.isnan(num):
            return None
        elif math.isinf(num):
            return None  # o podrías usar str(num) para mantener "inf"/"-inf" como cadena
        else:
            return num
    elif isinstance(obj, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    else:
        return obj

@router.post("/upload-bank-report")
async def upload_bank_report(
    file: UploadFile = File(...),
):
    """
    Recibe y procesa un archivo Excel de banco.

    - **file**: Archivo Excel del banco

    Retorna el saldo contable y los movimientos extraídos del archivo, distinguiendo entre ingresos y gastos.
    Las transacciones que coinciden con patrones a ignorar serán excluidas del procesamiento.
    """
    logger.info(f"Inicio de procesamiento de archivo bancario: {file.filename},")
    
    # Verificar que el archivo es un Excel
    if not file.filename.endswith((".xls", ".xlsx")):
        logger.warning(f"Formato de archivo incorrecto: {file.filename}")
        raise HTTPException(
            status_code=400, detail="El archivo debe ser un Excel (.xls o .xlsx)"
        )

    # Guardar el archivo temporalmente
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(file.filename)[1]
    )
    try:
        contents = await file.read()
        logger.info(f"Archivo leído correctamente: {len(contents)} bytes")
        
        with open(temp_file.name, "wb") as f:
            f.write(contents)
        logger.info(f"Archivo guardado temporalmente en: {temp_file.name}")

        # Obtener patrones a ignorar del usuario (ID=1 por defecto)
        logger.info("Obteniendo patrones a ignorar para el procesamiento")
        pattern_ignores = await get_user_pattern_ignores()
        logger.info(f"Se encontraron {len(pattern_ignores)} patrones a ignorar")

        # Procesar el archivo según el ID del banco
       
        # Pasar los patrones a ignorar a la función de extracción
        movimientos = await extraer_datos(temp_file.name, pattern_ignores)
        logger.info(f"Extracción completada: transacciones={len(movimientos)}")
        
        # Sanitizar datos para evitar errores de serialización JSON
        response_data = {
            "transactions": movimientos
        }
        
        logger.info("Sanitizando datos para respuesta JSON")
        sanitized_data = sanitize_json_data(response_data)
        logger.info(f"Procesamiento completado exitosamente. Retornando {len(sanitized_data['transactions'])} transacciones")
        return sanitized_data        
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error al procesar el archivo: {str(e)}"
        )
    finally:
        # Limpiar archivos temporales
        logger.info(f"Limpiando archivo temporal: {temp_file.name}")
        temp_file.close()
        os.unlink(temp_file.name)


async def extraer_datos(archivo, pattern_ignores=None):
    """
    Extrae las transacciones de un archivo de banco y las clasifica usando patrones de usuario.
    Filtra las transacciones que coinciden con patrones a ignorar.
    
    Args:
        archivo: Ruta al archivo a procesar
        pattern_ignores: Lista de patrones a ignorar
        
    Returns:
        Lista de transacciones categorizadas que no coinciden con patrones a ignorar
    """
    try:
        logger.info(f"Iniciando procesamiento de archivo: {archivo}")
        
        # Si no hay patrones a ignorar, inicializar como lista vacía
        if pattern_ignores is None:
            pattern_ignores = []
        
        # Log file extension
        file_extension = os.path.splitext(archivo)[1]
        logger.info(f"Extensión del archivo: \n{file_extension}")
        
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)

        logger.info(f"Procesando archivo con forma: \n{df.shape}")

        ## lista de encabezados según el banco
        fecha_headers = [
            "Fecha",
            "Fecha Transacción"
        ]
            
        descripcion_headers = [
            "Descripción",
            "Detalle"
        ]

        cargos_headers = [
            "Cargos (CLP)",
            "Cargo $",
            "Monto cargo ($)",
            "Cheques / Cargos $",
        ]

        abonos_headers = [
            "Abonos (CLP)",
            "Abono $",
            "Monto abono ($)",
            "Depósitos / Abonos $"
        ]
       
        # Buscar columnas con información de movimientos
        header_row = None
        for i, row in df.iterrows():
            row_str = row.to_string().lower()
            
            # Verificar que hay al menos una coincidencia en cada lista de encabezados
            fecha_match = any(header.lower() in row_str for header in fecha_headers)
            descripcion_match = any(header.lower() in row_str for header in descripcion_headers)
            cargos_match = any(header.lower() in row_str for header in cargos_headers)
            abonos_match = any(header.lower() in row_str for header in abonos_headers)
            
            # Contar el total de coincidencias
            total_matches = sum([
                fecha_match,
                descripcion_match,
                cargos_match,
                abonos_match
            ])
            
            # Verificar si cumple con el criterio mínimo
            if total_matches >= 4:
                logger.info(f"Encontrados posibles encabezados en fila {i}: {row_str}")
                header_row = i
                break

        logger.info(f"Fila de encabezado encontrada: {header_row}")
        if header_row is not None:
            df_movimientos = df.iloc[header_row + 1:].copy()
            df_movimientos.columns = df.iloc[header_row]
            
            # Mapear las columnas necesarias
            column_mapping = {
                "Fecha": fecha_headers,
                "Descripción": descripcion_headers,
                "Cargo": cargos_headers,
                "Abono": abonos_headers,
            }
            
            # Buscar las columnas en el dataframe
            found_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    col_str = str(col_name).lower()
                    if any(possible.lower() in col_str for possible in possible_names):
                        found_columns[target_col] = col_name
                        break
            
            logger.info(f"Columnas encontradas: {found_columns}")
            # Verificar que tenemos las columnas mínimas necesarias
            if "Fecha" in found_columns and "Descripción" in found_columns and ("Cargo" in found_columns or "Abono" in found_columns):
                # Crear DataFrame con columnas estandarizadas
                df_final = pd.DataFrame()
                df_final["Fecha"] = df_movimientos[found_columns["Fecha"]]
                df_final["Descripción"] = df_movimientos[found_columns["Descripción"]]
                
                # Inicializar columnas numéricas
                df_final["Cargo"] = 0
                df_final["Abono"] = 0
                
                # Función para convertir strings con formato de moneda chilena a números
                def parse_chilean_amount(value):
                    if pd.isna(value):
                        return 0
                    
                    # Si ya es un número, devolverlo directamente
                    if isinstance(value, (int, float)):
                        return value
                    
                    # Convertir a string si no lo es
                    value_str = str(value)
                    
                    # Reemplazar puntos (separadores de miles) y comas (separadores decimales)
                    # En Chile: 1.234,56 = 1234.56 en formato inglés
                    cleaned_value = value_str.replace('.', '').replace(',', '.')
                    
                    try:
                        return float(cleaned_value)
                    except ValueError:
                        # Si hay error, intentar extraer solo dígitos y puntos/comas
                        import re
                        numeric_chars = re.sub(r'[^\d,.]', '', value_str)
                        if numeric_chars:
                            numeric_chars = numeric_chars.replace('.', '').replace(',', '.')
                            try:
                                return float(numeric_chars)
                            except ValueError:
                                return 0
                        return 0
                
                # Procesar columnas de montos con la nueva función
                if "Cargo" in found_columns:
                    df_final["Cargo"] = df_movimientos[found_columns["Cargo"]].apply(parse_chilean_amount)
                
                if "Abono" in found_columns:
                    df_final["Abono"] = df_movimientos[found_columns["Abono"]].apply(parse_chilean_amount)
                
                # Si hay una columna de monto que puede contener valores positivos y negativos
                if "Monto" in found_columns:
                    montos = df_movimientos[found_columns["Monto"]].apply(parse_chilean_amount)
                    df_final["Cargo"] += montos.apply(lambda x: abs(x) if x < 0 else 0)
                    df_final["Abono"] += montos.apply(lambda x: x if x > 0 else 0)
                
                # Determinar el tipo de transacción
                df_final["Tipo"] = "Gasto"
                df_final.loc[df_final["Abono"] > 0, "Tipo"] = "Ingreso"
                
                # Calcular el monto final (positivo para ambos tipos)
                df_final["Monto"] = df_final["Cargo"] + df_final["Abono"]
                
                # Registrar algunos montos para verificación
                logger.debug(f"Ejemplos de montos procesados: {df_final['Monto'].head().tolist()}")
                
                # Filtrar filas con valores nulos y montos cero
                df_final = df_final.dropna(subset=["Fecha", "Monto"])
                df_final = df_final[df_final["Monto"] != 0]
                
                # Convertir a lista de diccionarios para procesar patrones
                movimientos = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                
                # Filtrar transacciones que coinciden con patrones a ignorar
                if pattern_ignores:
                    movimientos_filtrados = []
                    count_ignored = 0
                    
                    for movimiento in movimientos:
                        descripcion = movimiento["Descripción"].lower() if "Descripción" in movimiento and movimiento["Descripción"] else ""
                        
                        # Verificar si la descripción coincide con algún patrón a ignorar
                        should_ignore = False
                        for pattern in pattern_ignores:
                            pattern_exp = pattern["match_text"]
                            
                            # Convertir el patrón con comodines a una expresión regular
                            if "*" in pattern_exp:
                                pattern_regex = pattern_exp.replace("*", ".*")
                                import re
                                if re.search(pattern_regex, descripcion, re.IGNORECASE):
                                    logger.debug(f"Ignorando transacción que coincide con patrón '{pattern_exp}': {descripcion}")
                                    should_ignore = True
                                    count_ignored += 1
                                    break
                            # Si no tiene comodines, hacer comparación directa
                            elif pattern_exp.lower() in descripcion:
                                logger.debug(f"Ignorando transacción que coincide con patrón '{pattern_exp}': {descripcion}")
                                should_ignore = True
                                count_ignored += 1
                                break
                        
                        # Si no debe ignorarse, añadir a la lista filtrada
                        if not should_ignore:
                            movimientos_filtrados.append(movimiento)
                    
                    logger.info(f"Se ignoraron {count_ignored} transacciones según patrones definidos")
                    movimientos = movimientos_filtrados
                
                # Obtener patrones del usuario para clasificar las transacciones
                user_patterns = await get_user_patterns()
                
                # Aplicar categorización a las transacciones
                movimientos_categorizados = await categorizar_transacciones(movimientos, user_patterns)
                
                logger.info(f"Extracción y categorización completada: {len(movimientos_categorizados)} movimientos")
                if len(movimientos_categorizados) > 0:
                    logger.debug(f"Muestra de datos categorizados: {movimientos_categorizados[0]}")
                
                return movimientos_categorizados
            else:
                logger.warning("No se encontraron las columnas necesarias para extraer transacciones")
                return []
        else:
            logger.warning("No se pudo identificar la fila de encabezados en el archivo")
            return []
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {str(e)}", exc_info=True)
        return []

async def categorizar_transacciones(transacciones, patrones_usuario):
    """
    Categoriza las transacciones según los patrones definidos por el usuario.
    
    Args:
        transacciones: Lista de diccionarios con las transacciones
        patrones_usuario: Lista de categorías con sus subcategorías y patrones
        
    Returns:
        Lista de transacciones con categorías y subcategorías asignadas
    """
    import re
    import unicodedata
    
    try:
        # logger.info(f"Iniciando categorización de {len(transacciones)} transacciones")
        
        # Preparar la estructura para transacciones categorizadas
        transacciones_categorizadas = []
        
        # Contador para estadísticas
        contador_categorizadas = 0
        
        # Función para normalizar texto eliminando espacios y acentos
        def normalize_text(text):
            return ''.join(
                c for c in unicodedata.normalize('NFD', text)
                if unicodedata.category(c) != 'Mn'
            ).replace(" ", "").lower()
        
        # Procesar cada transacción
        for transaccion in transacciones:
            descripcion = transaccion["Descripción"].lower() if transaccion.get("Descripción") else ""
            logger.debug(f"Procesando transacción: {transaccion}")
            transaccion_categorizada = transaccion.copy()
            
            # Valores predeterminados
            transaccion_categorizada["category_id"] = None
            transaccion_categorizada["category_name"] = "Sin categoría"
            transaccion_categorizada["subcategory_id"] = None
            transaccion_categorizada["subcategory_name"] = "Sin subcategoría"
            transaccion_categorizada["category_color"] = "#CCCCCC"  # Color gris por defecto
            transaccion_categorizada["pattern_id"] = None  # Añadir pattern_id con valor predeterminado
            
            # Buscar coincidencias con patrones
            for categoria in patrones_usuario:
                # logger.debug(f"Evaluando categoría: {categoria['category_name']} (ID: {categoria['category_id']})")
                for subcategoria in categoria["subcategories"]:
                    # logger.debug(f"Evaluando subcategoría: {subcategoria['subcategory_name']} (ID: {subcategoria['subcategory_id']})")
                    for patron in subcategoria["patterns"]:
                        pattern_text = patron["pattern_text"]
                        is_regex = patron["is_regex"]
                        # logger.debug(f"Evaluando patrón: {pattern_text} (Regex: {is_regex})")
                        
                        # Eliminar espacios y acentos para comparación
                        normalized_pattern = normalize_text(pattern_text)
                        normalized_description = normalize_text(descripcion)
                        
                        # Verificar si hay coincidencia (solo búsqueda de texto simple)
                        logger.debug(f"##### Buscando coincidencia con patrón: {normalized_pattern} ---> {normalized_description}")
                        coincide = normalized_pattern in normalized_description
                        if coincide:
                            logger.debug(f"Coincidencia encontrada con patrón simple: {pattern_text}")
                            # Asignar categoría y subcategoría
                            transaccion_categorizada["category_id"] = categoria["category_id"]
                            transaccion_categorizada["category_name"] = categoria["category_name"]
                            transaccion_categorizada["subcategory_id"] = subcategoria["subcategory_id"]
                            transaccion_categorizada["subcategory_name"] = subcategoria["subcategory_name"]
                            transaccion_categorizada["category_color"] = categoria["category_color"]
                            transaccion_categorizada["pattern_id"] = patron["pattern_id"]  # Añadir el ID del patrón que coincidió
                            contador_categorizadas += 1
                            
                            logger.debug(f"Transacción categorizada: {transaccion_categorizada}")
                            # Terminar búsqueda al encontrar coincidencia
                            break
                    
                    # Si ya se encontró categoría, salir del ciclo de subcategorías
                    if transaccion_categorizada["category_id"] is not None:
                        break
                        
                # Si ya se encontró categoría, salir del ciclo de categorías
                if transaccion_categorizada["category_id"] is not None:
                    break
            
            # Agregar transacción categorizada al resultado
            transacciones_categorizadas.append(transaccion_categorizada)
        
        # Estadísticas de categorización
        porcentaje = (contador_categorizadas / len(transacciones)) * 100 if transacciones else 0
        logger.info(f"Categorización completada: {contador_categorizadas} de {len(transacciones)} ({porcentaje:.2f}%) transacciones categorizadas")
        
        return transacciones_categorizadas
    
    except Exception as e:
        logger.error(f"Error al categorizar transacciones: {str(e)}", exc_info=True)
        # Devolver transacciones sin categorizar en caso de error
        return []

async def get_user_patterns(user_id: int = 1):
    """
    Obtiene todos los patrones asociados a un usuario específico.
    
    La consulta recorre la estructura:
    budget (user_id) -> categories -> subcategories -> patterns
    
    Args:
        user_id: ID del usuario, default=1
    
    Returns:
        Lista de categorías con sus subcategorías y patrones asociados
    """
    try:
        logger.info(f"Obteniendo patrones para el usuario ID: {user_id}")
        
        # Consulta SQL que conecta budget -> categories -> subcategories -> patterns
        # Removed the non-existent c.color field
        query = """
        SELECT 
            p.id AS pattern_id,
            p.match_text AS pattern_text,
            sc.id AS subcategory_id,
            sc.name AS subcategory_name,
            c.id AS category_id,
            c.name AS category_name,
            b.id AS budget_id,
            b.name AS budget_name
        FROM 
            budget b
        JOIN 
            category c ON c.budget_id = b.id
        JOIN 
            subcategory sc ON sc.category_id = c.id
        JOIN 
            pattern p ON p.subcategory_id = sc.id
        WHERE 
            b.user_id = %s
        ORDER BY 
            c.name, sc.name
        """
        
        # Parámetros para la consulta
        params = [user_id]
        
        # Ejecutar la consulta
        from tortoise import connections
        conn = connections.get("default")
        results = await conn.execute_query(query, params)
        
        # Organizar resultados en una estructura jerárquica
        categories = {}
        
        # The results structure is different than expected
        # results[0] is actually a list of dictionaries, not a list of tuples
        logger.info(f"Resultados de la consulta: {results}")
        
        # Process the results, which are already in dictionary format
        for row in results[1]:  # Use results[1] which contains the actual rows as dictionaries
            # Access fields by name instead of unpacking
            pattern_id = row['pattern_id']
            pattern_text = row['pattern_text']
            subcategory_id = row['subcategory_id']
            subcategory_name = row['subcategory_name']
            category_id = row['category_id']
            category_name = row['category_name']
            budget_id = row['budget_id']
            budget_name = row['budget_name']
            
            # Crear categoría si no existe
            if category_id not in categories:
                categories[category_id] = {
                    "category_id": category_id,
                    "category_name": category_name,
                    "category_color": "#CCCCCC",  # Default color since the field doesn't exist
                    "budget_id": budget_id,
                    "budget_name": budget_name,
                    "subcategories": {}
                }
            
            # Crear subcategoría si no existe
            if subcategory_id not in categories[category_id]["subcategories"]:
                categories[category_id]["subcategories"][subcategory_id] = {
                    "subcategory_id": subcategory_id,
                    "subcategory_name": subcategory_name,
                    "patterns": []
                }
            
            # Añadir patrón a la subcategoría
            categories[category_id]["subcategories"][subcategory_id]["patterns"].append({
                "pattern_id": pattern_id,
                "pattern_text": pattern_text,
                "is_regex": False  # Set a default value for is_regex since it's not in the query
            })
        
        # Convertir el diccionario a una lista para el resultado final
        result = []
        for category in categories.values():
            # Convertir subcategorías de diccionario a lista
            subcategories_list = []
            for subcategory in category["subcategories"].values():
                subcategories_list.append(subcategory)
            
            category["subcategories"] = subcategories_list
            result.append(category)
        
        logger.info(f"Se encontraron {len(result)} categorías con patrones para el usuario {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error al obtener patrones del usuario {user_id}: {str(e)}", exc_info=True)
        return []

async def get_user_pattern_ignores(user_id: int = 1):
    """
    Obtiene todos los patrones a ignorar asociados a un usuario específico.
    
    Args:
        user_id: ID del usuario, default=1
    
    Returns:
        Lista de patrones a ignorar con sus detalles
    """
    try:
        logger.info(f"Obteniendo patrones a ignorar para el usuario ID: {user_id}")
        
        from app.db.models.pattern_ignore import PatternIgnore
        
        # Obtener todos los patrones a ignorar del usuario
        pattern_ignores = await PatternIgnore.filter(user_id=user_id).all()
        
        # Convertir a lista de diccionarios
        result = []
        for pattern in pattern_ignores:
            result.append({
                "id": pattern.id,
                "match_text": pattern.match_text,
                "description": pattern.description,
                "created_at": pattern.created_at.isoformat() if pattern.created_at else None,
                "updated_at": pattern.updated_at.isoformat() if pattern.updated_at else None
            })
        
        logger.info(f"Se encontraron {len(result)} patrones a ignorar para el usuario {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error al obtener patrones a ignorar del usuario {user_id}: {str(e)}", exc_info=True)
        return []

# Modelo para recibir transacciones en masa
class TransactionInput(BaseModel):
    fecha: Union[str, date, datetime]
    descripcion: str
    monto: float
    categoria: Optional[str] = "Sin clasificar"
    banco_id: Optional[int] = None
    tipo: Optional[str] = None  # Agregamos el campo tipo como opcional

# Modelo para bulk-transactions
class BulkTransactionInput(BaseModel):
    transaction_date: Union[str, date, datetime]
    description: str
    amount: float
    type: str  # "Ingreso" o "Gasto"
    user_bank_id: int
    subcategory_id: int
    pattern_id: Optional[int] = None  # Opcional: ID del patrón que coincide con esta transacción

@router.post("/bulk-transactions")
async def create_bulk_transactions(
    transactions: List[BulkTransactionInput] = Body(...),
    year_month: Optional[str] = Query(None, description="Filtrar por año y mes (formato: YYYY-MM). Por defecto, el mes actual.")
):
    """
    Registra múltiples transacciones en la base de datos verificando duplicados.
    
    Args:
        transactions: Lista de transacciones a registrar
        year_month: Filtrar por año y mes (formato: YYYY-MM, ej: 2023-11)
        
    Returns:
        Resumen de las transacciones procesadas, insertadas y duplicadas
    """
    try:
        logger.info(f"Recibidas {len(transactions)} transacciones para inserción masiva")
        
        # Procesar el parámetro de año-mes
        if year_month:
            try:
                year, month = map(int, year_month.split('-'))
                # Validar el formato
                if not (1 <= month <= 12 and 1000 <= year <= 9999):
                    raise ValueError("Formato de mes inválido")
            except ValueError as e:
                logger.warning(f"Formato de año-mes inválido: {year_month}. {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de año-mes inválido: {year_month}. Use el formato YYYY-MM (ej: 2023-11)"
                )
        else:
            # Usar el mes actual por defecto
            current_date = datetime.now()
            year, month = current_date.year, current_date.month
        
        logger.info(f"Procesando transacciones para el período: {year}-{month:02d}")
        
        # Contadores para estadísticas
        total_processed = len(transactions)
        inserted_count = 0
        duplicates_count = 0
        duplicate_records = []
        inserted_records = []
        
        # Obtener conexión a la BD
        from tortoise import connections
        conn = connections.get("default")
        
        # Procesar cada transacción
        for transaction_data in transactions:
            # Convertir fecha si es necesario
            if isinstance(transaction_data.transaction_date, str):
                try:
                    transaction_date = datetime.fromisoformat(transaction_data.transaction_date.replace('Z', '+00:00'))
                except ValueError:
                    # Intentar otros formatos comunes
                    try:
                        transaction_date = datetime.strptime(transaction_data.transaction_date, "%Y-%m-%d")
                    except ValueError:
                        logger.warning(f"Formato de fecha inválido: {transaction_data.transaction_date}")
                        continue
            else:
                transaction_date = transaction_data.transaction_date
                
            # Verificar si la fecha de la transacción está en el mes solicitado
            # Solo si se especificó un mes
            if year_month and isinstance(transaction_date, datetime):
                if transaction_date.year != year or transaction_date.month != month:
                    logger.debug(f"Transacción fuera del período solicitado: {transaction_date}")
                    continue
            
            # Verificar si la transacción ya existe usando la vista view_transaction_hierarchy
            # Revisando la estructura de la vista, no incluye user_bank_id directamente
            # Actualizamos para usar sólo los campos disponibles en la vista
            duplicate_check_query = """
            SELECT t.* FROM view_transaction_hierarchy v
            JOIN transaction t ON t.id = v.transaction_id
            WHERE v.transaction_date = %s
            AND v.transaction_description = %s
            AND v.amount = %s
            AND t.user_bank_id = %s
            AND v.subcategory_id = %s
            """
            
            duplicate_params = [
                transaction_date,
                transaction_data.description,
                transaction_data.amount,
                transaction_data.user_bank_id,
                transaction_data.subcategory_id
            ]
            
            # Ejecutar consulta de duplicados
            duplicate_results = await conn.execute_query(duplicate_check_query, duplicate_params)
            
            if duplicate_results[1]:
                # La transacción ya existe
                duplicate_record = duplicate_results[1][0]
                logger.debug(f"Transacción duplicada encontrada: {transaction_data.description} {transaction_data.amount}")
                duplicates_count += 1
                
                # Crear un registro enriquecido con datos de la jerarquía
                duplicate_info = {
                    "transaction_id": duplicate_record.get("transaction_id"),
                    "transaction_date": transaction_date.isoformat() if isinstance(transaction_date, datetime) else transaction_date,
                    "description": transaction_data.description,
                    "amount": float(transaction_data.amount),
                    "type": transaction_data.type,
                    "user_bank_id": transaction_data.user_bank_id,
                    "subcategory_id": transaction_data.subcategory_id,
                    "bank_name": duplicate_record.get("bank_name"),
                    "category_name": duplicate_record.get("category_name"),
                    "subcategory_name": duplicate_record.get("subcategory_name"),
                    "budget_name": duplicate_record.get("budget_name")
                }
                duplicate_records.append(duplicate_info)
            else:
                # La transacción no existe, insertarla
                try:
                    # Crear diccionario con los datos de la transacción
                    transaction_data_dict = {
                        "transaction_date": transaction_date,
                        "description": transaction_data.description,
                        "amount": transaction_data.amount,
                        "type": transaction_data.type,
                        "user_bank_id": transaction_data.user_bank_id,
                        "subcategory_id": transaction_data.subcategory_id
                    }
                    
                    # Si hay un pattern_id, incluirlo en la creación
                    if transaction_data.pattern_id is not None:
                        transaction_data_dict["pattern_id"] = transaction_data.pattern_id
                    
                    # Crear la transacción con los datos proporcionados
                    new_transaction = await Transaction.create(**transaction_data_dict)
                    inserted_count += 1
                    
                    # Obtener información completa de la transacción desde la vista
                    transaction_query = """
                    SELECT * FROM view_transaction_hierarchy
                    WHERE transaction_id = %s
                    """
                    transaction_result = await conn.execute_query(transaction_query, [new_transaction.id])
                    
                    # Preparar el registro enriquecido para la respuesta
                    transaction_info = {
                        "id": new_transaction.id,
                        "transaction_date": transaction_date.isoformat() if isinstance(transaction_date, datetime) else transaction_date,
                        "description": transaction_data.description,
                        "amount": float(transaction_data.amount),
                        "type": transaction_data.type,
                        "user_bank_id": transaction_data.user_bank_id,
                        "subcategory_id": transaction_data.subcategory_id
                    }
                    
                    # Añadir información adicional de la jerarquía si está disponible
                    if transaction_result[1]:
                        hierarchy_data = transaction_result[1][0]
                        transaction_info.update({
                            "bank_name": hierarchy_data.get("bank_name"),
                            "category_name": hierarchy_data.get("category_name"),
                            "subcategory_name": hierarchy_data.get("subcategory_name"),
                            "budget_name": hierarchy_data.get("budget_name")
                        })
                    
                    inserted_records.append(transaction_info)
                    logger.debug(f"Transacción insertada correctamente: ID={new_transaction.id}")
                except Exception as e:
                    logger.error(f"Error al insertar transacción {transaction_data.description}: {str(e)}", exc_info=True)
        
        # Preparar respuesta
        response = {
            "total_processed": total_processed,
            "inserted_count": inserted_count,
            "duplicates_count": duplicates_count,
            "inserted_records": inserted_records,
            "duplicate_records": duplicate_records,
            "period": f"{year}-{month:02d}"
        }
        
        logger.info(f"Procesamiento masivo completado para {year}-{month:02d}. Insertadas: {inserted_count}, Duplicadas: {duplicates_count}")
        return response
    
    except Exception as e:
        logger.error(f"Error en la inserción masiva de transacciones: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar las transacciones: {str(e)}"
        )

@router.get("/budget-summary")
async def get_budget_summary(
    user_id: int = Query(1, description="ID del usuario"),
    year_month: Optional[str] = Query(None, description="Filtrar por año y mes (formato: YYYY-MM). Por defecto, el mes actual.")
):
    """
    Obtiene un resumen jerárquico de presupuestos con totales de transacciones.
    
    Args:
        user_id: ID del usuario (por defecto: 1)
        year_month: Filtrar por año y mes (formato: YYYY-MM, ej: 2023-11)
        
    Returns:
        Estructura jerárquica con presupuestos, categorías, subcategorías y patrones,
        incluyendo los montos totales de transacciones en cada nivel.
        También incluye la transacción de sueldo (Zweicom) del mes anterior.
    """
    try:
        # Procesar el parámetro de año-mes
        if year_month:
            try:
                year, month = map(int, year_month.split('-'))
                # Validar el formato
                if not (1 <= month <= 12 and 1000 <= year <= 9999):
                    raise ValueError("Formato de mes inválido")
            except ValueError as e:
                logger.warning(f"Formato de año-mes inválido: {year_month}. {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de año-mes inválido: {year_month}. Use el formato YYYY-MM (ej: 2023-11)"
                )
        else:
            # Usar el mes actual por defecto
            current_date = datetime.now()
            year, month = current_date.year, current_date.month
        
        logger.info(f"Generando resumen de presupuesto para el usuario ID: {user_id}, período: {year}-{month:02d}")
        
        # Calcular el mes anterior para buscar el sueldo
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        
        logger.info(f"Buscando sueldo del mes anterior: {prev_year}-{prev_month:02d}")
        
        # Obtener conexión a la BD
        from tortoise import connections
        conn = connections.get("default")
        
        # Consulta para obtener el sueldo del mes anterior (tipo Ingreso, subcategoría Zweicom)
        # Corregir la consulta eliminando el campo user_bank_id que no existe en la vista
        salary_query = """
        SELECT 
            t.id AS transaction_id,
            t.transaction_date,
            t.description,
            t.amount,
            t.type,
            v.subcategory_name,
            v.category_name,
            v.budget_name,
            t.user_bank_id,
            ub.description AS bank_name
        FROM 
            transaction t
        JOIN
            view_transaction_hierarchy v ON t.id = v.transaction_id
        LEFT JOIN
            user_bank ub ON t.user_bank_id = ub.id
        WHERE 
            v.user_id = %s
            AND EXTRACT(YEAR FROM t.transaction_date) = %s
            AND EXTRACT(MONTH FROM t.transaction_date) = %s
            AND t.type = 'Ingreso'
            AND v.subcategory_name = 'Zweicom'
        ORDER BY 
            t.transaction_date DESC
        LIMIT 1
        """
        
        # Ejecutar consulta para obtener el sueldo del mes anterior
        salary_params = [user_id, prev_year, prev_month]
        salary_result = await conn.execute_query(salary_query, salary_params)
        
        # Variable para almacenar la transacción del sueldo del mes anterior
        previous_month_salary = None
        
        if (salary_result[1]):
            previous_month_salary = {
                'id': salary_result[1][0]['transaction_id'],
                'transaction_date': salary_result[1][0]['transaction_date'].isoformat() if isinstance(salary_result[1][0]['transaction_date'], datetime) else salary_result[1][0]['transaction_date'],
                'description': salary_result[1][0]['description'],
                'amount': float(salary_result[1][0]['amount']),
                'type': salary_result[1][0]['type'],
                'subcategory_name': salary_result[1][0]['subcategory_name'],
                'category_name': salary_result[1][0]['category_name'],
                'budget_name': salary_result[1][0]['budget_name'],
                'user_bank_id': salary_result[1][0]['user_bank_id'],
                'bank_name': salary_result[1][0]['bank_name']
            }
            logger.info(f"Sueldo del mes anterior encontrado: {previous_month_salary['description']}, monto: {previous_month_salary['amount']}")
        else:
            logger.warning(f"No se encontró sueldo del mes anterior para el período {prev_year}-{prev_month:02d}")

        # 1. Obtener la estructura jerárquica completa usando la vista view_transaction_hierarchy
        # Asegurar que todas las columnas están correctamente cualificadas para evitar ambigüedad
        hierarchy_query = """
        SELECT 
            v.budget_id,
            v.budget_name,
            v.category_id,
            v.category_name,
            v.subcategory_id,
            v.subcategory_name,
            v.subcategory_budget_amount,
            v.category_budget_amount,
            v.budget_amount,
            v.pattern_id,
            v.pattern_text,
            v.transaction_id,
            v.transaction_description AS description,
            v.amount,
            t.type AS transaction_type
        FROM 
            view_transaction_hierarchy v
        JOIN
            transaction t ON t.id = v.transaction_id
        WHERE 
            v.user_id = %s
            AND EXTRACT(YEAR FROM v.transaction_date) = %s
            AND EXTRACT(MONTH FROM v.transaction_date) = %s
        ORDER BY 
            v.budget_id, v.category_id, v.subcategory_id, v.pattern_id
        """
        
        # Ejecutar consulta unificada
        params = [user_id, year, month]
        logger.debug(f"Ejecutando consulta con parámetros: {params}")
        query_results = await conn.execute_query(hierarchy_query, params)
        
        logger.debug(f"Encontrados {len(query_results[1])} registros en la vista de jerarquía de transacciones")
        
        # 2. Crear estructuras para almacenar los datos
        budgets = {}
        transaction_processed = set()  # Conjunto para evitar procesar transacciones duplicadas
        
        # Variable para almacenar la transacción de sueldo del mes actual (a excluir)
        current_month_salary = None
        
        # 3. Procesar resultados y organizarlos en la estructura jerárquica
        for row in query_results[1]:
            # Extraer datos del registro
            budget_id = row.get('budget_id')
            budget_name = row.get('budget_name')
            category_id = row.get('category_id')
            category_name = row.get('category_name')
            subcategory_id = row.get('subcategory_id')
            subcategory_name = row.get('subcategory_name')
            subcategory_budget_amount = float(row.get('subcategory_budget_amount', 0))
            category_budget_amount = float(row.get('category_budget_amount', 0))
            budget_amount = float(row.get('budget_amount', 0))
            pattern_id = row.get('pattern_id')
            pattern_text = row.get('pattern_text')
            transaction_id = row.get('transaction_id')
            description = row.get('description')
            amount = float(row.get('amount', 0))
            transaction_type = row.get('transaction_type')
            
            # Identificar si esta transacción es el sueldo del mes actual
            if (transaction_type == 'Ingreso' and subcategory_name == 'Zweicom'):
                current_month_salary = {
                    'id': transaction_id,
                    'description': description,
                    'amount': amount,
                    'type': transaction_type,
                    'subcategory_name': subcategory_name
                }
                logger.info(f"Sueldo del mes actual encontrado (será excluido): {description}, monto: {amount}")
                continue  # Saltar la transacción del sueldo del mes actual
            
            # Convertir a valor negativo si es un gasto
            if transaction_type == 'Gasto':
                amount = -abs(amount)
            
            # Evitar registros sin información de presupuesto
            if not budget_id or not category_id or not subcategory_id:
                continue
                
            # Inicializar presupuesto si no existe
            if budget_id not in budgets:
                budgets[budget_id] = {
                    'id': budget_id,
                    'name': budget_name,
                    'total': 0.0,
                    'budget_amount': budget_amount,  # Usar el valor directamente de la vista
                    'categories': {}
                }
            
            # Inicializar categoría si no existe
            if category_id not in budgets[budget_id]['categories']:
                budgets[budget_id]['categories'][category_id] = {
                    'id': category_id,
                    'name': category_name,
                    'total': 0.0,
                    'category_budget_amount': category_budget_amount,  # Usar el valor directamente de la vista
                    'subcategories': {}
                }
                
            # Inicializar subcategoría si no existe
            if subcategory_id not in budgets[budget_id]['categories'][category_id]['subcategories']:
                budgets[budget_id]['categories'][category_id]['subcategories'][subcategory_id] = {
                    'id': subcategory_id,
                    'name': subcategory_name,
                    'total': 0.0,
                    'subcategory_budget_amount': subcategory_budget_amount,  # Usar el valor directamente de la vista
                    'patterns': {}
                }
            
            # Definir patrón: si no hay pattern_id, usar "sin_patron_{subcategory_id}"
            current_pattern_id = pattern_id if pattern_id else f"sin_patron_{subcategory_id}"
            current_pattern_text = pattern_text if pattern_text else "Sin patrón específico"
            
            # Inicializar patrón si no existe
            if current_pattern_id not in budgets[budget_id]['categories'][category_id]['subcategories'][subcategory_id]['patterns']:
                budgets[budget_id]['categories'][category_id]['subcategories'][subcategory_id]['patterns'][current_pattern_id] = {
                    'id': current_pattern_id,
                    'text': current_pattern_text,
                    'total': 0.0,
                    'transactions': []
                }
            
            # Procesar transacción si existe y no ha sido procesada antes
            if transaction_id and transaction_id not in transaction_processed:
                transaction_processed.add(transaction_id)
                
                # Crear objeto de transacción con el monto ajustado para gastos
                transaction_data = {
                    'id': transaction_id,
                    'amount': amount,  # Ya ajustado (negativo para gastos)
                    'description': description,
                    'type': transaction_type
                }
                
                # Agregar transacción al patrón
                pattern = budgets[budget_id]['categories'][category_id]['subcategories'][subcategory_id]['patterns'][current_pattern_id]
                pattern['transactions'].append(transaction_data)
                pattern['total'] += amount
                
                # Actualizar totales en la jerarquía
                budgets[budget_id]['categories'][category_id]['subcategories'][subcategory_id]['total'] += amount
                budgets[budget_id]['categories'][category_id]['total'] += amount
                budgets[budget_id]['total'] += amount
        
        # Agregar el sueldo del mes anterior a la estructura de presupuestos
        if previous_month_salary:
            # Obtener los valores reales de la transacción del salario para armar la estructura
            salary_budget_name = previous_month_salary['budget_name']
            salary_category_name = previous_month_salary['category_name']
            salary_subcategory_name = previous_month_salary['subcategory_name']
            
            # Buscar el presupuesto por nombre, o usar el ID real si está disponible
            salary_budget_id = None
            
            # Intentar usar el ID real del presupuesto asociado al salario (si existe en la vista)
            salary_query = """
            SELECT 
                sc.id AS subcategory_id,
                c.id AS category_id,
                b.id AS budget_id
            FROM 
                subcategory sc
            JOIN 
                category c ON sc.category_id = c.id
            JOIN 
                budget b ON c.budget_id = b.id
            WHERE 
                sc.name = %s
                AND c.name = %s
                AND b.name = %s
                AND b.user_id = %s
            LIMIT 1
            """
            
            salary_structure_params = [
                salary_subcategory_name,
                salary_category_name,
                salary_budget_name,
                user_id
            ]
            
            try:
                salary_structure_result = await conn.execute_query(salary_query, salary_structure_params)
                
                if salary_structure_result[1]:
                    # Usar los IDs reales de la estructura
                    real_budget_id = salary_structure_result[1][0]['budget_id']
                    real_category_id = salary_structure_result[1][0]['category_id']
                    real_subcategory_id = salary_structure_result[1][0]['subcategory_id']
                    
                    logger.info(f"Usando IDs reales para el sueldo: budget={real_budget_id}, category={real_category_id}, subcategory={real_subcategory_id}")
                    
                    # Usar los IDs reales para insertar el salario en la estructura correcta
                    salary_budget_id = real_budget_id
                    salary_category_id = real_category_id
                    salary_subcategory_id = real_subcategory_id
                    
                    # Inicializar la estructura si no existe
                    if salary_budget_id not in budgets:
                        budgets[salary_budget_id] = {
                            'id': salary_budget_id,
                            'name': salary_budget_name,
                            'total': 0.0,
                            'budget_amount': 0.0,  # Se actualizará con los valores reales si están disponibles
                            'categories': {}
                        }
                    
                    if salary_category_id not in budgets[salary_budget_id]['categories']:
                        budgets[salary_budget_id]['categories'][salary_category_id] = {
                            'id': salary_category_id,
                            'name': salary_category_name,
                            'total': 0.0,
                            'category_budget_amount': 0.0,
                            'subcategories': {}
                        }
                    
                    if salary_subcategory_id not in budgets[salary_budget_id]['categories'][salary_category_id]['subcategories']:
                        budgets[salary_budget_id]['categories'][salary_category_id]['subcategories'][salary_subcategory_id] = {
                            'id': salary_subcategory_id,
                            'name': salary_subcategory_name,
                            'total': 0.0,
                            'subcategory_budget_amount': 0.0,
                            'patterns': {}
                        }
                else:
                    logger.warning(f"No se encontraron IDs reales para la estructura de sueldo: {salary_budget_name}/{salary_category_name}/{salary_subcategory_name}")
                    
                    # Fallback a la lógica anterior usando nombres y IDs temporales
                    # Buscar por nombre en los presupuestos ya existentes
                    for budget_id, budget in budgets.items():
                        if budget['name'] == salary_budget_name:
                            salary_budget_id = budget_id
                            break
                    
                    if not salary_budget_id:
                        salary_budget_id = f"prev_salary_budget_{len(budgets) + 1}"
                        budgets[salary_budget_id] = {
                            'id': salary_budget_id,
                            'name': salary_budget_name,
                            'total': 0.0,
                            'budget_amount': 0.0,
                            'categories': {}
                        }
                    
                    salary_category_id = None
                    if salary_budget_id in budgets:
                        for cat_id, category in budgets[salary_budget_id]['categories'].items():
                            if category['name'] == salary_category_name:
                                salary_category_id = cat_id
                                break
                        
                    if not salary_category_id:
                        salary_category_id = f"prev_salary_category_{len(budgets[salary_budget_id]['categories']) + 1}"
                        budgets[salary_budget_id]['categories'][salary_category_id] = {
                            'id': salary_category_id,
                            'name': salary_category_name,
                            'total': 0.0,
                            'category_budget_amount': 0.0,
                            'subcategories': {}
                        }
                    
                    salary_subcategory_id = None
                    if salary_category_id in budgets[salary_budget_id]['categories']:
                        for subcat_id, subcategory in budgets[salary_budget_id]['categories'][salary_category_id]['subcategories'].items():
                            if subcategory['name'] == salary_subcategory_name:
                                salary_subcategory_id = subcat_id
                                break
                        
                    if not salary_subcategory_id:
                        salary_subcategory_id = f"prev_salary_subcategory_{len(budgets[salary_budget_id]['categories'][salary_category_id]['subcategories']) + 1}"
                        budgets[salary_budget_id]['categories'][salary_category_id]['subcategories'][salary_subcategory_id] = {
                            'id': salary_subcategory_id,
                            'name': salary_subcategory_name,
                            'total': 0.0,
                            'subcategory_budget_amount': 0.0,
                            'patterns': {}
                        }
            except Exception as e:
                logger.error(f"Error al obtener estructura real para el sueldo: {str(e)}", exc_info=True)
                # Fallback a IDs generados si ocurre un error
                salary_budget_id = f"prev_salary_budget_{len(budgets) + 1}"
                salary_category_id = f"prev_salary_category_1"
                salary_subcategory_id = f"prev_salary_subcategory_1"
                
                # Crear estructura mínima
                budgets[salary_budget_id] = {
                    'id': salary_budget_id,
                    'name': salary_budget_name,
                    'total': 0.0,
                    'budget_amount': 0.0,
                    'categories': {
                        salary_category_id: {
                            'id': salary_category_id,
                            'name': salary_category_name,
                            'total': 0.0,
                            'category_budget_amount': 0.0,
                            'subcategories': {
                                salary_subcategory_id: {
                                    'id': salary_subcategory_id,
                                    'name': salary_subcategory_name,
                                    'total': 0.0,
                                    'subcategory_budget_amount': 0.0,
                                    'patterns': {}
                                }
                            }
                        }
                    }
                }
            
            # Crear un patrón especial para el sueldo del mes anterior usando
            # valores reales de la transacción
            prev_salary_pattern_id = "prev_month_salary_pattern"
            budgets[salary_budget_id]['categories'][salary_category_id]['subcategories'][salary_subcategory_id]['patterns'][prev_salary_pattern_id] = {
                'id': prev_salary_pattern_id,
                'text': "Sueldo del mes anterior",
                'total': previous_month_salary['amount'],
                'transactions': [{
                    'id': previous_month_salary['id'],
                    'amount': previous_month_salary['amount'],
                    'description': previous_month_salary['description'],
                    'type': previous_month_salary['type'],
                    'from_previous_month': True,  # Marcar que viene del mes anterior
                    'transaction_date': previous_month_salary['transaction_date']  # Incluir la fecha original
                }]
            }
            
            # Actualizar totales en la jerarquía para incluir el sueldo del mes anterior
            budgets[salary_budget_id]['categories'][salary_category_id]['subcategories'][salary_subcategory_id]['total'] += previous_month_salary['amount']
            budgets[salary_budget_id]['categories'][salary_category_id]['total'] += previous_month_salary['amount']
            budgets[salary_budget_id]['total'] += previous_month_salary['amount']
        
        # 4. Convertir diccionarios a listas para el formato final de respuesta
        result = []
        for budget_id, budget in budgets.items():
            budget_result = {
                'id': budget['id'],
                'name': budget['name'],
                'total': budget['total'],
                'budget_amount': budget['budget_amount'],
                'categories': []
            }
            
            for category_id, category in budget['categories'].items():
                category_result = {
                    'id': category['id'],
                    'name': category['name'],
                    'total': category['total'],
                    'category_budget_amount': category['category_budget_amount'],
                    'subcategories': []
                }
                
                for subcategory_id, subcategory in category['subcategories'].items():
                    subcategory_result = {
                        'id': subcategory_id,
                        'name': subcategory['name'],
                        'total': subcategory['total'],
                        'subcategory_budget_amount': subcategory['subcategory_budget_amount'],
                        'patterns': []
                    }
                    
                    for pattern_id, pattern in subcategory['patterns'].items():
                        pattern_result = {
                            'id': pattern['id'],
                            'text': pattern['text'],
                            'total': pattern['total'],
                            'transaction_count': len(pattern['transactions'])
                        }
                        subcategory_result['patterns'].append(pattern_result)
                    
                    subcategory_result['patterns'].sort(key=lambda x: x['total'], reverse=True)
                    category_result['subcategories'].append(subcategory_result)
                
                category_result['subcategories'].sort(key=lambda x: x['total'], reverse=True)
                budget_result['categories'].append(category_result)
            
            budget_result['categories'].sort(key=lambda x: x['total'], reverse=True)
            result.append(budget_result)
        
        result.sort(key=lambda x: x['total'], reverse=True)
        
        response = {
            'budgets': result,
            'period': f"{year}-{month:02d}"
        }
        
        if current_month_salary:
            response['current_month_salary'] = current_month_salary
        
        logger.info(f"Resumen de presupuesto generado exitosamente para el usuario {user_id}, período {year}-{month:02d}")
        return response
    
    except Exception as e:
        logger.error(f"Error al generar resumen de presupuesto: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el resumen de presupuesto: {str(e)}"
        )

