from django.contrib import admin
from .models import PDFUpload, PDFImage, UserProfile

@admin.register(PDFUpload)
class PDFUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username',)


@admin.register(PDFImage)
class PDFImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'pdf', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('pdf__user__username',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'download_count')
    search_fields = ('user__username',)
