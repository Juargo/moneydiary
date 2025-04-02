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

# def sanitize_json_data(obj: Any) -> Any:
#     """
#     Convierte valores no serializables en JSON (como NaN, Infinity) a valores compatibles.
#     También convierte numpy.int64/float64 a tipos Python nativos para serialización.
#     """
#     if isinstance(obj, dict):
#         return {k: sanitize_json_data(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [sanitize_json_data(item) for item in obj]
#     elif isinstance(obj, (np.integer, np.int64)):
#         return int(obj)
#     elif isinstance(obj, (np.floating, np.float64)):
#         num = float(obj)
#         if math.isnan(num):
#             return None
#         elif math.isinf(num):
#             return None  # o podrías usar str(num) para mantener "inf"/"-inf" como cadena
#         else:
#             return num
#     elif isinstance(obj, (pd.Timestamp, pd._libs.tslibs.timestamps.Timestamp)):
#         return obj.isoformat()
#     elif pd.isna(obj):
#         return None
#     else:
#         return obj

@router.post("/upload-bank-report")
async def upload_bank_report(
    file: UploadFile = File(...),
    bank_id: str = Form(...),
):
    """
    Recibe y procesa un archivo Excel de banco.

    - **file**: Archivo Excel del banco
    - **bank_id**: ID del banco (bancoestado, bancochile, bancosantander, bancobci)

    Retorna el saldo contable y los movimientos extraídos del archivo, distinguiendo entre ingresos y gastos.
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

        # Procesar el archivo según el ID del banco
        logger.info(f"Procesando archivo para banco: {bank_id}")
        if bank_id == 'bancoestado':  # BancoEstado
            logger.info("Iniciando extracción de datos para BancoEstado")
            saldo, movimientos = extraer_datos_bancoestado(temp_file.name)
        elif bank_id == 'bancochile':  # BancoChile
            logger.info("Iniciando extracción de datos para BancoChile")
            saldo, movimientos = extraer_datos_bancochile(temp_file.name)
        elif bank_id == 'bancosantander':  # Santander
            logger.info("Iniciando extracción de datos para Santander")
            saldo, movimientos = extraer_datos_santander(temp_file.name)
        elif bank_id == 'bancobci':  # BCI
            logger.info("Iniciando extracción de datos para BCI")
            saldo, movimientos = extraer_datos_bci(temp_file.name)
        else:
            logger.error(f"ID de banco no válido: {bank_id}")
            raise HTTPException(
                status_code=400, detail=f"ID de banco no válido: {bank_id}"
            )
        
        logger.info(f"Extracción completada: saldo={saldo}, transacciones={len(movimientos)}")
        
        # Sanitizar datos para evitar errores de serialización JSON
        response_data = {
            "bank_id": bank_id,
            "balance": saldo,
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


def extraer_datos_bancoestado(archivo):
    """Extrae el saldo contable y movimientos de un archivo de BancoEstado."""
    logger.info(f"Iniciando extracción de datos de BancoEstado desde archivo: {archivo}")
    
    try:
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]  # Asume que la primera hoja es la correcta
        logger.info(f"Hoja de cálculo a procesar: {sheet_name}")
        
        df = pd.read_excel(xls, sheet_name=sheet_name)
        logger.info(f"Archivo Excel cargado exitosamente. Dimensiones: {df.shape}")
        
        # Extraer saldo contable
        saldo_contable = df.iloc[9, 3]
        logger.info(f"Saldo contable extraído: {saldo_contable}")
        
        # Extraer movimientos (a partir de la fila 13 en adelante)
        df_movimientos = df.iloc[
            13:, [0, 1, 2, 3]
        ]  # Fecha, N° Operación, Descripción, Cargo/Abono
        
        df_movimientos.columns = ["Fecha", "N° Operación", "Descripción", "Monto"]
        logger.info(f"Datos iniciales extraídos: {len(df_movimientos)} filas")
        
        # Filtrar filas que corresponden a subtotales o totales
        df_movimientos = df_movimientos[
            ~df_movimientos["Descripción"].astype(str).str.contains("Subtotal|SUBTOTAL|Total|TOTAL", na=False)
        ]
        
        # Filtrar filas donde la fecha no es nula (elimina filas de subtotal adicionales)
        df_movimientos = df_movimientos[df_movimientos["Fecha"].notna()]
        logger.info(f"Datos después de filtrar filas inválidas: {len(df_movimientos)} filas")
        
        # Convertir montos a numéricos
        df_movimientos["Monto"] = pd.to_numeric(df_movimientos["Monto"], errors="coerce")
        
        # Identificar ingresos y gastos
        df_movimientos["Tipo"] = df_movimientos["Monto"].apply(
            lambda x: "Ingreso" if x > 0 else "Gasto" if x < 0 else None
        )
        
        # Filtrar registros con montos válidos y tipos identificados
        df_movimientos = df_movimientos[df_movimientos["Tipo"].notna()]
        
        # Tomar el valor absoluto de los montos
        df_movimientos["Monto"] = df_movimientos["Monto"].abs()
        logger.info(f"Datos finales procesados: {len(df_movimientos)} transacciones")
        
        # Contabilizar tipos
        ingresos = (df_movimientos["Tipo"] == "Ingreso").sum()
        gastos = (df_movimientos["Tipo"] == "Gasto").sum()
        logger.info(f"Distribución: {ingresos} ingresos, {gastos} gastos")
        
        # Convertir DataFrame a lista de diccionarios
        movimientos_bancoestado = df_movimientos.to_dict(orient="records")
        logger.info(f"Extracción finalizada: {len(movimientos_bancoestado)} movimientos")
        
        return saldo_contable, movimientos_bancoestado
    except Exception as e:
        logger.error(f"Error en extraer_datos_bancoestado: {str(e)}", exc_info=True)
        return 0, []


def extraer_datos_bancochile(archivo):
    """Extrae el saldo contable y movimientos de un archivo de Banco de Chile."""
    try:
        logger.info(f"Iniciando procesamiento de archivo Banco Chile: {archivo}")
        # Intentar múltiples estrategias para cargar y procesar el archivo
        
        # 1. Intento directo con pandas - formato estándar
        try:
            # Cargar el archivo Excel - probar primero sheet_name=0
            df = pd.read_excel(archivo, sheet_name=0)
            logger.info(f"Archivo cargado exitosamente con dimensiones: {df.shape}")
            
            # Estrategia 1: Formato específico para Banco de Chile
            # Este es un enfoque directo para extraer datos si conocemos la estructura exacta
            saldo, movimientos = extraer_datos_bancochile_formato1(df)
            if movimientos and len(movimientos) > 0:
                logger.info(f"Datos extraídos con formato 1: {len(movimientos)} movimientos")
                return saldo, movimientos
            
            # Estrategia 2: Búsqueda flexible de patrones
            saldo, movimientos = extraer_datos_bancochile_formato2(df)
            if movimientos and len(movimientos) > 0:
                logger.info(f"Datos extraídos con formato 2: {len(movimientos)} movimientos")
                return saldo, movimientos
            
            # Estrategia 3: Análisis estructural completo
            logger.info("Usando análisis estructural para detectar movimientos")
            saldo, movimientos = extraer_datos_bancochile_analisis_estructural(df)
            if movimientos and len(movimientos) > 0:
                logger.info(f"Datos extraídos con análisis estructural: {len(movimientos)} movimientos")
                return saldo, movimientos
            
        except Exception as e:
            logger.warning(f"Error en primer intento: {str(e)}. Intentando con otras hojas...")
        
        # 2. Probar con todas las hojas del archivo
        xls = pd.ExcelFile(archivo)
        for sheet_name in xls.sheet_names:
            try:
                logger.info(f"Intentando con hoja: {sheet_name}")
                df = pd.read_excel(xls, sheet_name=sheet_name)
                
                # Intentar los mismos métodos con cada hoja
                saldo, movimientos = extraer_datos_bancochile_formato1(df)
                if movimientos and len(movimientos) > 0:
                    logger.info(f"Datos extraídos de hoja {sheet_name} con formato 1: {len(movimientos)} movimientos")
                    return saldo, movimientos
                
                saldo, movimientos = extraer_datos_bancochile_formato2(df)
                if movimientos and len(movimientos) > 0:
                    logger.info(f"Datos extraídos de hoja {sheet_name} con formato 2: {len(movimientos)} movimientos")
                    return saldo, movimientos
                
                saldo, movimientos = extraer_datos_bancochile_analisis_estructural(df)
                if movimientos and len(movimientos) > 0:
                    logger.info(f"Datos extraídos de hoja {sheet_name} con análisis estructural: {len(movimientos)} movimientos")
                    return saldo, movimientos
                
            except Exception as e:
                logger.warning(f"Error procesando hoja {sheet_name}: {str(e)}")
        
        # 3. Último intento - cargar sin encabezados
        try:
            logger.info("Intentando cargar sin encabezados")
            df = pd.read_excel(archivo, header=None)
            saldo, movimientos = extraer_datos_bancochile_sin_encabezados(df)
            if movimientos and len(movimientos) > 0:
                logger.info(f"Datos extraídos sin encabezados: {len(movimientos)} movimientos")
                return saldo, movimientos
        except Exception as e:
            logger.warning(f"Error en intento sin encabezados: {str(e)}")
        
        # Si llegamos aquí, no se pudieron extraer datos
        logger.error("No se pudieron extraer movimientos del archivo de Banco Chile")
        return 0, []
            
    except Exception as e:
        logger.error(f"Error general al procesar archivo de Banco Chile: {str(e)}", exc_info=True)
        return 0, []

def extraer_datos_bancochile_formato1(df):
    """Extrae datos de archivo BancoChile con formato estándar"""
    logger.info("Intentando extraer datos con formato estándar de BancoChile")
    saldo_disponible = 0
    
    # Buscar saldo directamente - formato común
    try:
        # Buscar celdas que contengan "Saldo"
        for i in range(min(20, len(df))):
            row_str = ' '.join([str(x).lower() for x in df.iloc[i].values if not pd.isna(x)])
            if 'saldo' in row_str:
                # Buscar valor numérico en la misma fila
                numeric_values = [x for x in df.iloc[i].values if isinstance(x, (int, float)) and not pd.isna(x)]
                if numeric_values:
                    saldo_disponible = float(numeric_values[0])
                    logger.info(f"Saldo encontrado: {saldo_disponible}")
                    break
    except Exception as e:
        logger.warning(f"Error al buscar saldo: {str(e)}")
    
    # Buscar tabla de movimientos por encabezados específicos
    try:
        # Buscar fila con encabezados típicos de Banco Chile
        encabezados_buscar = ['fecha', 'descripción', 'cargo', 'abono', 'monto']
        header_row = None
        
        for i in range(len(df)):
            # Convertir fila a texto y buscar encabezados
            row_values = [str(x).lower() for x in df.iloc[i].values if not pd.isna(x)]
            row_str = ' '.join(row_values)
            
            # Verificar cuántos encabezados están presentes
            present_headers = sum(1 for h in encabezados_buscar if any(h in s for s in row_values))
            
            if present_headers >= 2:  # Si hay al menos 2 encabezados
                header_row = i
                logger.info(f"Encabezados encontrados en fila {i}: {row_str}")
                break
        
        if header_row is not None:
            # Verificar que hay suficientes filas para procesar después del encabezado
            if header_row + 1 < len(df):
                # Extraer datos desde la fila siguiente a los encabezados
                data_df = df.iloc[header_row+1:].copy()
                
                # Asegurar que las columnas sean válidas antes de asignar
                valid_columns = []
                if len(df.iloc[header_row]) == len(data_df.columns):
                    # Asignar nombres de columnas desde la fila de encabezado
                    data_df.columns = df.iloc[header_row]
                else:
                    # Si hay un problema con las dimensiones, usar nombres genéricos
                    logger.warning(f"Incompatibilidad en número de columnas. Usando nombres genéricos.")
                    data_df.columns = [f"Column{i}" for i in range(len(data_df.columns))]
                
                # Identificar columnas relevantes
                cols = {
                    'fecha': None,
                    'descripcion': None,
                    'cargo': None,
                    'abono': None,
                    'monto': None
                }
                
                # Mapear columnas detectadas
                for col in data_df.columns:
                    col_str = str(col).lower()
                    if 'fecha' in col_str:
                        cols['fecha'] = col
                    elif any(x in col_str for x in ['descripción', 'descripcion', 'glosa', 'detalle']):
                        cols['descripcion'] = col
                    elif any(x in col_str for x in ['cargo', 'débito', 'debito']):
                        cols['cargo'] = col
                    elif any(x in col_str for x in ['abono', 'crédito', 'credito']):
                        cols['abono'] = col
                    elif 'monto' in col_str:
                        cols['monto'] = col
                
                # Si no se encontró columna de fecha, usar la primera columna
                if cols['fecha'] is None and len(data_df.columns) > 0:
                    cols['fecha'] = data_df.columns[0]
                
                # Si no se encontró descripción, usar la segunda columna
                if cols['descripcion'] is None and len(data_df.columns) > 1:
                    cols['descripcion'] = data_df.columns[1]
                
                # Crear DataFrame normalizado
                result_df = pd.DataFrame()
                
                # Procesar fechas y descripciones
                if cols['fecha'] and cols['descripcion']:
                    # Verificar si las columnas existen en el DataFrame
                    if cols['fecha'] in data_df.columns and cols['descripcion'] in data_df.columns:
                        result_df['Fecha'] = data_df[cols['fecha']]
                        result_df['Descripción'] = data_df[cols['descripcion']]
                        
                        # Procesar montos - diferentes posibles formatos
                        result_df['Cargo'] = 0
                        result_df['Abono'] = 0
                        
                        # Función para limpiar y convertir montos
                        def parse_monto(valor):
                            if pd.isna(valor):
                                return 0
                            if isinstance(valor, (int, float)):
                                return float(valor)
                            # Limpiar strings
                            valor_str = str(valor).replace('$', '').replace('.', '').replace(',', '.').strip()
                            try:
                                return float(valor_str)
                            except:
                                return 0
                        
                        # Procesar cargos y abonos si existen
                        if cols['cargo'] and cols['cargo'] in data_df.columns:
                            result_df['Cargo'] = data_df[cols['cargo']].apply(parse_monto)
                        if cols['abono'] and cols['abono'] in data_df.columns:
                            result_df['Abono'] = data_df[cols['abono']].apply(parse_monto)
                        
                        # Si hay una columna de monto único
                        if cols['monto'] and cols['monto'] in data_df.columns and not (cols['cargo'] or cols['abono']):
                            montos = data_df[cols['monto']].apply(parse_monto)
                            result_df['Cargo'] = montos.apply(lambda x: abs(x) if x < 0 else 0)
                            result_df['Abono'] = montos.apply(lambda x: x if x > 0 else 0)
                        
                        # Determinar tipo - Corregir la lógica
                        # Siempre asignar según valores en Cargo y Abono
                        result_df['Tipo'] = 'Gasto'  # Valor predeterminado
                        
                        # Es un gasto si hay valor en Cargo
                        gastos_mask = result_df['Cargo'] > 0
                        result_df.loc[gastos_mask, 'Tipo'] = 'Gasto'
                        
                        # Es un ingreso si hay valor en Abono y no hay valor en Cargo
                        ingresos_mask = (result_df['Abono'] > 0) & (~gastos_mask)
                        result_df.loc[ingresos_mask, 'Tipo'] = 'Ingreso'
                        
                        # Calcular monto final basado en el tipo
                        result_df['Monto'] = result_df.apply(
                            lambda row: row['Abono'] if row['Tipo'] == 'Ingreso' else row['Cargo'], 
                            axis=1
                        )
                        
                        # Limpiar datos
                        result_df = result_df.dropna(subset=['Fecha'])
                        result_df = result_df[result_df['Monto'] != 0]
                        
                        # Filtrar filas de totales y subtotales
                        result_df = result_df[~result_df['Descripción'].astype(str).str.contains('total|subtotal|saldo', case=False)]
                        
                        # Convertir a lista de diccionarios
                        movimientos = result_df[['Fecha', 'Descripción', 'Monto', 'Tipo']].to_dict(orient='records')
                        
                        if movimientos and len(movimientos) > 0:
                            return saldo_disponible, movimientos
    
    except Exception as e:
        logger.warning(f"Error en formato 1: {str(e)}")
    
    return saldo_disponible, []

def extraer_datos_bancochile_formato2(df):
    """Extrae datos con un enfoque más flexible para otro formato de BancoChile"""
    saldo_disponible = 0
    
    # Identificar patrones de fechas - común en cartolas bancarias
    try:
        fecha_columna = None
        fecha_indices = []
        
        # Buscar columna con mayor número de fechas
        for col_idx in range(df.shape[1]):
            fecha_count = 0
            for row_idx in range(df.shape[0]):
                cell = df.iloc[row_idx, col_idx]
                # Verificar si es fecha por tipo o por formato
                if isinstance(cell, (pd.Timestamp, datetime, date)):
                    fecha_count += 1
                    fecha_indices.append(row_idx)
                elif isinstance(cell, str) and len(cell) >= 8:
                    # Verificar patrones de fecha como DD/MM/YYYY o similares
                    if any(x in cell for x in ['/', '-', '.']) and any(char.isdigit() for char in cell):
                        try:
                            # Intentar convertir a fecha con formato explícito para Chile (DD/MM/YYYY)
                            pd.to_datetime(cell, errors='raise', dayfirst=True)
                            fecha_count += 1
                            fecha_indices.append(row_idx)
                        except:
                            pass
            
            if fecha_count > 5:  # Si hay suficientes fechas
                fecha_columna = col_idx
                break
        
        if fecha_columna is not None and fecha_indices:
            # Encontrar el inicio de la tabla (primer índice con fecha)
            inicio_tabla = min(fecha_indices)
            
            # Asumir que el inicio de la tabla es la fila anterior (encabezados)
            header_row = max(0, inicio_tabla - 1)
            
            # Extraer la tabla y convertir a DataFrame
            data_df = df.iloc[inicio_tabla:].copy()
            
            # Usar encabezados de la fila anterior o generar automáticamente
            if header_row >= 0:
                # Verificar si la fila tiene valores no nulos (posibles encabezados)
                header_values = [str(x) for x in df.iloc[header_row] if not pd.isna(x)]
                if len(header_values) >= 2:  # Al menos 2 encabezados
                    data_df.columns = df.iloc[header_row]
                else:
                    # Generar encabezados genéricos
                    data_df.columns = [f"Col{i}" for i in range(data_df.shape[1])]
            else:
                # Generar encabezados genéricos
                data_df.columns = [f"Col{i}" for i in range(data_df.shape[1])]
            
            # Identificar columnas por posición si no hay encabezados claros
            col_fecha = data_df.columns[fecha_columna]
            
            # Buscar columna de descripción (generalmente la segunda columna o tercera)
            col_descripcion = None
            for i in range(1, min(4, data_df.shape[1])):
                if i != fecha_columna:  # No usar la columna de fecha
                    # Verificar si la columna tiene valores de texto
                    text_values = data_df.iloc[:, i].astype(str).str.len() > 5
                    if text_values.sum() > len(data_df) * 0.5:  # Al menos 50% son textos largos
                        col_descripcion = data_df.columns[i]
                        break
            
            # Si no se encontró, usar la siguiente columna después de la fecha
            if col_descripcion is None:
                next_col = fecha_columna + 1
                if next_col < data_df.shape[1]:
                    col_descripcion = data_df.columns[next_col]
                else:
                    # No hay columna disponible, usar primera columna
                    col_descripcion = data_df.columns[0]
            
            # Buscar columnas numéricas para montos
            cols_numericas = []
            for i in range(data_df.shape[1]):
                if i not in [fecha_columna, data_df.columns.get_loc(col_descripcion)]:
                    # Verificar si la columna tiene valores numéricos
                    numeric_values = pd.to_numeric(data_df.iloc[:, i], errors='coerce')
                    if numeric_values.notna().sum() > len(data_df) * 0.3:  # Al menos 30% son números
                        cols_numericas.append(data_df.columns[i])
            
            # Crear DataFrame normalizado
            result_df = pd.DataFrame()
            result_df['Fecha'] = data_df[col_fecha]
            result_df['Descripción'] = data_df[col_descripcion]
            
            # Inicializar columnas de montos
            result_df['Cargo'] = 0
            result_df['Abono'] = 0
            
            # Función para limpiar y convertir montos
            def parse_monto(valor):
                if pd.isna(valor):
                    return 0
                if isinstance(valor, (int, float)):
                    return float(valor)
                # Limpiar strings
                valor_str = str(valor).replace('$', '').replace('.', '').replace(',', '.').strip()
                try:
                    return float(valor_str)
                except:
                    return 0
            
            # Procesar columnas numéricas
            if len(cols_numericas) == 1:
                # Una sola columna de monto (probablemente con signos)
                montos = pd.to_numeric(data_df[cols_numericas[0]], errors='coerce').fillna(0)
                result_df['Cargo'] = montos.apply(lambda x: abs(x) if x < 0 else 0)
                result_df['Abono'] = montos.apply(lambda x: x if x > 0 else 0)
            elif len(cols_numericas) >= 2:
                # Probablemente columnas separadas para cargo y abono
                cargo_encontrado = False
                abono_encontrado = False
                
                for col in cols_numericas:
                    valores = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
                    # Si la mayoría son negativos, probablemente es cargo
                    neg_count = (valores < 0).sum()
                    pos_count = (valores > 0).sum()
                    
                    if neg_count > pos_count and not cargo_encontrado:
                        result_df['Cargo'] = valores.apply(lambda x: abs(x) if x < 0 else 0)
                        cargo_encontrado = True
                    elif pos_count > neg_count and not abono_encontrado:
                        result_df['Abono'] = valores.apply(lambda x: x if x > 0 else 0)
                        abono_encontrado = True
            
            # Determinar tipo - Corregir la lógica
            # Siempre asignar según valores en Cargo y Abono
            result_df['Tipo'] = 'Gasto'  # Valor predeterminado
            
            # Es un gasto si hay valor en Cargo
            gastos_mask = result_df['Cargo'] > 0
            result_df.loc[gastos_mask, 'Tipo'] = 'Gasto'
            
            # Es un ingreso si hay valor en Abono y no hay valor en Cargo
            ingresos_mask = (result_df['Abono'] > 0) & (~gastos_mask)
            result_df.loc[ingresos_mask, 'Tipo'] = 'Ingreso'
            
            # Calcular monto final basado en el tipo
            result_df['Monto'] = result_df.apply(
                lambda row: row['Abono'] if row['Tipo'] == 'Ingreso' else row['Cargo'], 
                axis=1
            )
            
            # Limpiar datos
            result_df = result_df.dropna(subset=['Fecha'])
            result_df = result_df[result_df['Monto'] != 0]
            
            # Filtrar filas de totales y subtotales
            result_df = result_df[~result_df['Descripción'].astype(str).str.contains('total|subtotal|saldo', case=False)]
            
            # Convertir a lista de diccionarios
            movimientos = result_df[['Fecha', 'Descripción', 'Monto', 'Tipo']].to_dict(orient='records')
            
            if movimientos and len(movimientos) > 0:
                return saldo_disponible, movimientos
    
    except Exception as e:
        logger.warning(f"Error en formato 2: {str(e)}")
    
    return saldo_disponible, []

def extraer_datos_bancochile_analisis_estructural(df):
    """Realiza un análisis estructural completo para identificar tablas de datos"""
    saldo_disponible = 0
    
    try:
        # 1. Buscar regiones densas con datos no nulos
        regiones_candidatas = []
        
        # Calcular la densidad de datos en bloques
        for i in range(0, len(df) - 10, 5):
            # Contar celdas no nulas en el bloque
            bloque = df.iloc[i:i+10]
            densidad = bloque.notna().sum().sum() / (bloque.shape[0] * bloque.shape[1])
            
            if densidad > 0.5:  # Al menos 50% de celdas con datos
                # Verificar si hay columnas numéricas
                num_cols = sum(1 for col in bloque.columns 
                              if pd.to_numeric(bloque[col], errors='coerce').notna().sum() > 5)
                
                if num_cols >= 1:  # Al menos una columna con números
                    regiones_candidatas.append((i, i+10, densidad, num_cols))
        
        # Ordenar regiones por densidad y número de columnas numéricas
        regiones_candidatas.sort(key=lambda x: (x[2], x[3]), reverse=True)
        
        # Procesar cada región candidata
        for inicio, fin, densidad, num_cols in regiones_candidatas:
            # Extraer la región
            bloque = df.iloc[inicio:fin].copy()
            
            # Buscar columnas con fechas
            fecha_cols = []
            for col in bloque.columns:
                # Verificar si la columna tiene fechas
                if bloque[col].apply(lambda x: isinstance(x, (pd.Timestamp, datetime, date))).any():
                    fecha_cols.append(col)
            
            # Si hay columnas de fecha, usar la primera como inicio
            if fecha_cols:
                col_fecha = fecha_cols[0]
                
                # Buscar fila de inicio (primera fila con fecha)
                for i in range(len(bloque)):
                    if isinstance(bloque.iloc[i][col_fecha], (pd.Timestamp, datetime, date)):
                        inicio_datos = i
                        break
                else:
                    inicio_datos = 0
                
                # Extraer datos desde el inicio
                data_df = bloque.iloc[inicio_datos:].copy()
                
                # Generar encabezados genéricos
                data_df.columns = [f"Col{i}" for i in range(data_df.shape[1])]
                
                # Identificar columnas clave
                col_fecha_str = f"Col{bloque.columns.get_loc(col_fecha)}"
                
                # Buscar columna de descripción (columna con más texto)
                col_desc = None
                max_text_len = 0
                
                for col in data_df.columns:
                    if col != col_fecha_str:
                        # Calcular longitud promedio de texto
                        text_len = data_df[col].astype(str).str.len().mean()
                        if text_len > max_text_len:
                            max_text_len = text_len
                            col_desc = col
                
                # Buscar columnas numéricas (posibles montos)
                col_montos = []
                for col in data_df.columns:
                    if col not in [col_fecha_str, col_desc]:
                        # Verificar si la columna tiene valores numéricos
                        nums = pd.to_numeric(data_df[col], errors='coerce')
                        if nums.notna().sum() > 3:  # Al menos 3 valores numéricos
                            col_montos.append(col)
                
                # Si tenemos fecha, descripción y algún monto, procesar
                if col_desc and col_montos:
                    # Crear DataFrame normalizado
                    result_df = pd.DataFrame()
                    result_df['Fecha'] = data_df[col_fecha_str]
                    result_df['Descripción'] = data_df[col_desc]
                    
                    # Inicializar columnas de montos
                    result_df['Cargo'] = 0
                    result_df['Abono'] = 0
                    
                    # Procesar columnas de montos
                    if len(col_montos) == 1:
                        # Una sola columna de monto (con signos)
                        montos = pd.to_numeric(data_df[col_montos[0]], errors='coerce').fillna(0)
                        result_df['Cargo'] = montos.apply(lambda x: abs(x) if x < 0 else 0)
                        result_df['Abono'] = montos.apply(lambda x: x if x > 0 else 0)
                    else:
                        # Múltiples columnas - intentar detectar cargo y abono
                        for col in col_montos:
                            valores = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
                            # Si la mayoría son negativos, probablemente es cargo
                            neg_count = (valores < 0).sum()
                            pos_count = (valores > 0).sum()
                            
                            if neg_count > pos_count:
                                result_df['Cargo'] += valores.apply(lambda x: abs(x) if x < 0 else 0)
                            else:
                                result_df['Abono'] += valores.apply(lambda x: x if x > 0 else 0)
                    
                    # Determinar tipo - Corregir la lógica
                    # Siempre asignar según valores en Cargo y Abono
                    result_df['Tipo'] = 'Gasto'  # Valor predeterminado
                    
                    # Es un gasto si hay valor en Cargo
                    gastos_mask = result_df['Cargo'] > 0
                    result_df.loc[gastos_mask, 'Tipo'] = 'Gasto'
                    
                    # Es un ingreso si hay valor en Abono y no hay valor en Cargo
                    ingresos_mask = (result_df['Abono'] > 0) & (~gastos_mask)
                    result_df.loc[ingresos_mask, 'Tipo'] = 'Ingreso'
                    
                    # Calcular monto final basado en el tipo
                    result_df['Monto'] = result_df.apply(
                        lambda row: row['Abono'] if row['Tipo'] == 'Ingreso' else row['Cargo'], 
                        axis=1
                    )
                    
                    # Limpiar datos
                    result_df = result_df.dropna(subset=['Fecha'])
                    result_df = result_df[result_df['Monto'] != 0]
                    
                    # Convertir a lista de diccionarios
                    movimientos = result_df[['Fecha', 'Descripción', 'Monto', 'Tipo']].to_dict(orient='records')
                    
                    if movimientos and len(movimientos) > 0:
                        return saldo_disponible, movimientos
    
    except Exception as e:
        logger.warning(f"Error en análisis estructural: {str(e)}")
    
    return saldo_disponible, []

def extraer_datos_bancochile_sin_encabezados(df):
    """Extrae datos cuando no hay encabezados claros"""
    saldo_disponible = 0
    
    try:
        # Asumiendo que los primeros N (5-10) filas contienen información general
        # y el resto es la tabla de movimientos
        
        # Buscar saldo en las primeras filas
        for i in range(min(15, len(df))):
            row_str = ' '.join([str(x).lower() for x in df.iloc[i].values if not pd.isna(x)])
            if 'saldo' in row_str:
                # Buscar valores numéricos en la fila
                nums = [x for x in df.iloc[i].values if isinstance(x, (int, float)) and not pd.isna(x)]
                if nums:
                    saldo_disponible = float(nums[0])
                    break
        
        # Intentar detectar dónde comienza la tabla de datos
        # Buscar filas con fechas en la primera columna
        fecha_indices = []
        for i in range(len(df)):
            cell = df.iloc[i, 0]
            if isinstance(cell, (pd.Timestamp, datetime, date)):
                fecha_indices.append(i)
            elif isinstance(cell, str) and len(cell) >= 8:
                # Verificar si parece una fecha
                if any(x in cell for x in ['/', '-', '.']) and any(char.isdigit() for char in cell):
                    fecha_indices.append(i)
        
        if fecha_indices:
            # Encontrar secuencias continuas de fechas
            secuencias = []
            seq_actual = [fecha_indices[0]]
            
            for i in range(1, len(fecha_indices)):
                if fecha_indices[i] == fecha_indices[i-1] + 1:
                    seq_actual.append(fecha_indices[i])
                else:
                    if len(seq_actual) >= 3:  # Secuencia con al menos 3 fechas
                        secuencias.append(seq_actual)
                    seq_actual = [fecha_indices[i]]
            
            # Agregar última secuencia si es válida
            if len(seq_actual) >= 3:
                secuencias.append(seq_actual)
            
            # Usar la secuencia más larga
            if secuencias:
                secuencia_principal = max(secuencias, key=len)
                inicio_datos = secuencia_principal[0]
                
                # Extraer datos
                data_df = df.iloc[inicio_datos:].copy()
                
                # Asignar nombres genéricos a las columnas
                data_df.columns = [f"Col{i}" for i in range(data_df.shape[1])]
                
                # Asumir columna 0 es fecha, columna 1 es descripción
                result_df = pd.DataFrame()
                result_df['Fecha'] = data_df['Col0']
                
                # Buscar columna de descripción (mayor longitud de texto)
                col_desc = None
                max_text_len = 0
                
                for i in range(1, min(4, data_df.shape[1])):
                    col = f"Col{i}"
                    text_len = data_df[col].astype(str).str.len().mean()
                    if text_len > max_text_len:
                        max_text_len = text_len
                        col_desc = col
                
                if not col_desc:
                    col_desc = 'Col1' if data_df.shape[1] > 1 else 'Col0'
                
                result_df['Descripción'] = data_df[col_desc]
                
                # Inicializar columnas de montos
                result_df['Cargo'] = 0
                result_df['Abono'] = 0
                
                # Buscar columnas numéricas para montos
                col_montos = []
                for i in range(data_df.shape[1]):
                    col = f"Col{i}"
                    if col not in ['Col0', col_desc]:
                        nums = pd.to_numeric(data_df[col], errors='coerce')
                        if nums.notna().sum() > 3:  # Al menos 3 valores numéricos
                            col_montos.append(col)
                
                # Procesar columnas de montos
                if col_montos:
                    if len(col_montos) == 1:
                        # Una sola columna con signos
                        montos = pd.to_numeric(data_df[col_montos[0]], errors='coerce').fillna(0)
                        result_df['Cargo'] = montos.apply(lambda x: abs(x) if x < 0 else 0)
                        result_df['Abono'] = montos.apply(lambda x: x if x > 0 else 0)
                    else:
                        # Intentar identificar cargos y abonos
                        for col in col_montos:
                            valores = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
                            if (valores < 0).sum() > (valores > 0).sum():
                                result_df['Cargo'] += valores.apply(lambda x: abs(x) if x < 0 else 0)
                            else:
                                result_df['Abono'] += valores.apply(lambda x: x if x > 0 else 0)
                
                # Determinar tipo - Corregir la lógica
                # Siempre asignar según valores en Cargo y Abono
                result_df['Tipo'] = 'Gasto'  # Valor predeterminado
                
                # Es un gasto si hay valor en Cargo
                gastos_mask = result_df['Cargo'] > 0
                result_df.loc[gastos_mask, 'Tipo'] = 'Gasto'
                
                # Es un ingreso si hay valor en Abono y no hay valor en Cargo
                ingresos_mask = (result_df['Abono'] > 0) & (~gastos_mask)
                result_df.loc[ingresos_mask, 'Tipo'] = 'Ingreso'
                
                # Calcular monto final basado en el tipo
                result_df['Monto'] = result_df.apply(
                    lambda row: row['Abono'] if row['Tipo'] == 'Ingreso' else row['Cargo'], 
                    axis=1
                )
                
                # Limpiar datos
                result_df = result_df.dropna(subset=['Fecha'])
                result_df = result_df[result_df['Monto'] != 0]
                
                # Convertir a lista de diccionarios
                movimientos = result_df[['Fecha', 'Descripción', 'Monto', 'Tipo']].to_dict(orient='records')
                
                if movimientos and len(movimientos) > 0:
                    return saldo_disponible, movimientos
    
    except Exception as e:
        logger.warning(f"Error en método sin encabezados: {str(e)}")
    
    return saldo_disponible, []


def extraer_datos_santander(archivo):
    """Extrae el saldo contable y movimientos de un archivo de Banco Santander."""
    try:
        logger.info(f"Iniciando procesamiento de archivo Santander: {archivo}")
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        logger.info(f"Procesando archivo Santander con forma: {df.shape}")
        
        # Inicializar variables
        saldo_disponible = None
        df_movimientos = None
        
        # Intento 1: Buscar la tabla de movimientos por encabezados
        for i in range(len(df) - 5):  # Revisar todas las filas, dejando margen para datos
            current_row = df.iloc[i:i+1]
            row_text = " ".join([str(x).lower() for x in current_row.values.flatten() if pd.notna(x)])
            
            # Buscar patrones comunes en encabezados de movimientos Santander
            if any(x in row_text for x in ["fecha", "descripción", "cargo", "abono", "detalle"]):
                logger.info(f"Encontrados posibles encabezados en fila {i}: {row_text}")
                
                # Intentar extraer la tabla usando esta fila como encabezado
                try:
                    headers = [str(col).strip() for col in df.iloc[i]]
                    df_movimientos = pd.DataFrame(df.iloc[i+1:].values, columns=headers)
                    
                    # Verificar si tenemos datos válidos
                    if len(df_movimientos) > 0:
                        logger.info(f"Tabla de movimientos extraída con {len(df_movimientos)} filas")
                        break
                except Exception as e:
                    logger.warning(f"Error al extraer tabla en fila {i}: {str(e)}")
        
        # Si no se encontró la tabla, buscar por análisis de estructura
        if df_movimientos is None:
            logger.info("Buscando tabla por análisis de estructura...")
            
            # Buscar bloques de texto que contengan columnas numéricas (posibles montos)
            for i in range(len(df) - 10):
                numeric_cols = df.iloc[i:i+10].select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:  # Al menos dos columnas numéricas (cargo y abono)
                    # Verificar si hay texto que parece encabezados en esta área
                    text_cols = [col for col in df.columns if col not in numeric_cols]
                    if len(text_cols) >= 1:  # Al menos una columna de texto (descripción)
                        logger.info(f"Posible tabla encontrada en fila {i}")
                        
                        # Crear nombres de columna si no son claros
                        headers = []
                        for j, col in enumerate(df.columns):
                            if j in numeric_cols:
                                if "cargo" not in headers and "abono" not in headers:
                                    headers.append("Cargo" if j % 2 == 0 else "Abono")
                                else:
                                    headers.append("Monto" + str(j))
                            else:
                                if "fecha" not in headers:
                                    headers.append("Fecha")
                                elif "descrip" not in headers and "detalle" not in headers:
                                    headers.append("Descripción")
                                else:
                                    headers.append("Texto" + str(j))
                        
                        # Crear DataFrame con datos desde esta fila
                        df_movimientos = pd.DataFrame(df.iloc[i:].values, columns=headers)
                        break
        
        # Procesar el DataFrame de movimientos si se encontró
        if df_movimientos is not None:
            # Eliminar filas sin fechas o con datos incompletos
            df_movimientos = df_movimientos.dropna(thresh=3)  # Al menos 3 columnas con datos
            
            # Buscar columnas clave
            col_fecha = next((col for col in df_movimientos.columns if "fecha" in str(col).lower()), None)
            col_descripcion = next((col for col in df_movimientos.columns 
                                   if any(x in str(col).lower() for x in ["descrip", "detalle", "glosa", "concepto"])), None)
            col_cargo = next((col for col in df_movimientos.columns 
                             if any(x in str(col).lower() for x in ["cargo", "débito", "debito"])), None)
            col_abono = next((col for col in df_movimientos.columns 
                             if any(x in str(col).lower() for x in ["abono", "crédito", "credito"])), None)
            
            logger.info(f"Columnas identificadas: Fecha={col_fecha}, Desc={col_descripcion}, Cargo={col_cargo}, Abono={col_abono}")
            
            # Verificar que tenemos las columnas mínimas necesarias
            if col_fecha is not None and col_descripcion is not None and (col_cargo is not None or col_abono is not None):
                # Crear DataFrame final con columnas estandarizadas
                df_final = pd.DataFrame()
                df_final["Fecha"] = df_movimientos[col_fecha]
                df_final["Descripción"] = df_movimientos[col_descripcion]
                
                # Inicializar columnas numéricas
                df_final["Cargo"] = 0
                df_final["Abono"] = 0
                
                # Función para convertir valores a números
                def parse_monto(valor):
                    if pd.isna(valor):
                        return 0
                    if isinstance(valor, (int, float)):
                        return valor
                    try:
                        # Limpiar el valor (quitar símbolos, separadores, etc.)
                        valor_str = str(valor).replace('$', '').replace('.', '').replace(',', '.').strip()
                        return float(valor_str)
                    except:
                        return 0
                
                # Procesar columnas de cargo y abono
                if col_cargo is not None:
                    df_final["Cargo"] = pd.to_numeric(df_movimientos[col_cargo], errors="coerce")
                if col_abono is not None:
                    df_final["Abono"] = pd.to_numeric(df_movimientos[col_abono], errors="coerce")
                
                # Si existe una columna de monto que puede tener valores positivos (abonos) y negativos (cargos)
                if "Monto" in df_movimientos.columns or any("monto" in str(col).lower() for col in df_movimientos.columns):
                    col_monto = next((col for col in df_movimientos.columns if "monto" in str(col).lower()), None)
                    if col_monto:
                        df_final["Monto"] = pd.to_numeric(df_movimientos[col_monto], errors="coerce")
                        # Los cargos son negativos, los abonos positivos
                        df_final["Cargo"] = df_final["Cargo"].fillna(0) + df_final["Monto"].apply(lambda x: abs(x) if x < 0 else 0)
                        df_final["Abono"] = df_final["Abono"].fillna(0) + df_final["Monto"].apply(lambda x: x if x > 0 else 0)
                
                # Determinar el tipo de transacción
                df_final["Tipo"] = "Gasto"
                df_final.loc[df_final["Abono"] > 0, "Tipo"] = "Ingreso"
                
                # Calcular monto total (positivo para ambos tipos)
                df_final["Monto"] = df_final["Cargo"] + df_final["Abono"]
                
                # Limpiar datos - eliminar filas sin montos o con fechas inválidas
                df_final = df_final[df_final["Monto"] > 0]  # Solo montos positivos > 0
                df_final = df_final[~df_final["Fecha"].astype(str).str.contains("Total|TOTAL|Subtotal", case=False)]
                
                # Formatear datos para el resultado final
                movimientos_santander = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                
                logger.info(f"Extraídos {len(movimientos_santander)} movimientos de Santander")
                if movimientos_santander:
                    logger.debug(f"Primer movimiento: {movimientos_santander[0]}")
                
                return saldo_disponible or 0, movimientos_santander
            else:
                logger.warning("No se encontraron columnas necesarias en los datos")
                return 0, []
        else:
            logger.warning("No se pudo identificar la tabla de movimientos")
            return 0, []
    
    except Exception as e:
        logger.error(f"Error al procesar archivo de Banco Santander: {str(e)}", exc_info=True)
        return 0, []


def extraer_datos_bci(archivo):
    """Extrae el saldo contable y movimientos de un archivo de BCI."""
    try:
        logger.info(f"Iniciando procesamiento de archivo BCI: {archivo}")
        
        # Cargar el archivo Excel
        xls = pd.ExcelFile(archivo)
        sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # No hay saldo para BCI según requerimientos
        saldo_bci = 0

        # Buscar columnas con información de movimientos
        header_row = None
        for i, row in df.iterrows():
            row_str = row.to_string().lower()
            if (
                "fecha" in row_str
                and any(term in row_str for term in ["transacción", "transaccion", "detalle", "descripción"])
                and any(term in row_str for term in ["cargo", "débito", "abono", "crédito", "monto"])
            ):
                header_row = i
                break

        if header_row is not None:
            df_movimientos = df.iloc[header_row + 1:].copy()
            df_movimientos.columns = df.iloc[header_row]
            
            # Mapear las columnas necesarias
            column_mapping = {
                "Fecha": ["Fecha", "Fecha Transacción", "FECHA"],
                "Descripción": ["Descripción", "DESCRIPCION", "Detalle", "Glosa"],
                "Cargo": ["Cargo", "CARGO", "Débito", "Monto Débito"],
                "Abono": ["Abono", "ABONO", "Crédito", "Monto Crédito"],
                "Monto": ["Monto", "MONTO", "Valor"]
            }
            
            # Buscar las columnas en el dataframe
            found_columns = {}
            for target_col, possible_names in column_mapping.items():
                for col_name in df_movimientos.columns:
                    col_str = str(col_name).lower()
                    if any(possible.lower() in col_str for possible in possible_names):
                        found_columns[target_col] = col_name
                        break
            
            # Verificar que tenemos las columnas mínimas necesarias
            if "Fecha" in found_columns and "Descripción" in found_columns and any(k in found_columns for k in ["Cargo", "Abono", "Monto"]):
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
                
                # Convertir a lista de diccionarios
                movimientos_bci = df_final[["Fecha", "Descripción", "Monto", "Tipo"]].to_dict(orient="records")
                logger.info(f"Extracción completada: movimientos={len(movimientos_bci)}")
                if len(movimientos_bci) > 0:
                    logger.debug(f"Muestra de datos: {movimientos_bci[0]}")
                return saldo_bci, movimientos_bci
            else:
                return saldo_bci, []
        else:
            return saldo_bci, []
    except Exception as e:
        logger.error(f"Error al procesar archivo de BCI: {str(e)}", exc_info=True)
        return 0, []


# Modelo para recibir transacciones en masa
class TransactionInput(BaseModel):
    fecha: Union[str, date, datetime]
    descripcion: str
    monto: float
    categoria: Optional[str] = "Sin clasificar"
    banco_id: Optional[int] = None
    tipo: Optional[str] = None  # Agregamos el campo tipo como opcional

