from django.contrib import admin
from .models import Expense, Category, Payment
# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):

    list_display = ('amount', 'description', 'owner', 'category', 'date', 'payment',)
    search_fields = ('description', 'category', 'date', 'payment',)

    list_per_page = 5


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)
admin.site.register(Payment)

