import os
import glob
import pandas as pd

def interpolar_csv(file_path, output_path, data_source):
    df = pd.read_csv(file_path)

    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format='%Y-%m-%d %H:%M:%S')

    df.set_index(df.columns[0], inplace=True)

    if data_source.lower() == 'armada':
        df['Nivel'] = df['Nivel'] - 2.359
    elif data_source.lower() == 'puertos_estado':
        df['Nivel'] = df['Nivel'] - 2.359 + 0.16
    elif data_source.lower() == 'copernicus':
        df['Nivel'] = df['Nivel'] + 0.3225
    elif data_source.lower() == 'shom':
        df['Nivel'] = df['Nivel'] + 0.15
        df.index = df.index - pd.Timedelta(hours=2)

    # Resample y aplicar interpolación
    df_resampled = df.resample('10T').mean()
    df_resampled = df_resampled.interpolate(method='cubicspline')

    # Guardar el resultado en un nuevo CSV
    df_resampled.to_csv(output_path)

base_dir = 'C:/Users/365N/Desktop/tide_data'
latest_files = []

# Buscar archivos en la carpeta base
for root, dirs, files in os.walk(base_dir):
    if os.path.basename(root) == 'data':
        all_files = glob.glob(os.path.join(root, '*.csv'))  

        if all_files:
            latest_file = max(all_files, key=os.path.getmtime)
            latest_files.append(latest_file)

# Procesar cada archivo encontrado
for input_csv in latest_files:
    # Obtener la fuente de datos de la carpeta anterior a 'data'
    data_source = os.path.basename(os.path.dirname(os.path.dirname(input_csv))).lower()  # Nombre de la carpeta anterior a 'data'
    
    # Crear el nombre de salida
    output_csv = f'C:/Users/365N/Desktop/tide_data/processed/{data_source}.csv'
    
    # Llamar a la función de interpolación
    interpolar_csv(input_csv, output_csv, data_source)
