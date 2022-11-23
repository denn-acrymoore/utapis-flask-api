"""NOTE: File ini digunakan untuk uji API saat mengirimkan artikel."""
import requests
import json

url = "http://localhost:8000/utapis-cek-sintaksis-kal"

article = """TRIBUNNEWS.COM, SERPONG - Universitas Multimedia Nusantara (UMN) mengembangkan aplikasi penapis kesalahan berbahasa pada tulisan yang diberi nama U-Tapis.

Pengembangan aplikasi U-Tapis bertepatan dengan bulan bahasa Indonesia yang dirayakan setiap bulan Oktober.
"""

response = requests.post(url, data={"article": article}, stream=True)

idx = 1
for r in response.iter_lines():
    print(f"Result {idx}")
    idx += 1
    print(r)
    print()
