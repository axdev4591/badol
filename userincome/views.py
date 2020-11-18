from django.shortcuts import render, redirect
from .models import Source, UserIncome, Categories, Versements
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from expenses.models import Expense


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            categories__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            versements__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Categories.objects.all()
    versement = Versements.objects.all()
    source =  Source.objects.all()
    
    income = UserIncome.objects.filter(owner=request.user).order_by('-id')
    paginator = Paginator(income, 6)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie')
        return redirect('preferences')

    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index_smDesktop.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    categories = Categories.objects.all()
    versement = Versements.objects.all()
    source =  Source.objects.all()    
    
    context = {
        'source': source,
        'categorie': categories,
        'versement': versement,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']  
        versement = request.POST['versement']
        categorie = request.POST['category']


        if not amount:
            messages.error(request, 'Montant obligatoire')
            return render(request, 'income/add_income.html', context)
        elif amount.find(',') != -1:
            messages.error(request, 'Le montant est un nombre décimal, remplacez la virgule par un point svp')
            return render(request, 'income/add_income.html', context)
        
        if not date:
            messages.error(request, 'date obligatoire')
            return render(request, 'income/add_income.html', context)

        if not description:
            messages.error(request, 'description obligatoire')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, categories=categorie, versements=versement, description=description)
        messages.success(request, 'Votre revenu a été bien enregistré')
        

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    categories = Categories.objects.all()
    versements = Versements.objects.all()
    
    context = {
        'income': income,
        'values': income,
        'sources': sources,
        'categories': categories,
        'versements': versements
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        categorie = request.POST['categories']
        versement = request.POST['versements']
        if not amount:
            messages.error(request, 'Montant obligatoire')
            return render(request, 'income/edit_income.html', context)
        elif amount.find(',') != -1:
            messages.error(request, 'Le montant est un nombre décimal, remplacez la virgule par un point svp')
            return render(request, 'income/edit_income.html', context)

        if not description:
            messages.error(request, 'description obligatoire')
            return render(request, 'income/edit_income.html', context)

        income.amount = amount
        income. date = date
        income.source = source
        income.categories = categorie
        income.versements = versement
        income.description = description

        if not date:
            messages.error(request, 'date obligatoire')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income. date = date
        income.source = source
        income.categories = categorie
        income.versements = versement
        income.description = description

        income.save()
        messages.success(request, 'Record updated  successfully')

        return redirect('income')


def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Revenu supprimé')
    return redirect('income')


def income_category_summary(request):
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
    date_last_month3 = ""
    date_last_month4 = ""
  
    if month ==  1:
        date_last_month = datetime.date(int(year), 12, int(day))
        date_last_month3 = datetime.date(int(year), 11, int(day))
        date_last_month4 = datetime.date(int(year), 10, int(day))
    elif month == 2 :
        date_last_month = datetime.date(int(year), 1, int(day))
        date_last_month3 = datetime.date(int(year), 12, int(day))
        date_last_month4 = datetime.date(int(year), 11, int(day))
    elif month == 3 :
        date_last_month = datetime.date(int(year), 2, int(day))
        date_last_month3 = datetime.date(int(year), 1, int(day))
        date_last_month4 = datetime.date(int(year), 12, int(day))
    elif month == 4 :
        date_last_month = datetime.date(int(year), 3, int(day))
        date_last_month3 = datetime.date(int(year), 2, int(day))
        date_last_month4 = datetime.date(int(year), 1, int(day))
    else:
        date_last_month = datetime.date(int(year), int(month)-1, int(day))
        date_last_month3 = datetime.date(int(year), int(month)-2, int(day))
        date_last_month4 = datetime.date(int(year), int(month)-3, int(day))
    

    Solde = "Solde"
    income = 0
    expenses = 0
    last_income =0
    last_income3 = 0
    last_income4 = 0
    expense = 0
    last_expense = 0
    last_expense3 = 0
    last_expense4 = 0
    finalreponse = {}
    finalrep_expense = {}
    finalrep_income = {}

    this_month_incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=todays_date)
    last_month_incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month)

    last_month_incomes3 = UserIncome.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month3)
    last_month_incomes4 = UserIncome.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month4)



    this_month_expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=todays_date)
    last_month_expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month)

    last_month_expenses3 = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month3)
    last_month_expenses4 = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_year, date__lte=date_last_month4)

    Allexpenses = Expense.objects.filter(owner=request.user)
    Allincomes = UserIncome.objects.filter(owner=request.user)


    for item in this_month_incomes:
        income += item.amount

    for item in this_month_expenses:
        expenses += item.amount

    income = income - expenses

    for item in last_month_incomes:
        last_income += item.amount    

    for item in last_month_expenses:
        last_expense += item.amount

    last_income = last_income - last_expense

    for item in last_month_incomes3:
        last_income3 += item.amount    

    for item in last_month_expenses3:
        last_expense3 += item.amount
    
    last_income3 = last_income3 - last_expense3

    for item in last_month_incomes4:
        last_income4 += item.amount    

    for item in last_month_expenses4:
        last_expense4 += item.amount
    
    last_income4 = last_income4 - last_expense4

 
        
    """
    def manage_income(incomes, sum_CC, sum_EP):
        
        for income in incomes:
            if income.source == EP and income.categories == CC:
                sum_EP = sum_EP - income.amount
            elif income.source == CC and income.categories == EP:
                sum_CC = sum_CC - income.amount

        return {'sum_EP':sum_EP, 'sum_CC':sum_CC}
    
    """

    if request.method == 'POST':        
        start = request.POST.get('startdate')
        end = request.POST.get('enddate')
        finalrep = {}
        list_EP_CC = {}
             

        if start and end:
            incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=start, date__lte=end)     
            
            def get_category(income):
                return income.categories

            category_list = list(set(map(get_category, incomes)))


            def get_income_category_amount(category):
                amount = 0
                filtered_by_category = incomes.filter(categories=category)

                for item in filtered_by_category:
                    amount += item.amount
                return amount

            for x in incomes:
                for y in category_list:
                    finalrep[y] = get_income_category_amount(y)
            
            if CC in category_list and EP in category_list:
                sum_CC = get_income_category_amount(CC)
                sum_EP = get_income_category_amount(EP)
                list_EP_CC = manage_income(incomes)
                finalrep[CC] = list_EP_CC['sum_CC']
                finalrep[EP] = list_EP_CC['sum_EP']

        else:
            messages.success(request, 'Veuillez les champs date')
            instats_view(request)



        return JsonResponse({'income_data': finalrep}, safe=False)


    if request.method == 'GET':


        # check if solde calculate its income
        def get_category(income):
            return income.categories

        category_list_solde = list(set(map(get_category, Allincomes)))
        if Solde in category_list_solde:
            finalreponse["Solde {}".format(date_last_month4)] = float("{:.2f}".format(last_income4))
            finalreponse["Solde {}".format(date_last_month3)] = float("{:.2f}".format(last_income3))
            finalreponse["Solde {}".format(date_last_month)] = float("{:.2f}".format(last_income))
            finalreponse["Solde {}".format(date_this_month)] = float("{:.2f}".format(income))
            
            
           
        else:
            #income calculation
            def get_category(income):
                return income.categories

            category_list = list(set(map(get_category, Allincomes)))

            def get_income_category_amount(category):
                amount = 0
                filtered_by_category = Allincomes.filter(categories=category)

                for item in filtered_by_category:
                    amount += item.amount
                return amount

            for x in Allincomes:
                for y in category_list:
                    finalrep_income[y] = get_income_category_amount(y)
                

            #Expense calculation                
            def get_category(expense):
                return expense.category

            category_list_expense = list(set(map(get_category, Allexpenses)))


            def get_expense_category_amount(category):
                amount = 0
                filtered_by_category = Allexpenses.filter(category=category)

                for item in filtered_by_category:
                    amount += item.amount
                return amount

            for x in Allexpenses:
                for y in category_list_expense:
                    finalrep_expense[y] = get_expense_category_amount(y)

            
            for key, value in  finalrep_income.items():
                if key in finalrep_expense.keys():
                    finalreponse[key] = float("{:.2f}".format(value - finalrep_expense[key]))

       
        return JsonResponse({'income_data': finalreponse}, safe=False)


