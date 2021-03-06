from contextvars import Context
import re
from unicodedata import category
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense 
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference

# Create your views here.

def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        # amount = request.POST['amount']
        # description = request.POST['description']
        # date = request.POST['expense_date']
        # category = request.POST['category']
        # # owner = request.POST[]

        expenses = Expense.objects.filter(amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith = search_str, owner=request.user) | Expense.objects.filter(
                description__icontains=search_str, owner=request.user) | Expense.objects.filter(
                    category__icontains=search_str, owner=request.user)
                    
        data = expenses.values()

        return JsonResponse(list(data), safe=False)




@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expense = Expense.objects.filter(owner = request.user)
    paginator = Paginator(expense, 2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'expenses': expense,
        'page_obj': page_obj,
        'currency': currency, 
    }
    return render(request, 'expenses/index.html',context)



@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'value': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expenses.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount: 
            messages.error(request, "Amount is required")
            return render(request, 'expenses/add_expenses.html', context)

        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        if not description: 
            messages.error(request, "Description is required")
            return render(request, 'expenses/add_expenses.html', context)

        # if not date: 
        #     messages.error(request, "Date is required")
        #     return render(request, 'expenses/add_expenses.html', context)

        # if not category: 
        #     messages.error(request, "Category is required")
        #     return render(request, 'expenses/add_expenses.html', context)

        Expense.objects.create(owner=request.user,amount=amount, date=date, 
                                        category=category, description=description)

        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')



@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
         
    }
    if request.method=='GET':
        return render(request, 'expenses/edit_expense.html',context)
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        expense.oner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()

        messages.success(request, 'Expense updated successfully')

        return redirect('expenses')


        # messages.info(request, 'Handling post form')
        # return render(request, 'expenses/edit_expenses.html',context)


@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')