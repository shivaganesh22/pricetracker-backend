from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(FCM)
admin.site.register(Alert)
admin.site.register(Verification)
admin.site.register(ForgotPassword)
admin.site.register(Contact)