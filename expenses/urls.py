from django.urls import path, include
from . import views
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

#The REST Framework router will make sure our requests end up at the right resource dynamically
#A router works with a viewset (see views.py above) to dynamically route requests
router = routers.DefaultRouter()
router.register(r'expenses', views.ExpenseViewSet)


urlpatterns = [
    path('expenses', views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expense"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense-delete/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses),
         name="search_expenses"),  
    path('expense_category_summary', views.expense_category_summary,
         name="expense_category_summary"),
    path('stats', views.stats_view,
         name="stats"),
     path('', views.home, name="home"),
     path('export_csv', views.export_csv,
         name="export-csv"),
     path('export_excel', views.export_excel,
         name="export-excel"),
     path('export_pdf', views.export_pdf,
         name="export_pdf"),
    
    # Wire up our API using automatic URL routing.
    # Additionally, we include login URLs for the browsable API.
    path('api', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')), #l'ajout du namespace cause des erreur de hyperlink, user-detail
    
    path('geoapi', views.geoapi,
         name="geoapi"),

]