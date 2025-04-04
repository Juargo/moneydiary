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
    bank_id: int = Form(...),
):
    """
    Recibe y procesa un archivo Excel de banco.

    - **file**: Archivo Excel del banco
    - **bank_id**: ID del banco (bancoestado, bancochile, bancosantander, bancobci)

    Retorna el saldo contable y los movimientos extraídos del archivo, distinguiendo entre ingresos y gastos.
    Las transacciones que coinciden con patrones a ignorar serán excluidas del procesamiento.
    """
    logger.info(f"Inicio de procesamiento de archivo bancario: {file.filename}, banco_id: {bank_id}")
    
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
        logger.info(f"Procesando archivo para banco: {bank_id}")
       
        # Pasar los patrones a ignorar a la función de extracción
        movimientos = await extraer_datos(temp_file.name, pattern_ignores)
        logger.info(f"Extracción completada: transacciones={len(movimientos)}")
        
        # Sanitizar datos para evitar errores de serialización JSON
        response_data = {
            "bank_id": bank_id,
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
            # Verificar si la fila contiene encabezados de interés
            if any(header.lower() in row_str for header in fecha_headers + descripcion_headers + cargos_headers + abonos_headers):
                # Encontrar la fila de encabezado
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
                            pattern_exp = pattern["exp_name"]
                            
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
    
    try:
        logger.info(f"Iniciando categorización de {len(transacciones)} transacciones")
        
        # Preparar la estructura para transacciones categorizadas
        transacciones_categorizadas = []
        
        # Contador para estadísticas
        contador_categorizadas = 0
        
        # Procesar cada transacción
        for transaccion in transacciones:
            descripcion = transaccion["Descripción"].lower() if transaccion.get("Descripción") else ""
            transaccion_categorizada = transaccion.copy()
            
            # Valores predeterminados
            transaccion_categorizada["category_id"] = None
            transaccion_categorizada["category_name"] = "Sin categoría"
            transaccion_categorizada["subcategory_id"] = None
            transaccion_categorizada["subcategory_name"] = "Sin subcategoría"
            transaccion_categorizada["category_color"] = "#CCCCCC"  # Color gris por defecto
            
            # Buscar coincidencias con patrones
            for categoria in patrones_usuario:
                for subcategoria in categoria["subcategories"]:
                    for patron in subcategoria["patterns"]:
                        pattern_text = patron["pattern_text"]
                        is_regex = patron["is_regex"]
                        
                        # Verificar si hay coincidencia
                        coincide = False
                        if is_regex:
                            try:
                                # Usar expresión regular
                                if re.search(pattern_text, descripcion, re.IGNORECASE):
                                    coincide = True
                            except re.error:
                                # Si hay error en la expresión regular, tratar como texto simple
                                coincide = pattern_text.lower() in descripcion
                        else:
                            # Búsqueda de texto simple
                            coincide = pattern_text.lower() in descripcion
                        
                        if coincide:
                            # Asignar categoría y subcategoría
                            transaccion_categorizada["category_id"] = categoria["category_id"]
                            transaccion_categorizada["category_name"] = categoria["category_name"]
                            transaccion_categorizada["subcategory_id"] = subcategoria["subcategory_id"]
                            transaccion_categorizada["subcategory_name"] = subcategoria["subcategory_name"]
                            transaccion_categorizada["category_color"] = categoria["category_color"]
                            contador_categorizadas += 1
                            
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
        return transacciones

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
            p.exp_name AS pattern_text,
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
                "exp_name": pattern.exp_name,
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

