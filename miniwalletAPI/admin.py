from django.contrib import admin
from .models import Wallet, Customer, Transaction

# Register your models here.

admin.site.register(Wallet)
admin.site.register(Customer)
admin.site.register(Transaction)
