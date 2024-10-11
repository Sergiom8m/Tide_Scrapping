from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time 
import csv
from datetime import datetime, timedelta

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

url = 'https://services.data.shom.fr/oceano/render/text?duration=4&delta-date=0&lon=-3.0512966332596534&lat=43.36006414172118&lang=fr'

driver.get(url)

# Encontrar el único tag <pre> en la página
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, 'pre'))
)

# Obtener el texto del tag <pre>
rendered_html = driver.page_source

driver.quit()

# Día y hora actual
fechaHora = time.strftime('%Y-%m-%d_%H-%M')

# Eliminar las primeras 71 líneas del HTML
rendered_html = rendered_html.split('\n')[71:]

# Eliminar las filas que empiezan por AAAA-MM-DD 00:00:00 y AAAA-MM-DD 01:00:00 donde DD es el día actual
fecha_actual = datetime.now()
fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')
rendered_html = [line for line in rendered_html if not line.startswith(f'{fecha_actual_str} 00:00:00') and not line.startswith(f'{fecha_actual_str} 01:00:00')]

# En la última línea quitar el final: </pre></body></html>
rendered_html[-1] = rendered_html[-1].replace('</pre></body></html>', '')

# Crear un diccionario para almacenar las mediciones
datos = {}


# Fecha límite: 3 días a partir de ahora, a las 23:00:00
fecha_limite = fecha_actual.replace(hour=1, minute=0, second=0, microsecond=0) + timedelta(days=3)

# Procesar las líneas del texto
for line in rendered_html:
    line = line.strip()
    if not line: 
        continue

    # Separar los campos
    campos = line.split(';')
    if len(campos) != 4:
        print(f'Error: Formato incorrecto en la línea: {line}')
        continue # Ignorar líneas con formato incorrecto
    
    fecha_str, profundidad, medicion, tipo_medicion = campos

    # Convertir la cadena de fecha a objeto datetime
    try:
        fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print(f'Error: Formato de fecha incorrecto en la línea: {line}')
        continue

    # Verificar si la fecha es mayor que la fecha límite
    if fecha > fecha_limite:
        continue  # Ignorar esta línea si está más allá de la fecha límite

    # Verificar que el tipo de medición sea válido (8 o 9)
    if tipo_medicion.strip() in ('8', '9'):
        # Formatear la fecha y hora
        if fecha_str not in datos:
            datos[fecha_str] = {'marea': None, 'nivel': None}

        # Almacenar medición según el tipo
        if tipo_medicion.strip() == '8':  # Marea
            datos[fecha_str]['marea'] = medicion.strip()
        elif tipo_medicion.strip() == '9':  # Nivel
            datos[fecha_str]['nivel'] = medicion.strip()

# Guardar en un archivo CSV
csv_filename = f'C:/Users/jlupiola/Desktop/tide_data/predictions/shom/data/datos_{time.strftime("%Y-%m-%d_%H-%M")}.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Fecha', 'Marea', 'Nivel']) 

    # Escribir las filas de datos
    for fecha, mediciones in datos.items():
        marea = mediciones['marea'] if mediciones['marea'] is not None else ''
        nivel = mediciones['nivel'] if mediciones['nivel'] is not None else ''
        writer.writerow([fecha, marea, nivel])
