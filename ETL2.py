import pandas as pd
import numpy as np

# Ruta del archivo de Excel
file_path = 'C:/Users/salin/OneDrive - alumnos.uv.cl/10 Semestre/Inteligencia de Negocios/proyecto/proyecto/BaseDefinitivaINDICES-2005-2024.xlsx'

def etl_process_cohort_analysis(file_path):
    # Extracción: Cargar el archivo Excel y seleccionar la hoja con los datos
    excel_data = pd.ExcelFile(file_path)
    data = excel_data.parse(excel_data.sheet_names[0])  # Carga la primera hoja

    # Selección de columnas clave para el análisis
    columns_of_interest = [
        "Año", "Carrera Genérica", "Nombre Region", "Vacantes", "Matrícula primer año hombres",
        "Matrícula primer año mujeres", "Matrícula Primer Año", "Matrícula Total", "Máximo Puntaje NEM",
        "Promedio Puntaje NEM", "Mínimo Puntaje NEM", "Máximo Puntaje Ranking", "Promedio Puntaje Ranking",
        "Mínimo Puntaje Ranking", "Tipo Carrera", "IngresoDirecto", "Matrícula primer año extranjeros"
    ]
    data_filtered = data[columns_of_interest].copy()

    # Filtrar solo los datos entre 2014 y 2024
    data_filtered = data_filtered[(data_filtered["Año"] >= 2014) & (data_filtered["Año"] <= 2024)]

    # Limpieza de datos: Eliminar duplicados
    data_filtered = data_filtered.drop_duplicates()

    # Imputación de valores faltantes en columnas clave
    columns_to_impute = [
        "Vacantes", "Matrícula Primer Año", "Matrícula Total", "Máximo Puntaje NEM", "Promedio Puntaje NEM",
        "Mínimo Puntaje NEM", "Máximo Puntaje Ranking", "Promedio Puntaje Ranking", "Mínimo Puntaje Ranking"
    ]
    for column in columns_to_impute:
        if column in data_filtered.columns:
            data_filtered.loc[:, column] = data_filtered[column].fillna(data_filtered[column].mean())

    # Estandarización de formatos
    data_filtered['Año'] = pd.to_numeric(data_filtered['Año'], errors='coerce')  # Asegura que el año esté en formato numérico
    data_filtered['Nombre Region'] = data_filtered['Nombre Region'].str.title()  # Normaliza el nombre de la región

    # Crear métricas adicionales
    data_filtered["Ingreso_Total"] = data_filtered["Matrícula primer año hombres"].fillna(0) + data_filtered["Matrícula primer año mujeres"].fillna(0) + data_filtered["Matrícula primer año extranjeros"].fillna(0)
    # Calcular "Retención" correctamente
    data_filtered["Retención"] = np.where(
        data_filtered["Ingreso_Total"] > 0,
        (data_filtered["Matrícula Total"] / data_filtered["Ingreso_Total"]) * 100,
        0  # Si no hay ingresos, la retención es 0
    )
   

    # Segmentación y agregación para análisis de cohortes
    cohort_analysis = data_filtered.groupby(["Año", "Carrera Genérica", "Nombre Region", "Tipo Carrera"]).agg({
        "Ingreso_Total": "sum",
        "Matrícula Total": "sum",
        "Vacantes": "sum",
        "Promedio Puntaje NEM": "mean",
        "Promedio Puntaje Ranking": "mean",
        "Retención": "mean"
    }).reset_index()

     # Limpieza adicional después de la agregación
    cohort_analysis = cohort_analysis.drop_duplicates()  # Eliminar duplicados nuevamen

    # Exportar datos listos para Power BI
    output_path = "C:/Users/salin/OneDrive - alumnos.uv.cl/10 Semestre/Inteligencia de Negocios/proyecto/proyecto/DatosFinal.xlsx"
    cohort_analysis.to_excel(output_path, index=False)

    return cohort_analysis, output_path

# Ejecutar el proceso ETL
etl_result, output_path = etl_process_cohort_analysis(file_path)
print(f"ETL completado. Datos guardados en {output_path}")
