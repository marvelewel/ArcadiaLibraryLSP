from django.urls import path
from . import views

# ==============================================================================
# URL CONFIGURATION (ROUTING)
# File ini mengatur peta alamat website (URL) ke fungsi logika (Views).
# ==============================================================================

urlpatterns = [
    # ------------------------------------------------------------------
    # 1. OTENTIKASI & LANDING PAGE
    # Mengatur akses masuk dan keluar sistem.
    # Root URL ('') diarahkan langsung ke Login agar aman.
    # ------------------------------------------------------------------
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ------------------------------------------------------------------
    # 2. ROLE PEMINJAM (USER AREA)
    # Halaman-halaman yang hanya bisa diakses oleh member/peminjam.
    # ------------------------------------------------------------------
    # Dashboard: Melihat profil dan riwayat pinjam
    path('dashboard/', views.dashboard_peminjam, name='dashboard_peminjam'),
    # Pesan: Form untuk memilih dan mengajukan peminjaman buku
    path('pesan/', views.buat_pesanan, name='buat_pesanan'),
    # Fitur Pengembalian: User konfirmasi mandiri jika buku sudah dikembalikan
    path('kembalikan-mandiri/<str:kode_pinjam>/', views.kembalikan_buku_user, name='kembalikan_buku_user'),

    # ------------------------------------------------------------------
    # 3. ROLE ADMIN (CONTROL PANEL)
    # Halaman-halaman manajemen yang dilindungi otorisasi Admin (is_staff).
    # ------------------------------------------------------------------
    # Dashboard Admin: Melihat semua antrean pesanan masuk
    path('admin-panel/', views.dashboard_admin, name='dashboard_admin'),
    
    # Kelola Buku: Halaman CRUD (Create/Read) data master buku
    path('admin-panel/kelola-buku/', views.kelola_buku, name='kelola_buku'),

    # ------------------------------------------------------------------
    # 4. FITUR TRANSAKSI & VALIDASI (ADMIN)
    # URL Dinamis yang membutuhkan parameter ID atau Kode Unik.
    # ------------------------------------------------------------------
    # Detail Pesanan: Admin melihat rincian & melakukan persetujuan (Approve/Reject)
    # Menggunakan <str:kode_pinjam> untuk menangkap kode unik transaksi
    path('admin-panel/detail/<str:kode_pinjam>/', views.detail_pesanan, name='detail_pesanan'),
    
    # Hapus Item: Admin mengurangi/menghapus buku spesifik dari dalam pesanan
    path('admin-panel/hapus-item/<int:id_detil>/', views.hapus_item_pesanan, name='hapus_item_pesanan'),

    # ------------------------------------------------------------------
    # 5. MANAJEMEN DATA BUKU (UPDATE & DELETE)
    # Fitur lanjutan pengolahan data buku.
    # ------------------------------------------------------------------
    # Edit Buku: Mengubah informasi buku yang salah input
    path('admin-panel/edit-buku/<int:id_buku>/', views.edit_buku, name='edit_buku'),
    
    # Hapus Buku: Menghapus buku dari database (sesuai instruksi soal)
    path('admin-panel/hapus-buku/<int:id_buku>/', views.hapus_buku, name='hapus_buku'),
]