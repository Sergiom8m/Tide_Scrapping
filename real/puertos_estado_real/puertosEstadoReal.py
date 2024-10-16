from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")


datos = {}

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

url = 'https://portus.puertos.es/index.html#/dataTablesRTWidget?stationCode=3114&variables=SEA_LEVEL&isRadar=false&latId=&lonId=&locale=es'

driver.get(url)
driver.execute_script("document.body.style.zoom='0.60'")

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, '__BVID__8'))
    )
    
    rendered_html = driver.page_source
except Exception as e:
    print(f"Ocurrió un error: {e}")
    
# Encontrar los botones para cambiar la cantidad de elementos a mostrar
botones = driver.find_elements(By.CLASS_NAME, 'dx-page-size')

# Seleccionar el botón para mostrar 500 elementos (ultimo botón)
botones[-1].click()

time.sleep(5)

# Encontrar la tabla de datos
contenedor_datos = driver.find_element(By.ID, '__BVID__9')

# Encontrar varias capas mas abajo un div de una clase especifica
div_datos = contenedor_datos.find_element(By.XPATH, './/div[@class="dx-datagrid-rowsview dx-datagrid-nowrap"]')

# Encontrar un par de capas mas abajo la etiqueta table
tabla_datos = div_datos.find_element(By.XPATH, './/table')

# Obtener datos de las primeras 60 filas
for index, tr in enumerate(tabla_datos.find_elements(By.XPATH, './/tr')):
    if index >= 3600:  # Limitar a las primeras 60 filas
        break

    # Obtener los valores de la fila
    valores = [td.text for td in tr.find_elements(By.XPATH, './/td')]
    
    if len(valores) > 0:
        fecha = valores[0]  
        nivel_medio = valores[2]
    
        # Agregar los valores a una estructura de datos (fecha, nivel_medio)
        datos[fecha] = nivel_medio   

driver.quit()

# Convertir el diccionario a DataFrame
df_nuevos = pd.DataFrame(datos.items(), columns=['Fecha', 'Nivel Medio'])

# Intentar cargar el CSV existente para agregar nuevos datos
try:
    # Leer el CSV existente
    df_existente = pd.read_csv('//192.168.0.250/intellialert/Vigilancia/Marea/real/puertos_estado_real/data/datos.csv')
    
    # Concatenar los nuevos datos, evitando duplicados de 'Fecha'
    df_final = pd.concat([df_nuevos, df_existente]).drop_duplicates(subset='Fecha', keep='first')
except FileNotFoundError:
    # Si el archivo no existe, simplemente se crea uno nuevo
    df_final = df_nuevos

# Ordenar por fecha en orden descendente (nuevos primero)
df_final = df_final.sort_values(by='Fecha', ascending=False)

# Guardar los datos en el archivo CSV
df_final.to_csv(f'//192.168.0.250/intellialert/Vigilancia/Marea/real/puertos_estado_real/data/datos.csv', index=False)
