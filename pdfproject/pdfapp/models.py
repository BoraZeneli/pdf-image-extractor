from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PDFUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PDF by {self.user.username} uploaded at {self.uploaded_at}"

class PDFImage(models.Model):
    pdf = models.ForeignKey(PDFUpload, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pdf_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for PDF {self.pdf.id}"

# ✅ Make sure this exists!
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    download_count = models.IntegerField(default=0)
    paid_downloads = models.BooleanField(default=False)  # ✅ Add this line

    def __str__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

# Optional signal to auto-create UserProfile on user creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
