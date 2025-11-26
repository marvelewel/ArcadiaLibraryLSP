from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
import uuid

# Import model dan form
from .models import Buku, Peminjam, Peminjaman, DetilPeminjaman
from .forms import RegisterForm, FormPesanBuku, FormStatusPinjam

# ==============================================================================
# 1. LOGIKA AUTENTIKASI (LOGIN, REGISTER, LOGOUT)
# Mengatur siapa yang boleh masuk dan membedakan halaman berdasarkan Role.
# ==============================================================================

def login_view(request):
    # Jika user submit form login
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            # LOGIKA PEMISAHAN ROLE:
            # Admin (is_staff=True) -> Diarahkan ke Dashboard Admin
            # User Biasa -> Diarahkan ke Dashboard Peminjam
            if user.is_staff:
                return redirect('dashboard_admin')
            else:
                return redirect('dashboard_peminjam')
        else:
            messages.error(request, "Username atau Password salah.")
            
    return render(request, 'main/login.html')

def register_view(request):
    # Logika Pendaftaran Anggota Baru
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # ATOMIC TRANSACTION:
                # Menjamin data User dan Peminjam tersimpan bersamaan.
                # Jika salah satu gagal, semua dibatalkan (Rollback).
                with transaction.atomic():
                    # A. Buat User Login (Tabel auth_user)
                    user_baru = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password']
                    )
                    
                    # B. Buat Profil Peminjam (Tabel Peminjam)
                    peminjam = form.save(commit=False)
                    peminjam.user = user_baru
                    peminjam.save()
                    
                messages.success(request, "Registrasi berhasil! Silakan login.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {e}")
    else:
        form = RegisterForm()
    
    return render(request, 'main/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


# ==============================================================================
# 2. VIEW UNTUK ROLE PEMINJAM (USER)
# Halaman Dashboard, Riwayat, dan Form Pemesanan.
# ==============================================================================

@login_required
def dashboard_peminjam(request):
    # PROTEKSI: Jika Admin mencoba akses halaman ini, lempar ke Admin Panel
    if request.user.is_staff:
        return redirect('dashboard_admin')
        
    try:
        peminjam = request.user.peminjam
        # Mengambil riwayat transaksi user tersebut (diurutkan terbaru)
        riwayat = Peminjaman.objects.filter(peminjam=peminjam).order_by('-tgl_pesan')
        
        context = {
            'peminjam': peminjam,
            'riwayat': riwayat
        }
        return render(request, 'main/dashboard_peminjam.html', context)
    except Peminjam.DoesNotExist:
        # Fallback jika data profil korup/hilang
        return redirect('logout')

@login_required
def buat_pesanan(request):
    if request.method == 'POST':
        form = FormPesanBuku(request.POST)
        if form.is_valid():
            buku_list = form.cleaned_data['buku_dipilih']
            peminjam = request.user.peminjam
            
            # 1. Generate Kode Unik Transaksi (Format: P-XXXXXX)
            kode_unik = "P-" + uuid.uuid4().hex[:6].upper()
            
            with transaction.atomic():
                # 2. Simpan Header Transaksi
                transaksi = Peminjaman.objects.create(
                    kode_pinjam=kode_unik,
                    peminjam=peminjam,
                    status_pinjam='DIPROSES' # Status awal selalu Diproses
                )
                
                # 3. Simpan Detail Item (Looping setiap buku yang dipilih)
                for buku in buku_list:
                    DetilPeminjaman.objects.create(
                        peminjaman=transaksi,
                        buku=buku
                    )
            
            messages.success(request, "Pesanan berhasil dibuat! Tunggu persetujuan Admin.")
            return redirect('dashboard_peminjam')
    else:
        form = FormPesanBuku()
        
    return render(request, 'main/dashboard_peminjam.html', {'form_pesan': form, 'mode': 'pesan'})

@login_required
def kembalikan_buku_user(request, kode_pinjam):
    # FITUR PENGEMBALIAN MANDIRI
    # User bisa konfirmasi bahwa buku sudah dikembalikan.
    
    # 1. Cari data transaksi milik user tersebut
    try:
        transaksi = Peminjaman.objects.get(
            kode_pinjam=kode_pinjam, 
            peminjam=request.user.peminjam
        )
    except Peminjaman.DoesNotExist:
        messages.error(request, "Data tidak ditemukan.")
        return redirect('dashboard_peminjam')

    # 2. Validasi: Hanya boleh dikembalikan jika status sedang DISETUJUI (Dipinjam)
    if transaksi.status_pinjam == 'DISETUJUI':
        with transaction.atomic():
            # A. Update Status Transaksi jadi SELESAI
            transaksi.status_pinjam = 'SELESAI'
            transaksi.tgl_kembali = timezone.now().date()
            transaksi.save()
            
            # B. SINKRONISASI STOK: Buka kunci buku (tersedia=True)
            # Agar buku bisa dipinjam lagi oleh user lain.
            detail_items = DetilPeminjaman.objects.filter(peminjaman=transaksi)
            for item in detail_items:
                item.buku.tersedia = True 
                item.buku.save()
                
        messages.success(request, f"Terima kasih! Buku {kode_pinjam} berhasil dikembalikan.")
    else:
        messages.warning(request, "Transaksi ini tidak dapat dikembalikan (Status salah).")

    return redirect('dashboard_peminjam')


# ==============================================================================
# 3. VIEW UNTUK ROLE ADMIN (PENGELOLA)
# Dashboard Antrean, Validasi Pesanan, dan Manajemen Data Buku (CRUD).
# ==============================================================================

@login_required
def dashboard_admin(request):
    # PROTEKSI: Hanya Admin yang boleh masuk
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
        
    # Menampilkan semua data transaksi dari seluruh user
    daftar_pinjam = Peminjaman.objects.all().order_by('-tgl_pesan')
    return render(request, 'main/dashboard_admin.html', {'daftar_pinjam': daftar_pinjam})

@login_required
def detail_pesanan(request, kode_pinjam):
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
        
    obj_peminjaman = get_object_or_404(Peminjaman, kode_pinjam=kode_pinjam)
    list_buku_item = DetilPeminjaman.objects.filter(peminjaman=obj_peminjaman)
    
    if request.method == 'POST':
        form = FormStatusPinjam(request.POST)
        if form.is_valid():
            status_baru = form.cleaned_data['status']
            tgl_manual = form.cleaned_data['tgl_kembali_rencana'] # Tanggal input manual admin
            
            # Update Status dan Admin Penanggung Jawab
            obj_peminjaman.status_pinjam = status_baru
            obj_peminjaman.admin = request.user
            
            # SKENARIO 1: ADMIN MENYETUJUI
            if status_baru == 'DISETUJUI':
                if not tgl_manual:
                    messages.error(request, "Harap isi Tanggal Wajib Kembali jika menyetujui!")
                    return redirect('detail_pesanan', kode_pinjam=kode_pinjam)
                
                obj_peminjaman.tgl_ambil = timezone.now().date()
                obj_peminjaman.tgl_wajibkembali = tgl_manual
                
                # KUNCI STOK: Set buku jadi TIDAK TERSEDIA
                for item in list_buku_item:
                    item.buku.tersedia = False
                    item.buku.save()

            # SKENARIO 2: ADMIN MENOLAK / SELESAI
            elif status_baru == 'SELESAI' or status_baru == 'DITOLAK':
                if status_baru == 'SELESAI':
                    obj_peminjaman.tgl_kembali = timezone.now().date()
                
                # BUKA KUNCI STOK: Set buku jadi TERSEDIA kembali
                for item in list_buku_item:
                    item.buku.tersedia = True
                    item.buku.save()
                
            obj_peminjaman.save()
            messages.success(request, f"Status berhasil diubah menjadi {status_baru}")
            return redirect('dashboard_admin')
    else:
        form = FormStatusPinjam(initial={'status': obj_peminjaman.status_pinjam})
        
    context = {
        'peminjaman': obj_peminjaman,
        'list_buku': list_buku_item,
        'form': form
    }
    return render(request, 'main/detail_pesanan.html', context)

# --- MANAJEMEN MASTER DATA BUKU (CRUD) ---

@login_required
def kelola_buku(request):
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
        
    # Fitur CREATE: Tambah Buku Baru
    if request.method == 'POST':
        judul = request.POST.get('judul')
        pengarang = request.POST.get('pengarang')
        penerbit = request.POST.get('penerbit')
        tgl = request.POST.get('tgl_terbit')
        
        Buku.objects.create(
            judul_buku=judul, nama_pengarang=pengarang, 
            nama_penerbit=penerbit, tgl_terbit=tgl
        )
        messages.success(request, "Buku berhasil ditambahkan")
        return redirect('kelola_buku')

    # Fitur READ: Tampilkan Daftar Buku
    daftar_buku = Buku.objects.all()
    return render(request, 'main/kelola_buku.html', {'daftar_buku': daftar_buku})

@login_required
def hapus_buku(request, id_buku):
    # Fitur DELETE: Hapus Buku Permanen
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
        
    buku = get_object_or_404(Buku, id=id_buku)
    buku.delete()
    messages.success(request, "Buku berhasil dihapus")
    return redirect('kelola_buku')

@login_required
def edit_buku(request, id_buku):
    # Fitur UPDATE: Edit Informasi Buku
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
    
    buku = get_object_or_404(Buku, id=id_buku)
    
    if request.method == 'POST':
        buku.judul_buku = request.POST.get('judul')
        buku.nama_pengarang = request.POST.get('pengarang')
        buku.nama_penerbit = request.POST.get('penerbit')
        buku.tgl_terbit = request.POST.get('tgl_terbit')
        buku.save()
        messages.success(request, "Data buku berhasil diperbarui!")
        return redirect('kelola_buku')
        
    return render(request, 'main/edit_buku.html', {'buku': buku})

@login_required
def hapus_item_pesanan(request, id_detil):
    # Fitur Tambahan: Admin bisa menghapus 1 item buku dari pesanan user
    # Berguna jika salah satu buku stok fisiknya rusak/hilang.
    if not request.user.is_staff:
        return redirect('dashboard_peminjam')
    
    item = get_object_or_404(DetilPeminjaman, id=id_detil)
    kode_pinjam = item.peminjaman.kode_pinjam
    
    # Validasi: Hanya boleh hapus jika status masih DIPROSES
    if item.peminjaman.status_pinjam == 'DIPROSES':
        item.delete()
        messages.success(request, "Buku berhasil dihapus dari pesanan ini.")
    else:
        messages.error(request, "Tidak bisa menghapus buku karena status sudah bukan 'Diproses'.")
        
    return redirect('detail_pesanan', kode_pinjam=kode_pinjam)