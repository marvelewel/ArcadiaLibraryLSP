# 📚 Arcadia Library Drive-Thru System

> **Sistem Informasi Manajemen Perpustakaan dengan Konsep Drive-Thru Modern.**
> *Efisiensi peminjaman buku tanpa antre, terintegrasi dengan validasi stok otomatis.*

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)
![Database](https://img.shields.io/badge/Database-Supabase_(PostgreSQL)-emerald.svg)

## 📖 Tentang Proyek

**Arcadia Library** adalah aplikasi web yang dirancang untuk memodernisasi proses peminjaman buku perpustakaan. Mengusung konsep **Drive-Thru**, anggota dapat memesan buku secara online, dan Admin akan menyiapkan buku tersebut untuk diambil tanpa peminjam harus turun dari kendaraan/mengantre lama.

Sistem ini menangani alur kerja (workflow) lengkap: mulai dari registrasi anggota, pemilihan buku, validasi admin, manajemen stok (penguncian otomatis saat dipinjam), hingga pengembalian.

---

## ✨ Fitur

### 👤 Panel Peminjam (User)
* **Modern Authentication:** Halaman Login & Register dengan desain *Split-Screen* dan validasi visual.
* **Dashboard Interaktif:** Melihat profil, status keanggotaan, dan statistik peminjaman pribadi.
* **Pemesanan Buku:** Memilih buku yang *Tersedia* menggunakan antarmuka *Card Selection* yang intuitif.
* **Riwayat Transaksi:** Memantau status pengajuan (Diproses, Disetujui, Ditolak, Selesai) secara *real-time*.
* **Self-Return:** Konfirmasi mandiri jika buku telah dikembalikan (opsional, tergantung kebijakan).

### 🛡️ Panel Admin (Petugas)
* **Control Center Dashboard:** Memantau antrean pesanan masuk dengan indikator visual.
* **Manajemen Pustaka (CRUD):** Tambah, Edit, dan Hapus data buku dengan formulir *Sticky Layout*.
* **Validasi Pesanan (Approval System):**
    * **Smart Stock Locking:** Saat Admin menyetujui (Approve) pesanan, stok buku otomatis terkunci (Tidak Tersedia) agar tidak bisa dipesan orang lain.
    * **Input Tanggal Kembali:** Menentukan tenggat waktu pengembalian saat validasi.
    * **Item Management:** Admin dapat menghapus sebagian buku dari pesanan jika stok fisik rusak/hilang.
* **Audit Trail:** Mencatat tanggal input buku secara otomatis.

---

## 🛠️ Teknologi yang Digunakan

* **Backend:** Python, Django Framework.
* **Database:** Supabase (PostgreSQL) - Cloud Database.
* **Frontend:** HTML5, CSS3, Bootstrap 5 (Soft UI Design).
* **Styling:** Custom CSS untuk animasi halus, *Glassmorphism*, dan *Responsive Layout*.
* **Icons:** FontAwesome 6.

---

## 🚀 Alur Logika Sistem (System Flow)

1.  **Pemesanan:** User memilih buku -> Status: `DIPROSES`.
2.  **Validasi:** Admin membuka detail pesanan.
    * Jika **DISETUJUI**: Admin input tanggal kembali -> Sistem mengunci buku (`tersedia=False`).
    * Jika **DITOLAK**: Transaksi batal -> Stok tetap aman.
3.  **Pengembalian:** Buku dikembalikan -> Status diubah ke `SELESAI` -> Sistem otomatis membuka kunci stok buku (`tersedia=True`) agar bisa dipesan user lain.

---

## 📸 Cuplikan Tampilan (Screenshots)

<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/fa01952a-3f72-4298-ad9c-a245a9161682" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/2c1420e3-0632-43e6-9a35-7172ee7e45e6" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/da912020-75e9-4c69-adbb-d3d0c93abdda" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/fede0360-0691-4f72-8939-ec997fef2395" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/6936471c-b001-4492-aec8-fbca5ed4dc21" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/19bc98e9-c81f-4a25-b905-01446d72cad2" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/f0313263-a83b-4e8f-924d-b4f182d72214" />


<img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/cb547d4c-a60a-47b3-a135-56dd32a2d448" />



---

## ⚙️ Cara Instalasi & Menjalankan (Localhost)

Ikuti langkah berikut untuk menjalankan proyek di komputer Anda:

1.  **Clone Repository** (atau extract folder project):
    ```bash
    git clone [https://github.com/username/arcadia-library.git](https://github.com/username/arcadia-library.git)
    cd arcadia-library
    ```

2.  **Aktifkan Virtual Environment (Disarankan):**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    
    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install django psycopg2-binary
    ```

4.  **Konfigurasi Database:**
    * Pastikan file `settings.py` sudah terhubung ke kredensial Supabase/PostgreSQL Anda.

5.  **Migrasi Database:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Buat Akun Admin (Superuser):**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Jalankan Server:**
    ```bash
    python manage.py runserver
    ```

8.  **Akses Aplikasi:**
    * Buka browser: `http://127.0.0.1:8000/`

---

## 👨‍💻 Author

Dibuat untuk memenuhi Tugas/Uji Kompetensi (LSP).
**Marvel Jeremia Putra Tjahyadi** - *Fullstack Django Developer*

---
*Copyright © 2025 Arcadia Library Drive-Thru System. All rights reserved.*
