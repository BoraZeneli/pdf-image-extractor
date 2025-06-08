from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('select-images/<int:pdf_id>/', views.select_images, name='select_images'),
    path('selected-images/', views.selected_images, name='selected_images'),
    path('download-zip/', views.download_zip, name='download_zip'),
    path('download-success/', views.download_success, name='download_success'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('pay-before-download/', views.pay_before_download, name='pay_before_download'),
    path('download-after-payment/', views.download_zip_after_payment, name='download_zip_after_payment'),

]