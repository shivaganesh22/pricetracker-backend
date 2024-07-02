from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
# Create your models here.
class FCM(models.Model):
    token=models.CharField(max_length=500,unique=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username+" "+self.token
class Alert(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=500)
    price=models.FloatField()
    slug=models.CharField(max_length=500)
    image=models.URLField()
    def __str__(self):
        return self.user.username+" "+self.slug
class Verification(models.Model):
    token=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    is_verified=models.BooleanField(default=False)
    def __str__(self):
        return self.user.username+" "+self.token
class ForgotPassword(models.Model):
    token=models.CharField(max_length=100)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    expire_date=models.DateTimeField(default=timezone.now() + timedelta(days=1))
    def __str__(self):
        return self.user.username+" "+self.token
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    subject=models.CharField(max_length=100)
    message=models.TextField()
    def __str__(self) :
        return self.name+"  "+self.subject
class ImageUpload(models.Model):
    img=models.ImageField(upload_to='images')