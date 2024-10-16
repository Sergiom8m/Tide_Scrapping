import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from pathlib import Path
import pandas as pd

# Inicializa la aplicación de Firebase
cred = credentials.Certificate('priv.json')
firebase_admin.initialize_app(cred)

# Inicializa Firestore
db = firestore.client()

path_puertos = Path('C:/Users/365N/Desktop/tide_data/processed/puertos_estado.csv')

# Leer el archivo CSV con pandas
df = pd.read_csv(path_puertos)

# Recorre las filas del dataframe
for index, row in df.iterrows():
    # Convertir la columna 'Fecha' a un objeto datetime
    fecha_hora = datetime.strptime(row['Fecha'], '%Y-%m-%d %H:%M:%S')
    
    # Formato 'fechaHora': 'YYYYMMDDHHMM'
    fecha_hora_str = fecha_hora.strftime('%Y%m%d%H%M')
    
    # Formato 'fecha': 'YYYY/MM/DD' y 'hora': 'HH:MM'
    fecha_str = fecha_hora.strftime('%Y/%m/%d')
    hora_str = fecha_hora.strftime('%H:%M')
    
    # Calcular nivelEuskalmet (Nivel + 2.69)
    nivel_euskalmet = row['Nivel'] + 2.69
    
    # Crear un diccionario con los datos en el formato especificado
    data = {
        'fechaHora': fecha_hora_str,
        'fecha': fecha_str,
        'hora': hora_str,
        'nivelMedio': row['Nivel'],
        'nivelEuskalmet': nivel_euskalmet
    }
    
    # Agregar los datos a Firestore (en una colección, por ejemplo, 'mareas2')
    db.collection('mareas2').document(fecha_hora_str).set(data)
    
    
