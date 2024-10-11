import pandas as pd
import numpy as np
import glob
from sklearn.metrics import mean_absolute_error, mean_squared_error
from permetrics.regression import RegressionMetric

# Ruta al archivo de datos reales
real = 'C:/Users/365N/Desktop/tide_data/processed/puertos_estado_real_datos.csv'

# Cargar los datos reales
df_real = pd.read_csv(real)

# Convertir la columna 'Fecha' a formato datetime
df_real['Fecha'] = pd.to_datetime(df_real['Fecha'])

# Limpiar los nombres de las columnas en df_real
df_real.columns = df_real.columns.str.strip()

# Crear una lista para almacenar los resultados de las métricas
metrics_results = []

# Iterar sobre los archivos predichos en la carpeta
for file in glob.glob('C:/Users/365N/Desktop/tide_data/processed/*.csv'):
    if file != real:
        # Cargar los datos predichos
        df_pred = pd.read_csv(file)
        
        # Limpiar los nombres de las columnas en df_pred
        df_pred.columns = df_pred.columns.str.strip()

        # Verificar los nombres de las columnas para depurar el error
        print(f"Archivo: {file}")
        print(df_pred.columns)  # Verificar las columnas del archivo

        # Convertir la columna 'Fecha' a datetime si existe
        if 'Fecha' in df_pred.columns:
            df_pred['Fecha'] = pd.to_datetime(df_pred['Fecha'])
        else:
            print(f"La columna 'Fecha' no se encontró en el archivo: {file}")
            continue  

        # Verificar si la columna 'Nivel' existe, y ajustar el nombre si es necesario
        if 'Nivel' in df_pred.columns:
            # Realizar el merge basado en la columna 'Fecha'
            df_merged = pd.merge(df_real[['Fecha', 'Nivel Medio']], df_pred[['Fecha', 'Nivel']], on='Fecha')
            
            # Mostrar las primeras filas para verificar la combinación
            print(df_merged.head())
            
            # Extraer los valores de nivel real y predicho
            y_real = df_merged['Nivel Medio'].values
            y_pred = df_merged['Nivel'].values
            print(y_real.mean())
            print(y_pred.mean())
            
            # Calcular las métricas
            bias = mean_absolute_error(y_real, y_pred)
            mse = mean_squared_error(y_real, y_pred)
            rmse = np.sqrt(mse)
            
            # Calcular NSE
            evaluator = RegressionMetric(y_real, y_pred)
            nse = evaluator.nash_sutcliffe_efficiency()  # Calcular NSE

            # Guardar los resultados en la lista
            metrics_results.append({
                'Fuente': file.split('/')[-1],
                'BIAS': bias,
                'MSE': mse,
                'RMSE': rmse,
                'NSE': nse,  # Incluir NSE en los resultados
            })
        else:
            print(f"La columna 'Nivel' no se encontró en el archivo: {file}")

# Guardar los resultados en un archivo CSV
metrics_df = pd.DataFrame(metrics_results)
metrics_df.to_csv('C:/Users/365N/Desktop/tide_data/processed/resultados_metricas.csv', index=False)
