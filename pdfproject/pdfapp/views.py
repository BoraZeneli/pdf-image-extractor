import os
import zipfile
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import PDFUpload, PDFImage, UserProfile
import fitz  # PyMuPDF
from django.http import HttpResponseForbidden
from django.contrib import messages
from functools import wraps

# Dekorator për të kontrolluar limitin e shkarkimeve
def can_download(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.download_count >= 5 and profile.paid_downloads <= 0:
            messages.warning(request, "Ju keni përdorur të gjitha 5 shkarkimet falas. Ju lutemi kryeni një pagesë për të vazhduar.")
            return redirect('pay_before_download')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        pdf_upload = PDFUpload.objects.create(user=request.user, pdf_file=pdf_file)

        pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_file.name)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        doc = fitz.open(pdf_path)
        image_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_images')
        os.makedirs(image_dir, exist_ok=True)

        img_count = 0
        for page in doc:
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"{pdf_upload.id}_{img_count}.{image_ext}"
                image_path = os.path.join(image_dir, image_filename)

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                PDFImage.objects.create(
                    pdf=pdf_upload,
                    image=f"pdf_images/{image_filename}"
                )
                img_count += 1

        return redirect('select_images', pdf_id=pdf_upload.id)

    return render(request, 'upload.html')

@login_required
def select_images(request, pdf_id):
    images = PDFImage.objects.filter(pdf_id=pdf_id)
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_images')
        if selected_ids:
            request.session['selected_images'] = selected_ids
            return redirect('selected_images')
    return render(request, 'select_images.html', {'images': images})

@login_required
def selected_images(request):
    selected_ids = request.session.get('selected_images', [])
    if not selected_ids:
        return redirect('upload_pdf')

    images = PDFImage.objects.filter(id__in=selected_ids)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.download_count < 5 or profile.paid_downloads > 0:
        download_url = 'download_zip'
    else:
        cost = len(selected_ids) * 0.20  # 0.20 euro për foto
        request.session['payment_amount'] = f"{cost:.2f}"
        download_url = 'pay_before_download'

    return render(request, 'selected.html', {
        'images': images,
        'download_url': download_url
    })

@login_required
@can_download
def download_zip(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    selected_ids = request.session.get('selected_images', [])
    if not selected_ids:
        return redirect('upload_pdf')

    # Rris numrin e shkarkimeve falas ose të paguara
    if profile.download_count < 5:
        profile.download_count += 1
    else:
        profile.paid_downloads -= 1
    profile.save()

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image in PDFImage.objects.filter(id__in=selected_ids):
            image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
            if os.path.exists(image_path):
                zip_file.write(image_path, os.path.basename(image_path))

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=selected_images.zip'
    request.session['download_success'] = True
    return response

@login_required
def pay_before_download(request):
    amount = request.session.get('payment_amount', '0.00')
    client_id = settings.PAYPAL_CLIENT_ID
    return render(request, 'pay_before_download.html', {
        'amount': amount,
        'paypal_client_id': client_id
    })

@login_required
def download_zip_after_payment(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    paypal_payment_id = request.POST.get('paypal_payment_id')

    if not paypal_payment_id:
        messages.error(request, "Informacion pagese i pavlefshëm.")
        return redirect('pay_before_download')

    # Shto 5 shkarkime të paguara për 1 euro
    profile.paid_downloads += 5
    profile.save()

    selected_ids = request.session.get('selected_images', [])
    if not selected_ids:
        return redirect('upload_pdf')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image in PDFImage.objects.filter(id__in=selected_ids):
            image_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
            if os.path.exists(image_path):
                zip_file.write(image_path, os.path.basename(image_path))

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=paid_images.zip'
    request.session['download_success'] = True
    return response

@login_required
def download_success(request):
    if request.session.get('download_success'):
        del request.session['download_success']
        return render(request, 'download_success.html')
    return redirect('upload_pdf')

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_pdf')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_pdf')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login_user')

def payment_success(request):
    return render(request, 'payment_success.html')

def home(request):
    return redirect('upload_pdf')