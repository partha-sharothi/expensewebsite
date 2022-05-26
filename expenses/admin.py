from django.contrib import admin
from .models import Expense, Category

# Register your models here.


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner','category','date',)
    search_fields = ('description','category','date',)


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)