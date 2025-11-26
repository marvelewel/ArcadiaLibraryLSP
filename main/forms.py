from django import forms
from django.contrib.auth.models import User
from .models import Peminjam, Buku

# ==============================================================================
# 1. FORMULIR REGISTRASI (RegisterForm)
# Digunakan pada halaman Pendaftaran (Register).
# Menggabungkan pembuatan akun Login (User) dan data Profil (Peminjam).
# ==============================================================================
class RegisterForm(forms.ModelForm):
    # Field manual untuk tabel 'auth_user' (Login System)
    # Menggunakan widget PasswordInput agar karakter tersembunyi
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Menghubungkan form dengan Model 'Peminjam' untuk data profil
    class Meta:
        model = Peminjam
        fields = ['nama_peminjam', 'foto_peminjam']
        widgets = {
            # Styling Bootstrap untuk tampilan yang rapi
            'nama_peminjam': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_peminjam': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ==============================================================================
# 2. FORMULIR PEMESANAN BUKU (FormPesanBuku)
# Digunakan oleh Peminjam di Dashboard untuk memilih buku.
# Fitur Utama: Validasi Stok Otomatis.
# ==============================================================================
class FormPesanBuku(forms.Form):
    # Menggunakan ModelMultipleChoiceField agar user bisa memilih banyak buku (Checkbox)
    # LOGIKA PENTING: Queryset di-filter 'tersedia=True'.
    # Artinya, buku yang sedang dipinjam orang lain TIDAK AKAN MUNCUL di daftar ini.
    buku_dipilih = forms.ModelMultipleChoiceField(
        queryset=Buku.objects.filter(tersedia=True), 
        widget=forms.CheckboxSelectMultiple,
        label="Pilih Buku (Hanya buku tersedia yang tampil)"
    )

# ==============================================================================
# 3. FORMULIR VALIDASI ADMIN (FormStatusPinjam)
# Digunakan oleh Admin pada halaman Detail Pesanan.
# Fungsinya untuk mengubah status transaksi dan menentukan tanggal kembali.
# ==============================================================================
class FormStatusPinjam(forms.Form):
    # Pilihan status yang bisa diambil oleh Admin
    STATUS_CHOICES = [
        ('DISETUJUI', 'Setujui'),
        ('DITOLAK', 'Tolak'),
        ('SELESAI', 'Selesai (Dikembalikan)'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Input Tanggal Wajib Kembali
    # Field ini wajib diisi manual oleh Admin jika status = DISETUJUI.
    tgl_kembali_rencana = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Tgl Wajib Kembali (Wajib diisi jika Disetujui)"
    )