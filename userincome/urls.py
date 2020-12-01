from django.urls import path
from . import views

from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="income"),
    path('add-income', views.add_income, name="add-income"),
    path('edit-income/<int:id>', views.income_edit, name="income-edit"),
    path('income-delete/<int:id>', views.delete_income, name="income-delete"),
    path('search-income', csrf_exempt(views.search_income),
         name="search_income"),
    path('income_category_summary', views.income_category_summary,
         name="income_category_summary"),
    path('instats', views.instats_view,
         name="instats"),
           path('iexport_csv', views.iexport_csv,
         name="iexport-csv"),
     path('iexport_excel', views.iexport_excel,
         name="iexport_excel"),
     path('iexport_pdf', views.iexport_pdf,
         name="iexport_pdf"),
]
