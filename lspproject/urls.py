from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), # Admin bawaan Django
    path('', include('main.urls')),  # Arahkan ke aplikasi main
]

# Konfigurasi agar file gambar (media) bisa diakses lewat browser
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)