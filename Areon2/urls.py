from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админ-панель
    path('admin/', admin.site.urls),
    
    # Главное приложение (все маршруты из main/urls.py)
    path('', include('main.urls')),
]

# Для загрузки медиа-файлов (изображения, документы) в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)