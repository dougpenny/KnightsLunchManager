from django.contrib import admin

from transactions.models import MenuLineItem
from transactions.models import Transaction


class LineItemInline(admin.TabularInline):
    model = MenuLineItem


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    fields = ['transactee', 'transaction_type', 'description', 'amount',
              'beginning_balance', 'ending_balance', 'submitted',
              'completed', 'ps_transaction_id']
    inlines = [LineItemInline, ]
    list_display = ('transactee', 'transaction_type',
                    'amount', 'submitted', 'status')
    ordering = ['submitted']
    readonly_fields = ['beginning_balance', 'ending_balance', 'ps_transaction_id', 'submitted']
    search_fields = ['description', 'transactee__user__first_name',
                     'transactee__user__last_name']
