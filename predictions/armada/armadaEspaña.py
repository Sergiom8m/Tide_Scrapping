from datetime import datetime, timedelta
import requests
import csv
import time

# Guardar el día de hoy en formato YYYY-MM-DD
fecha = datetime.now()

# Ajustar la fecha inicial a dos días antes
fecha_inicial = fecha - timedelta(days=2)

# Crear una lista para almacenar los datos antes de escribirlos en el CSV
data_rows = []

# Iterar desde 2 días antes hasta 4 días después (un total de 7 días)
for i in range(7):
    # Convertir la fecha al formato deseado (YYYYMMDD para la URL)
    fecha_formateada = fecha_inicial.strftime("%Y%m%d")
    
    # Crear la URL con la fecha formateada
    url = f"https://ideihm.covam.es/api-ihm/getmarea?request=gettide&id=2&format=json&date={fecha_formateada}"
    
    # Hacer la petición GET
    response_json = requests.get(url).json()
    
    # Recoger un array con las 4 mediciones 
    valores = response_json['mareas']['datos']
    
    # Iterar sobre los valores y almacenarlos en la lista data_rows
    for medicion in valores['marea']:
        hora = medicion['hora']
        altura = medicion['altura']
        
        # Formatear la fecha y hora como YYYY-MM-DD HH:MM:SS
        fecha_hora = f"{fecha_inicial.strftime('%Y-%m-%d')} {hora}:00"
        
        # Añadir la fila a la lista
        data_rows.append([fecha_hora, altura])
    
    # Sumar un día a la fecha inicial
    fecha_inicial += timedelta(days=1)

# Guardar todos los datos recolectados en el archivo CSV
with open(f'//192.168.0.250/intellialert/Vigilancia/Marea/predictions/armada/data/datos_{time.strftime("%Y-%m-%d_%H-%M")}.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escribir el encabezado
    writer.writerow(['Fecha', 'Nivel'])
    # Escribir todas las filas
    writer.writerows(data_rows)
