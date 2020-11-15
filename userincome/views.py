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
    
    income = UserIncome.objects.filter(owner=request.user)
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
    return render(request, 'income/index.html', context)


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
    incomes = UserIncome.objects.filter(owner=request.user)
    

    if request.method == 'POST':        
        critere = request.POST.get('critere')
        filtre = request.POST.get('DateSince')


        if critere == "date":
            six_months_ago = todays_date-datetime.timedelta(days=30*6)
            incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)
            date_amount = {}
            list_date_amount = {}
            if filtre != '':
                if filtre.split("-")[0] != todays_date.strftime("%d-%b-%Y").split("-")[2]:
                    messages.error(request, 'Saisissez une date de cette année')
                incomes = UserIncome.objects.filter(owner=request.user,
                                      date__gte=filtre, date__lte=todays_date)
            
            def get_Date(income):
                return income.categories

            category_list = list(set(map(get_Date, incomes)))

                
            def get_income_category_amount(category):
                filtered_by_category = incomes.filter(categories=category)

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
                get_income_category_amount(cat)
            fill_date(date_amount)
            
        else:
            list_date_amount = {}
            if filtre != '':
                if filtre.split("-")[0] != todays_date.strftime("%d-%b-%Y").split("-")[2]:
                    messages.error(request, 'Saisissez une date de cette année')
                incomes = UserIncome.objects.filter(owner=request.user,
                                    date__gte=filtre, date__lte=todays_date)       
            
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
                    list_date_amount[y] = get_income_category_amount(y)

        return JsonResponse({'income_data': list_date_amount}, safe=False)


    if request.method == 'GET':
        
        finalrep = {}

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
        
        return JsonResponse({'income_data': finalrep}, safe=False)


@login_required(login_url='/authentication/login')
def instats_view(request):

    categories = Categories.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
   
    try:    
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        messages.success(request, 'Veuillez configurer votre monnaie avant tout usage de badol')
        return redirect('preferences')

    budget = 0
    for item in income:
        budget += item.amount
        
    context = {
        'budget': budget,
        'income': income,
        'categories': categories,
        'currency': currency
    }
    return render(request, 'income/incomeStats.html', context)




def iexport_pdf(request):
    response = HttpResponse(content_type='text/pdf')
    response['Content-Disposition'] = 'attachement; filename=BadolIncome' + \
         str(datetime.datetime.now()) + '.pdf'

    response['Content-Transfer-Encoding'] = 'binary'
    incomes = UserIncome.objects.filter(owner=request.user)
    sum = incomes.aggregate(Sum('amount'))

    html_string = render_to_string('income/ipdf-output.html', {'incomes': incomes, 'total': sum['amount__sum']})
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