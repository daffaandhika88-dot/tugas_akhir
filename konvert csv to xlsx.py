import pandas as pd

input_csv = '2025-06-15-17-38-20-mavros-global_position-raw-gps_vel.csv'
output_xlsx = '2025-06-15-17-38-20-mavros-global_position-raw-gps_vel.xlsx'

try:
    # Baca CSV dengan handle kemungkinan error format
    df = pd.read_csv(
        input_csv,
        decimal='.',          # Pemisah desimal
        sep=',',             # Pemisah kolom
        encoding='utf-8',    # Encoding file
        engine='python'      # Engine pembaca
    )
    
    # Simpan ke Excel
    df.to_excel(output_xlsx, index=False)
    print(f"SUKSES: File {input_csv} telah dikonversi ke {output_xlsx}")
    
except Exception as e:
    print(f"ERROR: Gagal konversi. Pesan error: {str(e)}")