@login_required(login_url='/authentication/login')
def instats_view(request):
    todays_date = datetime.date.today()

    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
      
    
    date_start_month = datetime.date(int(year), month, 1)
    income = UserIncome.objects.filter(owner=request.user)
    Allexpenses = Expense.objects.filter(owner=request.user)

  

    categories = Categories.objects.all()
   
    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie avant tout usage de badol')
        return redirect('preferences')

    budget = 0
    for item in income:
        budget += item.amount

    expense = 0
    for item in Allexpenses:
        expense += item.amount
    budget = budget - expense
        
    context = {
        'budget': "{:.2f}".format(budget),
        'income': income,
        'categories': categories,
        'currency': currency
    }
    return render(request, 'income/incomeStats_smDesktop.html', context)




def iexport_pdf(request):
    response = HttpResponse(content_type='text/pdf')
    response['Content-Disposition'] = 'attachement; filename=BadolIncome' + \
         str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    todays_date = datetime.date.today()
    year = todays_date.strftime("%d-%b-%Y").split("-")[2]
    month = todays_date.strftime("%d-%b-%Y").split("-")[1]
    year_list = {"Jan":1, "Feb":2, "Mar":3, 
                    "Apr":4, "May":5, "Jun":6, "Jul":7, 
                    "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
    month = year_list[month]
    
    date_start_month = datetime.date(int(year), month, 1)
    incomes = UserIncome.objects.filter(owner=request.user, 
                                      date__gte=date_start_month, date__lte=todays_date)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date_start_month, date__lte=todays_date)

    sum = incomes.aggregate(Sum('amount'))
    buget1 = sum['amount__sum']
    sum = expenses.aggregate(Sum('amount'))
    budget = buget1 - sum['amount__sum']
    

    html_string = render_to_string('income/ipdf-output.html', {'incomes': incomes, 'total': "{:.1f}".format(budget)})
    html = HTML(string=html_string)
    result =  html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response


    

def iexport_excel(request):
    response = HttpResponse(content_type='text/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=BadolIncome' + \
         str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Depenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold=True

    columns = ['Montant', 'Source', 'Categorie', 'Mode de versement','Description', 'Date']

    for column in range(len(columns)):
        ws.write(row_num, column, columns[column], font_style)

    font_style = xlwt.XFStyle()

    rows = UserIncome.objects.filter(owner=request.user).values_list('amount','source', 'categories', 'versements', 'description', 'date')

    for row in rows:
        row_num += 1

        for column  in range(len(row)):
            ws.write(row_num, column, str(row[column]), font_style)

    wb.save(response)

    return response




def iexport_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename=BadolIncome' + \
         str(datetime.datetime.now()) + '.csv'

    writer =  csv.writer(response)
    writer.writerow(['Montant', 'Source', 'Categorie', 'Mode de versement','Description', 'Date'])

    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes :
        writer.writerow([income.amount, income.source, income.categories, income.versements, income.description, income.date])
    
    return response