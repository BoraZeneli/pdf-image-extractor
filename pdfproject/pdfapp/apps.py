from django.apps import AppConfig


class PdfappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdfapp'

# pdfapp/apps.py
def ready(self):
    import pdfapp.signals