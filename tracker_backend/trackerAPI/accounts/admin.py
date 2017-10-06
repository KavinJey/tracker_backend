from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

# Register your models here.
class UserAdmin(UserAdmin):
    """
    UserAdmin, which controls the display of user values on administration panel
    """

    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'budget', )


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'category', 'type', 'value', 'currency', )


admin.site.register(User, UserAdmin)
admin.site.register(Expense, ExpenseAdmin)
