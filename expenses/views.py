from django.contrib.auth.decorators import login_required
from .models import Expense, Category, Payment
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
from userincome.models import UserIncome
from django.views.decorators.csrf import csrf_exempt
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum



@login_required(login_url='/authentication/login')
def home(request):
    todays_date = datetime.date.today()
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    
    yesterday = todays_date-datetime.timedelta(days=1)
    a_week_ago = todays_date-datetime.timedelta(days=7)
    a_month_ago = todays_date-datetime.timedelta(days=30)
    a_year_ago = datetime.date(int(year), 1, 1)
    incomes = UserIncome.objects.filter(owner=request.user)

    amount_today = 0
    amount_yesterday = 0
    amount_a_week_ago = 0
    amount_a_month_ago = 0
    amount_year = 0
    budget = 0

    expenses_today = Expense.objects.filter(owner=request.user,
                                      date__gte=todays_date, date__lte=todays_date)
    for expense in expenses_today:
        amount_today += expense.amount


    expenses_yesterday = Expense.objects.filter(owner=request.user,
                                      date__gte=yesterday, date__lte=yesterday)
    for expense in expenses_yesterday:
        amount_yesterday += expense.amount


    expenses_week = Expense.objects.filter(owner=request.user,
                                      date__gte=a_week_ago, date__lte=todays_date)
    for expense in expenses_week:
        amount_a_week_ago += expense.amount


    expenses_month = Expense.objects.filter(owner=request.user,
                                      date__gte=a_month_ago, date__lte=todays_date)
    for expense in expenses_month:
        amount_a_month_ago += expense.amount


    expenses_year = Expense.objects.filter(owner=request.user,
                                      date__gte=a_month_ago, date__lte=todays_date)
    for expense in expenses_year:
        amount_year += expense.amount

    for income in incomes:
        budget += income.amount


    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    context = {
        'expenses_today': amount_today,
        'expenses_yesterday': amount_yesterday,
        'expenses_week': amount_a_week_ago,
        'expenses_month': amount_a_month_ago,
        'expenses_year': amount_year,
        'income': budget
    }

    return render(request, 'expenses/dashboard.html', context)

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



def export_pdf(request):
    response = HttpResponse(content_type='text/pdf')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
         str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string('expenses/pdf-output.html', {'expenses': expenses, 'total': sum['amount__sum']})
    html = HTML(string=html_string)
    result =  html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response


    

def export_excel(request):
    response = HttpResponse(content_type='text/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
         str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Depenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True

    columns = ['Montant', 'Mode de paiement', 'Categorie','Description', 'Date']

    for column in range(len(columns)):
        ws.write(row_num, column, columns[column], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount','payment', 'category', 'description', 'date')

    for row in rows:
        row_num += 1

        for column  in range(len(row)):
            ws.write(row_num, column, str(row[column]), font_style)

    wb.save(response)

    return response




def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
         str(datetime.datetime.now()) + '.csv'

    writer =  csv.writer(response)
    writer.writerow(['Montant', 'Mode de paiement', 'Categorie','Description', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses :
        writer.writerow([expense.amount, expense.payment, expense.category, expense.description, expense.date])
    
    return response