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
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    
    yesterday = todays_date-datetime.timedelta(days=1)
    a_week_ago = todays_date-datetime.timedelta(days=7)
    #a_month_ago = todays_date-datetime.timedelta(days=30)
    a_year_ago = datetime.date(int(year), 1, 1)
   
    
    date_start_month = datetime.date(int(year), month, 1)
    Allincomes = UserIncome.objects.filter(owner=request.user)
    allexpenses = Expense.objects.filter(owner=request.user)


    amount_today = 0
    amount_yesterday = 0
    amount_a_week_ago = 0
    amount_a_month_ago = 0
    amount_year = 0
    allexpense = 0
    budgetAnuelle = 0


    CC = "Compte courant"
    EP =  "Epargne"
    list_EP_CC = {}

    incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=date_start_month, date__lte=todays_date)

    def get_category(income):
        return income.categories

    category_list = list(set(map(get_category, incomes)))
    
    def get_income_category_amount(category, capital):
        amount = 0
        filtered_by_category = capital.filter(categories=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount
        
    
    def manage_income(incomes, sum_CC, sum_EP):
        
        for income in incomes:
            if income.source == EP and income.categories == CC:
                sum_EP = sum_EP - income.amount
            elif income.source == CC and income.categories == EP:
                sum_CC = sum_CC - income.amount

        return {'sum_EP':sum_EP, 'sum_CC':sum_CC}
   


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
                                      date__gte=date_start_month, date__lte=todays_date)
    for expense in expenses_month:
        amount_a_month_ago += expense.amount


    expenses_year = Expense.objects.filter(owner=request.user,
                                      date__gte=a_year_ago, date__lte=todays_date)
    income_year = UserIncome.objects.filter(owner=request.user,
                                      date__gte=a_year_ago, date__lte=todays_date)
    for expense in expenses_year:
        amount_year += expense.amount

    
    #revenu annuelle total
    for income in income_year:
        budgetAnuelle += income.amount

    #dépsnes annuelle
    for exp in allexpenses:
        allexpense += exp.amount
        

    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')


    if CC in category_list and EP in category_list:
        sum_CC = get_income_category_amount(CC, Allincomes)
        sum_EP = get_income_category_amount(EP, Allincomes)
        list_EP_CC = manage_income(Allincomes, sum_CC, sum_EP)
        #finalrep[CC] = list_EP_CC['sum_CC']
        #finalrep[EP] = list_EP_CC['sum_EP']
        list_EP_CC['sum_CC'] = list_EP_CC['sum_CC'] - allexpense
    
    capital = list_EP_CC['sum_CC'] + list_EP_CC['sum_EP']



    context = {
        'expenses_today': "{:.1f}".format(amount_today),
        'expenses_yesterday':  "{:.1f}".format(amount_yesterday),
        'expenses_week': "{:.1f}".format(amount_a_week_ago),
        'expenses_month':"{:.1f}".format(amount_a_month_ago),
        'expenses_year': "{:.1f}".format(amount_year),
        'income_year': "{:.1f}".format(budgetAnuelle),
        'budgettotal': "{:.1f}".format(capital),
        'compte_courant': "{:.1f}".format(list_EP_CC['sum_CC']),
        'epargne': "{:.1f}".format(list_EP_CC['sum_EP']),
    }

    return render(request, 'expenses/dashboard_smDesktop.html', context)

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
    expenses = Expense.objects.filter(owner=request.user).order_by('-id')
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

    return render(request, 'expenses/index_smDesktop.html', context)

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
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    
   
    date_start_month = datetime.date(int(year), month, 1)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_month, date__lte=todays_date)    
    list_date_amount_tmp = {"Jan-"+str(year):"0", "Feb-"+str(year):"0", "Mar-"+str(year):"0", 
                    "Apr-"+str(year):"0", "May-"+str(year):"0", "Jun-"+str(year):"0", "Jul-"+str(year):"0", 
                    "Aug-"+str(year):"0", "Sep-"+str(year):"0", "Oct-"+str(year):"0", "Nov-"+str(year):"0", "Dec-"+str(year):"0"}
    
    if request.method == 'POST':        
        start = request.POST.get('startdate')
        end = request.POST.get('enddate')


        if start & end:
            expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=start, date__lte=end)     
            
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
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    
   
    date_start_month = datetime.date(int(year), month, 1)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_month, date__lte=todays_date)

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
        'date6ago':date_start_month,
        'todays_date':todays_date,
        'expenseGlobal': "{:.1f}".format(expenseGlobal),
        'expenses':expenses,
        'categories': categories,
        'currency': currency
    }

    
    return render(request, 'expenses/stats_smDesktop.html', context)




def export_pdf(request):

    if request.method == 'POST':
        hello = ""
        
    todays_date = datetime.date.today()
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    
    date_start_month = datetime.date(int(year), month, 1)
    incomes = UserIncome.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_month, date__lte=todays_date)
  
    response = HttpResponse(content_type='text/pdf')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
         str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
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