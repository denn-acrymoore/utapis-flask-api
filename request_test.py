"""NOTE: File ini digunakan untuk uji API saat mengirimkan artikel."""
import requests

url = "http://10.100.1.99:8080/utapis-cek-sintaksis-kal"

article = """TRIBUNNEWS.COM, JAKARTA --Penggunaan laser dalam dunia kedokteran khususnya kesehatan kulit bukanlah hal  baru.

Ada banyak jenis laser dan masing-masing mempunyai kegunaannya sendiri

Mulai dari efektif mengatasi permasalahan kulit, penggunaan yang instan, serta hasil yang jangka panjang.

Dokter spesialis bedah plastik rekonstruksi dari Siloam Hospitals Balikpapan, dr. Arie Wibisono, Sp.BP-RE. mengatakan, RS Siloam Balikpapan telah menerapkan pelayanan terapi laser.

"Dari segi estetik, terapi laser dapat digunakan untuk perawatan, peremajaan, dan kecantikan kulit. Termasuk terapi laser untuk menghilangkan tatoo serta menyamarkan bekas luka," kata dia, melalui edukasi bincang sehat pada aplikasi Live Instagram, baru-baru ini.

Dikatakan Dokter Arie, terapi laser  tidak hanya bagi kaum wanita namun mulai diminati kaum lelaki dalam perawatan dan peremajaan kulit.

"Seperti menghilangkan kerutan di wajah dan leher. Terbukti dengan sekali sampai maksimal 2 kali perawatan sudah terlihat hasilnya, dengan dikombinasikan terapi yang lain seperti penggunaan serum dan krim," ungkapnya.

dr. Arie mengatakan, penggunaan laser ini juga bisa untuk menghilangkan bulu-bulu halus di tubuh secara permanen.

Metode sinar laser ini juga dapat menghilangkan jerawat di wajah mulai untuk  usia remaja sampai usia produktif.

Jerawat yang timbul ini di era pandemi ini dapat dipicu akibat penggunaan masker yang terlalu lama sehingga menyebabkan jerawat di sekitar hidung mulut dan pipi.

"Semua hal ini bisa ditangani dengan laser, jadi laser ini banyak sekali penggunaannya, manfaatnya, dan hasilnya lebih cepat dibandingkan penggunaan dengan produk-produk seperti krim, facial, atau perawatan klinik kecantikan saja," tuturnya.

Terapi Laser Siloam Hospitals Balikpapan

Laser yang digunakan oleh Siloam Hospitals Balikpapan ini memiliki kemampuan sinar yang masuk ke kulit yang paling dalam sehingga berguna menghilangkan pigmen dengan tingkat kedalaman yang maksimal.

Sementara itu penggunaan terapi laser turut digunakan untuk kasus seperti pigmen warna kulit yang biasa sangat mengganggu, misalnya keluhan flek UV atau hormonal di wajah yang umum disebabkan oleh faktor lingkungan dengan cuaca panas yang cukup dengan aktivitas yang dilakukan kebanyakan di luar ruangan/outdoor.

Adanya keluhan flek atau kelainan pigmen warna kulit bisa dibantu dengan menggunakan alat laser secara berkala yang saat ini sudah tersedia di Siloam Hospital Balikpapan.

Untuk kasus menghilangkan tatto perlu diketahui bahwa untuk menghilangkannya harus dilakukan dengan cara bertahap.

"Jadi ada beberapa warna pada tato yang sulit dihilangkan dengan laser dan harus dilakukan secara bertahap dan dilakukan beberapa evaluasi," ungkap dokter Arie"""

response = requests.post(url, data={"article": article})
print(response.json)
