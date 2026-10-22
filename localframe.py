# Re-import libraries after kernel reset
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Transformer

# Reload the file
file_path = "PARSING_1_DATALOG_SENSOR_PERSEPSI_NAVIGASI.xlsx"
sheet_name = "PARSING_1_DATALOG_SENSOR_PERSEP"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Konversi GPS ke derajat desimal
df['Latitude'] = df['Latitude'] / 1e7
df['Longitude'] = df['Longitude'] / 1e7

# Titik referensi ENU
origin_lat = df['Latitude'].iloc[0]
origin_lon = df['Longitude'].iloc[0]

# Konversi GPS ke ENU
transformer = Transformer.from_crs(
    "epsg:4326",
    f"+proj=tmerc +lat_0={origin_lat} +lon_0={origin_lon} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",
    always_xy=True
)
df['East'], df['North'] = transformer.transform(df['Longitude'].values, df['Latitude'].values)
df['East'] -= df['East'].iloc[0]
df['North'] -= df['North'].iloc[0]

# Yaw dari magnetometer
df['Yaw_rad'] = np.arctan2(df['My'], df['Mx'])
df['Yaw_deg'] = np.degrees(df['Yaw_rad'])
df['Yaw_deg'] = (df['Yaw_deg'] + 180) % 360 - 180

# Gabungkan Date dan Time menjadi datetime
df['datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))

# Tambahkan kolom elapsed_time (dalam detik sejak awal)
df['elapsed_time'] = (df['datetime'] - df['datetime'].iloc[0]).dt.total_seconds()

# Plot ulang dengan sumbu waktu dalam detik
plt.figure(figsize=(15, 10))

# Gyroscope
plt.subplot(2, 2, 1)
plt.plot(df['elapsed_time'], df['Gx'], label='Gx')
plt.plot(df['elapsed_time'], df['Gy'], label='Gy')
plt.plot(df['elapsed_time'], df['Gz'], label='Gz')
plt.title('Gyroscope Data')
plt.xlabel('Time (seconds)')
plt.ylabel('Gyro (°/s atau rad/s)')
plt.legend()
plt.grid(True)

# Accelerometer
plt.subplot(2, 2, 2)
plt.plot(df['elapsed_time'], df['Ax'], label='Ax')
plt.plot(df['elapsed_time'], df['Ay'], label='Ay')
plt.plot(df['elapsed_time'], df['Az'], label='Az')
plt.title('Accelerometer Data')
plt.xlabel('Time (seconds)')
plt.ylabel('Accel (m/s²)')
plt.legend()
plt.grid(True)

# Magnetometer
plt.subplot(2, 2, 3)
plt.plot(df['elapsed_time'], df['Mx'], label='Mx')
plt.plot(df['elapsed_time'], df['My'], label='My')
plt.plot(df['elapsed_time'], df['Mz'], label='Mz')
plt.title('Magnetometer Data')
plt.xlabel('Time (seconds)')
plt.ylabel('Magnetometer')
plt.legend()
plt.grid(True)

# GPS Path in ENU (tetap pakai East-North)
plt.subplot(2, 2, 4)
plt.plot(df['East'], df['North'], marker='o', markersize=2, label='GPS Track (ENU)')
plt.title('GPS Path in Local ENU Frame')
plt.xlabel('East (m)')
plt.ylabel('North (m)')
plt.axis('equal')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
