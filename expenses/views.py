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
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum

from rest_framework import viewsets
from .serializers import ExpenseSerializer
import requests
from badolexpenses.settings import *


#Create API for expenses
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-date')
    serializer_class = ExpenseSerializer


#Geolocalization Api
def geoapi(request):


    is_cached = ('geodata' in request.session)

    if not is_cached:
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')
        params = {'access_key': IPSTACK_API_KEY}
        response = requests.get('http://api.ipstack.com/%s' % ip_address, params=params)
        request.session['geodata'] = response.json()

        print(f'response geoapi: {response.json()}')
    geodata = request.session['geodata']

    return render(request, 'expenses/geoapi.html', {
        'ip': geodata.get('ip'),
        'country': geodata.get('country_name', ''),
        'latitude': geodata.get('latitude', ''),
        'longitude': geodata.get('longitude', ''),
        'api_key': GOOGLE_MAPS_API_KEY,
        'is_cached': is_cached
    })


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
    Allincomes = UserIncome.objects.all()
    allexpenses = Expense.objects.all()


    amount_today = 0
    amount_yesterday = 0
    amount_a_week_ago = 0
    amount_a_month_ago = 0
    amount_year = 0
    allexpense = 0
    allbudget = 0
    income_year = 0

    list_EP_CC = {}

    incomes = UserIncome.objects.filter(
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
        
    """
    def manage_income(incomes, sum_CC, sum_EP):
        
        for income in incomes:
            if income.source == EP and income.categories == CC:
                sum_EP = sum_EP - income.amount
            elif income.source == CC and income.categories == EP:
                sum_CC = sum_CC - income.amount

        return {'sum_EP':sum_EP, 'sum_CC':sum_CC}
   
    """

    expenses_today = Expense.objects.filter(
                                      date__gte=todays_date, date__lte=todays_date)
    for expense in expenses_today:
        amount_today += expense.amount


    expenses_yesterday = Expense.objects.filter(
                                      date__gte=yesterday, date__lte=yesterday)
    for expense in expenses_yesterday:
        amount_yesterday += expense.amount


    expenses_week = Expense.objects.filter(
                                      date__gte=a_week_ago, date__lte=todays_date)
    for expense in expenses_week:
        amount_a_week_ago += expense.amount


    expenses_month = Expense.objects.filter(
                                      date__gte=date_start_month, date__lte=todays_date)
    for expense in expenses_month:
        amount_a_month_ago += expense.amount


    expenses_year = Expense.objects.filter(
                                      date__gte=a_year_ago, date__lte=todays_date)

    incomes_year = UserIncome.objects.filter(
                                      date__gte=a_year_ago, date__lte=todays_date)

    #revenu annuelle
    for el in incomes_year:
        income_year += el.amount
    #depsnes anuelle
    for expense in expenses_year:
        amount_year += expense.amount

    
    #revenu  total
    for income in Allincomes:
        allbudget += income.amount

    #dépsnes total
    for exp in allexpenses:
        allexpense += exp.amount
        

    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    
    capital = allbudget -  allexpense
    income_year = income_year

    #calcul de l'état financier
    etat = "certain"
    list_etat_financier = {}

    if capital >=  500:
        etat =  "Certain"
    elif capital <= 500 and capital >= 0:
        etat =  "Normal"
    elif capital < -100:
        etat =  "Chaotique"
    else:
        etat =  "Critique"

   
    context = {
        'expenses_today': "{:.1f}".format(amount_today),
        'expenses_yesterday':  "{:.1f}".format(amount_yesterday),
        'expenses_week': "{:.1f}".format(amount_a_week_ago),
        'expenses_month': "{:.1f}".format(amount_a_month_ago),
        'expenses_year': "{:.1f}".format(amount_year),
        'budgetannuelle': "{:.1f}".format(income_year),
        'compte_courant': "{:.1f}".format(capital),
        'etat' : etat
    }

    return render(request, 'expenses/dashboard_smDesktop.html', context)

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str) | Expense.objects.filter(
            date__istartswith=search_str) | Expense.objects.filter(
            description__icontains=search_str) | Expense.objects.filter(
            category__icontains=search_str) | Expense.objects.filter(
            payment__icontains=search_str)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    payment =  Payment.objects.all()
    todays_date = datetime.date.today()
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    day = todays_date.strftime("%d-%b-%Y").split("-")[0]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month] 
    date_this_month = datetime.date(int(year), int(month), int(day))
    date_start_year = datetime.date(int(year), 1, 1)
    date_last_month = ""
    date_last_month2 = ""
    date_last_month3 = ""
  
    if month ==  1:
        date_last_month = datetime.date(int(year), 12, int(day))
        date_last_month2 = datetime.date(int(year), 11, int(day))
        date_last_month3 = datetime.date(int(year), 10, int(day))
    elif month == 2 :
        date_last_month = datetime.date(int(year), 1, int(day))
        date_last_month2 = datetime.date(int(year), 12, int(day))
        date_last_month3 = datetime.date(int(year), 11, int(day))
    elif month == 3 :
        date_last_month = datetime.date(int(year), 2, int(day))
        date_last_month2 = datetime.date(int(year), 1, int(day))
        date_last_month3 = datetime.date(int(year), 12, int(day))
    elif month == 4 :
        date_last_month = datetime.date(int(year), 3, int(day))
        date_last_month2 = datetime.date(int(year), 2, int(day))
        date_last_month3 = datetime.date(int(year), 1, int(day))
    else:
        date_last_month = datetime.date(int(year), int(month)-1, int(day))
        date_last_month2 = datetime.date(int(year), int(month)-2, int(day))
        date_last_month3 = datetime.date(int(year), int(month)-3, int(day))

    expenses = Expense.objects.filter(date__gte=date_last_month3, date__lte=todays_date).order_by('-id')
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
    expenses = Expense.objects.filter(
                                      date__gte=date_start_month, date__lte=todays_date)
    """    
    list_date_amount_tmp = {"Jan-"+str(year):"0", "Feb-"+str(year):"0", "Mar-"+str(year):"0", 
                    "Apr-"+str(year):"0", "May-"+str(year):"0", "Jun-"+str(year):"0", "Jul-"+str(year):"0", 
                    "Aug-"+str(year):"0", "Sep-"+str(year):"0", "Oct-"+str(year):"0", "Nov-"+str(year):"0", "Dec-"+str(year):"0"}
    """
    if request.method == 'POST':        
        start = request.POST['startdate']
        end = request.POST['enddate']
        finalrep = {}


        if start and end:
            expenses = Expense.objects.filter(
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
                    finalrep[y] = float("{:.2f}".format(get_expense_category_amount(y)))
            
        #https://badol.herokuapp.com/stats
        if finalrep == {} :
            finalrep = {"Solde": 0}

        return JsonResponse({'expense_data': finalrep}, safe=False)


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
                finalrep[y] = float("{:.2f}".format(get_expense_category_amount(y)))
       
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
    expenses = Expense.objects.filter(
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


@csrf_exempt
def export_pdf(request):

   
    todays_date = datetime.date.today()
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    allexpense = 0
    
    date_start_month = datetime.date(int(year), month, 1)
    expenses = Expense.objects.filter(
                                    date__gte=date_start_month, date__lte=todays_date)

    if request.method == 'POST':
        data = request.body
        array1 = data.split(b'&')
        startAr = array1[0].decode("utf-8")
        endAr = array1[1].decode("utf-8")
        startAr = startAr.split('=')
        endAr = endAr.split('=')

        start = startAr[1]
        end = endAr[1]
        yearStart = start.split('-')[0]
        monthStart = start.split('-')[1]
        dayStart = start.split('-')[2]

        yearEnd = end.split('-')[0]
        monthEnd = end.split('-')[1]
        dayEnd = end.split('-')[2]


        start = datetime.date(int(yearStart), int(monthStart), int(dayStart))
        end = datetime.date(int(yearEnd), int(monthEnd), int(dayEnd))
     
          
        if end and start:
            expenses = Expense.objects.filter(
                                            date__gte=start, date__lte=end)
        

    response = HttpResponse(content_type='text/pdf')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
        str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    sum = expenses.aggregate(Sum('amount'))

    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    allexpense = "{:.2f}".format(sum['amount__sum'])
    allexpense = str(allexpense)+currency


    html_string = render_to_string('expenses/pdf-output.html', {'expenses': expenses, 'total':allexpense })
    html = HTML(string=html_string)
    result =  html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response


@csrf_exempt
def export_excel(request):
    response = HttpResponse(content_type='text/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=BadolExpenses' + \
         str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Depenses')
    row_num = 0
    allexpense = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True

    columns = ['Montant', 'Mode de paiement', 'Categorie','Description', 'Date']

    for column in range(len(columns)):
        ws.write(row_num, column, columns[column], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.values_list('amount','payment', 'category', 'description', 'date')
    if request.method == 'POST':
        data = request.body
        array1 = data.split(b'&')
        startAr = array1[0].decode("utf-8")
        
        endAr = array1[1].decode("utf-8")
        startAr = startAr.split('=')
        endAr = endAr.split('=')

        start = startAr[1]
        end = endAr[1]
        yearStart = start.split('-')[0]
        monthStart = start.split('-')[1]
        dayStart = start.split('-')[2]

        yearEnd = end.split('-')[0]
        monthEnd = end.split('-')[1]
        dayEnd = end.split('-')[2]


        start = datetime.date(int(yearStart), int(monthStart), int(dayStart))
        end = datetime.date(int(yearEnd), int(monthEnd), int(dayEnd))

            
        if end and start:
            rows = Expense.objects.filter(date__gte=start, date__lte=end).values_list('amount','payment', 'category', 'description', 'date')

    for row in rows:
        row_num += 1
        allexpense += row[0]
        for column  in range(len(row)):
            ws.write(row_num, column, str(row[column]), font_style)
    allexpense =  "{:.2f}".format(allexpense)


    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    allexpense = str(allexpense)+currency
    ws.write(row_num+3, 0, "DEPENSE TOTALE: ", font_style)
    ws.write(row_num+3, 1, allexpense, font_style)

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




#Extra code, to automate text messaging
"""
This has nothing to do with expense app, i just wanted to put it there, not to create a separate app juste for this task of scheduling text messages

"""

import random, schedule, time

from twilio.rest import Client


account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')


GOOD_MORNING_QUOTES = [
    "Bonjour! Bon reveil à toi <3",
    "Salut! La journéee s'annonce bien chez toi ? <3",
    "Bon reveil matinal!",
    "Bonjour soit benit"
]

GOOD_EVENING_QUOTES = [
    "Bonsoir ça été ta journée?",
    "Hello!",
    "Comment vas ?",
    "Bonsoir, quoi de neuf <3"
]


def send_message(quotes_list=GOOD_MORNING_QUOTES):

    account = account_sid
    token = auth_token
    client = Client(account, token)
    quote = quotes_list[random.randint(0, len(quotes_list)-1)]

    client.messages.create(to="+33768936922",
                           from_="+33758000973",
                           body=quote
                           )


# send a message in the morning
schedule.every().day.at("10:58").do(send_message, GOOD_MORNING_QUOTES)

# send a message in the evening
schedule.every().day.at("20:00").do(send_message, GOOD_EVENING_QUOTES)

# testing
schedule.every().day.at("19:26").do(send_message, GOOD_EVENING_QUOTES)


schedule.run_pending()
time.sleep(2)
