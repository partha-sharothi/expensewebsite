from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        # amount = request.POST['amount']
        # description = request.POST['description']
        # date = request.POST['expense_date']
        # category = request.POST['category']
        # # owner = request.POST[]

        income = UserIncome.objects.filter(amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith = search_str, owner=request.user) | UserIncome.objects.filter(
                description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
                    source__icontains=search_str, owner=request.user)
                    
        data = income.values()

        return JsonResponse(list(data), safe=False)




@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner = request.user)
    paginator = Paginator(income, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency, 
    }
    return render(request, 'income/index.html',context)



@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'value': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount: 
            messages.error(request, "Amount is required")
            return render(request, 'income/add_income.html', context)

        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        if not description: 
            messages.error(request, "Description is required")
            return render(request, 'income/add_income.html', context)

        # if not date: 
        #     messages.error(request, "Date is required")
        #     return render(request, 'expenses/add_expenses.html', context)

        # if not category: 
        #     messages.error(request, "Category is required")
        #     return render(request, 'expenses/add_expenses.html', context)

        UserIncome.objects.create(owner=request.user,amount=amount, date=date, 
                                        source=source, description=description)

        messages.success(request, 'Record saved successfully')

        return redirect('income')




@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
         
    }
    if request.method=='GET':
        return render(request, 'income/edit_income.html',context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()

        messages.success(request, 'Record updated successfully')

        return redirect('income')


        # messages.info(request, 'Handling post form')
        # return render(request, 'expenses/edit_expenses.html',context)


@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record removed')
    return redirect('income')