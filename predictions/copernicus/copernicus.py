import copernicusmarine
import numpy as np
import pandas as pd
import netCDF4 as nc
from netCDF4 import Dataset
import datetime
import os
import time

# Obtener la fecha de hoy a las 00:00
fechaHoraInicio = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

# Obtener fecha de hoy + 3 días a las 23:00
fechaHoraFin = (datetime.datetime.now() + datetime.timedelta(days=2)).replace(hour=23, minute=0, second=0, microsecond=0)

# Formato de fecha y hora para el servicio
fechaHoraInicio_str = fechaHoraInicio.strftime('%Y-%m-%dT%H:%M:%S')
fechaHoraFin_str = fechaHoraFin.strftime('%Y-%m-%dT%H:%M:%S')

# Llamada a la función de Copernicus Marine
copernicusmarine.subset(
    dataset_id="cmems_mod_ibi_phy_anfc_0.027deg-2D_PT1H-m",
    dataset_version="202211",
    variables=["zos", "vo"],
    minimum_longitude=-3.1226038374150487,
    maximum_longitude=-3.1226038374150487,
    minimum_latitude=43.36669096842379,
    maximum_latitude=43.36669096842379,
    start_datetime=fechaHoraInicio_str,
    end_datetime=fechaHoraFin_str,
    force_download=True,
    subset_method="strict",
    disable_progress_bar=True,
    output_directory="C:/Users/jlupiola/Desktop/tide_data/predictions/copernicus/data"
)

# Guardar fecha de inicio y fin en formato 2024-10-08 
fechaInicio = fechaHoraInicio.strftime('%Y-%m-%d')
fechaFin = fechaHoraFin.strftime('%Y-%m-%d')

# Cargar el dataset
dataset = Dataset(f'C:/Users/jlupiola/Desktop/tide_data/predictions/copernicus/data/cmems_mod_ibi_phy_anfc_0.027deg-2D_PT1H-m_zos-vo_3.11W_43.36N_{fechaInicio}-{fechaFin}.nc', 'r')  

zos = dataset.variables['zos'][:].data.flatten()
fecha = dataset.variables['time'][:].data.flatten()

fecha = np.asarray(fecha, dtype=float)

# Las fechas están medidas en horas desde 1950-01-01 00:00:00. Cambiar a formato de fecha
fecha = [datetime.datetime(1950, 1, 1) + datetime.timedelta(hours=float(t)) for t in fecha]

# Crear DataFrame
df = pd.DataFrame({'Fecha': fecha, 'Nivel': zos})

# Guardar DataFrame en CSV
df.to_csv(f'C:/Users/jlupiola/Desktop/tide_data/predictions/copernicus/data/datos_{time.strftime("%Y-%m-%d_%H-%M")}.csv', index=False)

# Cerrar el dataset
dataset.close()

# Borrar el archivo .nc
os.remove(f'C:/Users/jlupiola/Desktop/tide_data/predictions/copernicus/data/cmems_mod_ibi_phy_anfc_0.027deg-2D_PT1H-m_zos-vo_3.11W_43.36N_{fechaInicio}-{fechaFin}.nc')
