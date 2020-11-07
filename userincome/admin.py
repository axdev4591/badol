from django.contrib import admin
from .models import UserIncome, Source, Categories, Versements
# Register your models here.

#class necessary to show models fiels in djando dashboard
class UserIncomeAdmin(admin.ModelAdmin):

    list_display = ('amount', 'description', 'owner', 'source', 'categories', 'date', 'versements',)
    search_fields = ('description', 'categories', 'source', 'date', 'versements',)

    list_per_page = 5


admin.site.register(UserIncome, UserIncomeAdmin)
admin.site.register(Source)
admin.site.register(Categories)
admin.site.register(Versements)

