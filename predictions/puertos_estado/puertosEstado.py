import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def mesANumero(mes_str):
    meses = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12
    }
    return meses.get(mes_str.lower(), None)

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    url = 'https://portus.puertos.es/index.html#/dataTablesPredWidget?locationCode=11120&nombre=Bilbao&latitud=43.367000579833984&longitud=-3.068000078201294&region=NoValid&variable=SEA_LEVEL&mapResource=pred-markers-nivmar-puerto&locale=es&mareografo=3114'
    driver.get(url)
    driver.execute_script("document.body.style.zoom='0.60'")

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, '__BVID__10'))
        )
    except Exception as e:
        print(f"Ocurrió un error: {e}")

    contenedor_datos = driver.find_element(By.ID, '__BVID__10__BV_tab_container_')
    ul_tab = driver.find_element(By.ID, '__BVID__10__BV_tab_controls_')
    dias = ul_tab.find_elements(By.XPATH, './li')

    # Crear una lista para almacenar las filas de datos
    data_rows = []

    # Iterar por los contenedores de datos (días)
    for index, contenedor in enumerate(contenedor_datos.find_elements(By.XPATH, './div')):
        dias[index].click()
        time.sleep(5)

        # Usar la fecha correspondiente al día actual
        fecha_string = dias[index].text.strip()
        componentes_fecha = fecha_string.split(' ')
        mes_numero = mesANumero(componentes_fecha[3])
        fecha = f'{componentes_fecha[5]}-{mes_numero:02d}-{int(componentes_fecha[1]):02d}'
        print(fecha)

        # Inicializar data_rows para el día actual
        daily_data_rows = [[] for _ in range(24)]  # Crea 24 filas vacías para cada hora

        tabla_datos = contenedor.find_elements(By.XPATH, './/table')[1]
        
        # Obtener datos de cada medición
        for i, tr in enumerate(tabla_datos.find_elements(By.XPATH, './/tr')):
            # Obtener los valores de la fila
            valores = [td.text for td in tr.find_elements(By.XPATH, './/td')]
            
            if len(valores) > 0:
                tipo_medicion = valores[1]  # Primer valor que indica el tipo de medición
                mediciones = valores[2:]  # 24 mediciones correspondientes a las horas

                # Para cada hora (00:00 a 23:00), formateamos y añadimos los datos
                for hora, medicion in enumerate(mediciones):
                    hora_str = f'{hora:02d}:00:00'
                    fecha_hora_str = f"{fecha} {hora_str}"  # Formato YYYY-MM-DD HH:MM:SS
                    
                    if tipo_medicion == 'Nivel (m)':
                        daily_data_rows[hora] = [fecha_hora_str, medicion, '', '', '']  # Nivel
                    elif tipo_medicion == 'Marea (m)':
                        daily_data_rows[hora][2] = medicion  # Marea
                    elif tipo_medicion == 'Residuo (m)':
                        daily_data_rows[hora][3] = medicion  # Residuo
                    elif tipo_medicion == 'Presión (mb)':
                        daily_data_rows[hora][4] = medicion  # Presión
        
        # Agregar los datos del día actual a data_rows
        data_rows.extend(daily_data_rows)  # Agrega las filas del día actual a la lista general

    # Guardar en un archivo CSV
    csv_filename = f'C:/Users/jlupiola/Desktop/tide_data/predictions/puertos_estado/data/datos_{time.strftime("%Y-%m-%d_%H-%M")}.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escribir los encabezados
        writer.writerow(['Fecha', 'Nivel', 'Marea', 'Residuo', 'Presion'])
        # Escribir los datos
        writer.writerows(data_rows)

    driver.quit()



