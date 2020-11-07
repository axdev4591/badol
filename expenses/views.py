from django.contrib.auth.decorators import login_required
from .models import Expense, Category, Payment
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
import datetime
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='/authentication/login')
def home(request):
    return render(request, 'expenses/home.html')

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user) | Expense.objects.filter(
            payment__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    payment =  Payment.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'expenses/index.html', context)

@login_required(login_url='/authentication/login')
def add_expense(request):

    categories = Category.objects.all()
    payment = Payment.objects.all()
    context = {
        'categories': categories,
        'payments': payment,
        'values': request.POST,
        'date2d': datetime.date.today()
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        payment = request.POST['payment']


        if not amount:
            messages.error(request, 'Montant obligatoire')
            return render(request, 'expenses/add_expense.html', context)
        elif amount.find(',') != -1:
            messages.error(request, 'Le montant est un nombre décimal, remplacez la virgule par un point svp')
            return render(request, 'expenses/add_expense.html', context)


        if not description:
            messages.error(request, 'description obligatoire')
            return render(request, 'expenses/add_expense.html', context)

        if not date:
            messages.error(request, 'Date obligatoire')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user, amount=amount, date=date,
                               category=category, payment=payment, description=description)
        messages.success(request, 'Votre dépense a bien été enregistrée')

        return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    payments =  Payment.objects.all()

    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
        'payments': payments
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        payment = request.POST['payment']

        if not amount:
            messages.error(request, 'Montant obligatoire')
            return render(request, 'expenses/edit-expense.html', context)
        elif amount.find(',') != -1:
            messages.error(request, 'Le montant est un nombre décimal, remplacez la virgule par un point svp')
            return render(request, 'expenses/edit-expense.html', context)


        if not description:
            messages.error(request, 'Description obligatoire')
            return render(request, 'expenses/edit-expense.html', context)

        try:
            if not date:
                messages.error(request, 'La date est obligatoire')
                return render(request, 'expenses/edit-expense.html', context)
        except:
            messages.error(request, 'Oups. Avez-vous respecté le format de la date ? Veuillez recommencer')
            return render(request, 'expenses/edit-expense.html', context)


        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description
        expense.payment = payment

        expense.save()
        messages.success(request, 'Mis à jour réussi !')

        return redirect('expenses')

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Votre dépense a été bien supprimée !')
    return redirect('expenses')

#@csrf_exempt
def expense_category_summary(request):
    todays_date = datetime.date.today()
    expenses = Expense.objects.filter(owner=request.user)
    

    if request.method == 'POST':        
        critere = request.POST.get('critere')
        filtre = request.POST.get('DateSince')


        if critere == "date":
            six_months_ago = todays_date-datetime.timedelta(days=30*6)
            expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
            date_amount = {}
            list_date_amount = {}
            if filtre != '':
                if filtre.split("-")[0] != todays_date.strftime("%d-%b-%Y").split("-")[2]:
                    messages.error(request, 'Saisissez une date de cette année')
                expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=filtre, date__lte=todays_date)
            
            def get_Date(expense):
                return expense.category

            category_list = list(set(map(get_Date, expenses)))

                
            def get_expense_category_amount(category):
                filtered_by_category = expenses.filter(category=category)

                for item in filtered_by_category:
                            date = item.date
                            date = date.strftime("%d-%b-%Y")
                            date_amount[date] = item.amount
       

            def fill_date(date_amount):
                year = todays_date.strftime("%d-%b-%Y").split("-")[2]
                list_date_amount_tmp = {"Jan-"+str(year):"0", "Feb-"+str(year):"0", "Mar-"+str(year):"0", 
                    "Apr-"+str(year):"0", "May-"+str(year):"0", "Jun-"+str(year):"0", "Jul-"+str(year):"0", 
                    "Aug-"+str(year):"0", "Sep-"+str(year):"0", "Oct-"+str(year):"0", "Nov-"+str(year):"0", "Dec-"+str(year):"0"}


                for key in date_amount:                    
                    month = key.split('-')[1]
                    year = key.split('-')[2]
                    
                    amount =  0
                    for key in date_amount:
                        if month in key:
                            amount += date_amount[key]
                    for key in  list_date_amount_tmp:
                        if month in key :
                            list_date_amount_tmp[key] = amount

                for key, value in list_date_amount_tmp.items():
                    if list_date_amount_tmp[key] != "0":
                        list_date_amount[key] = value





            for cat in category_list:
                get_expense_category_amount(cat)
            fill_date(date_amount)
            
        else:
            list_date_amount = {}
            if filtre != '':
                if filtre.split("-")[0] != todays_date.strftime("%d-%b-%Y").split("-")[2]:
                    messages.error(request, 'Saisissez une date de cette année')
                expenses = Expense.objects.filter(owner=request.user,
                                    date__gte=filtre, date__lte=todays_date)       
            
            def get_category(expense):
                return expense.category

            category_list = list(set(map(get_category, expenses)))


            def get_expense_category_amount(category):
                amount = 0
                filtered_by_category = expenses.filter(category=category)

                for item in filtered_by_category:
                    amount += item.amount
                return amount

            for x in expenses:
                for y in category_list:
                    list_date_amount[y] = get_expense_category_amount(y)

        return JsonResponse({'expense_data': list_date_amount}, safe=False)


    if request.method == 'GET':
        
        finalrep = {}

        def get_category(expense):
            return expense.category

        category_list = list(set(map(get_category, expenses)))


        def get_expense_category_amount(category):
            amount = 0
            filtered_by_category = expenses.filter(category=category)

            for item in filtered_by_category:
                amount += item.amount
            return amount

        for x in expenses:
            for y in category_list:
                finalrep[y] = get_expense_category_amount(y)
        
        return JsonResponse({'expense_data': finalrep}, safe=False)

@login_required(login_url='/authentication/login')
def stats_view(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)

    expenses = Expense.objects.filter(owner=request.user)
    categories = Category.objects.all()
    
    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')
 
    expenseGlobal = 0
    for item in expenses:
        expenseGlobal += item.amount

    context = {
        'date6ago':six_months_ago,
        'todays_date':todays_date,
        'expenseGlobal':expenseGlobal,
        'expenses':expenses,
        'categories': categories,
        'currency': currency
    }

    
    return render(request, 'expenses/stats.html', context)
