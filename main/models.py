from django.db import models
from django.contrib.auth.models import User

# ==============================================================================
# 1. MODEL BUKU (Master Data)
# Menyimpan data koleksi perpustakaan.
# Fitur: Mencatat ketersediaan stok dan log kapan buku diinput.
# ==============================================================================
class Buku(models.Model):
    # Field Standar sesuai soal
    judul_buku = models.CharField(max_length=200, verbose_name="Judul Buku")
    tgl_terbit = models.DateField(verbose_name="Tanggal Terbit")
    nama_pengarang = models.CharField(max_length=100, verbose_name="Pengarang")
    nama_penerbit = models.CharField(max_length=100, verbose_name="Penerbit")
    
    # LOGIKA STOK:
    # Field ini digunakan untuk mengunci buku saat dipinjam.
    # True = Bisa dipinjam, False = Sedang dipinjam orang lain.
    tersedia = models.BooleanField(default=True)
    
    # AUDIT TRAIL:
    # Mencatat kapan data ini dibuat secara otomatis (auto_now_add).
    tgl_input = models.DateTimeField(auto_now_add=True, null=True) 

    def __str__(self):
        return self.judul_buku


# ==============================================================================
# 2. MODEL PEMINJAM (Profil Anggota)
# Menyimpan biodata anggota perpustakaan.
# Relasi: One-to-One dengan tabel User bawaan Django untuk keamanan Login.
# ==============================================================================
class Peminjam(models.Model):
    # Menghubungkan data profil dengan akun Login (Auth System Django)
    # Jika User dihapus, data Peminjam juga terhapus (CASCADE).
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    nama_peminjam = models.CharField(max_length=100)
    tgl_daftar = models.DateField(auto_now_add=True) # Otomatis isi tgl hari ini
    
    # Menyimpan file foto ke folder 'media/foto_peminjam/'
    foto_peminjam = models.ImageField(upload_to='foto_peminjam/', blank=True, null=True)
    
    # Pilihan Status Keanggotaan
    STATUS_CHOICES = [
        ('Aktif', 'Aktif'),
        ('Tidak Aktif', 'Tidak Aktif'),
    ]
    status_peminjam = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aktif')

    def __str__(self):
        return self.nama_peminjam


# ==============================================================================
# 3. MODEL PEMINJAMAN (Transaksi Header)
# Mencatat data utama transaksi peminjaman (Siapa, Kapan, Status).
# ==============================================================================
class Peminjaman(models.Model):
    # Kode unik transaksi (Primary Key logis untuk pencarian)
    kode_pinjam = models.CharField(max_length=20, unique=True)
    
    # RELASI KE PEMINJAM:
    # Mengetahui siapa member yang melakukan transaksi.
    peminjam = models.ForeignKey(Peminjam, on_delete=models.CASCADE)
    
    # RELASI KE ADMIN (VERIFIKATOR):
    # Mengetahui siapa Admin yang menyetujui/menolak.
    # null=True karena saat baru dibuat user, belum ada admin yang menyentuh.
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_verifikator')
    
    # MANAGEMEN TANGGAL:
    tgl_pesan = models.DateField(auto_now_add=True)        # Kapan user klik pesan
    tgl_ambil = models.DateField(null=True, blank=True)    # Kapan admin menyetujui
    tgl_wajibkembali = models.DateField(null=True, blank=True) # Batas waktu (diinput Admin)
    tgl_kembali = models.DateField(null=True, blank=True)  # Tanggal aktual pengembalian
    
    # STATUS TRANSAKSI (FLOW SYSTEM):
    STATUS_PINJAM_CHOICES = [
        ('DIPROSES', 'Diproses'),     # 1. User baru request
        ('DISETUJUI', 'Disetujui'),   # 2. Admin ACC (Stok buku dikunci)
        ('DITOLAK', 'Ditolak'),       # 2. Admin Tolak
        ('SELESAI', 'Selesai'),       # 3. Buku dikembalikan (Stok dibuka lagi)
    ]
    status_pinjam = models.CharField(max_length=20, choices=STATUS_PINJAM_CHOICES, default='DIPROSES')

    def __str__(self):
        return f"{self.kode_pinjam} - {self.peminjam.nama_peminjam}"


# ==============================================================================
# 4. MODEL DETIL PEMINJAMAN (Transaksi Item)
# Tabel perantara (Many-to-Many Resolver) karena 1 Transaksi bisa banyak Buku.
# ==============================================================================
class DetilPeminjaman(models.Model):
    # Mengaitkan ke Header Transaksi
    peminjaman = models.ForeignKey(Peminjaman, on_delete=models.CASCADE)
    
    # Mengaitkan ke Buku yang dipilih
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.peminjaman.kode_pinjam} : {self.buku.judul_buku}"