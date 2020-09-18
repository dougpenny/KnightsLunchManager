import ast
import copy
import io
import logging
import os

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.http import FileResponse, HttpRequest
from django.shortcuts import redirect, render
from django.utils import timezone

from reportlab import platypus
from reportlab.lib import enums
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from lunchmanager.powerschool.powerschool import Powerschool
from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import MenuLineItem
from transactions.models import Transaction


logger = logging.getLogger(__file__)

def todays_transaction(profile: Profile) -> Transaction:
    try:
        transactions = Transaction.objects.filter(
            transactee=profile,
            transaction_type=Transaction.DEBIT,
            submitted__date=timezone.now().date(),
        )
        return transactions.latest('submitted')
    except:
        return None

@login_required
def delete_order(request):
    if request.method == 'POST':
        if Transaction.accepting_orders():
            transaction_id = request.POST.get('itemID')
            if transaction_id:
                transaction = Transaction.objects.get(id=transaction_id)
                try:
                    transaction.delete()
                    messages.success(request, 'Your order was successfully deleted.')
                    return redirect('home')
                except Exception as e:
                    logger.exception('An exception occured when trying to delete a transaction.')
                    messages.error(request, 'There was a problem deleting your order.')
                    return redirect('todays-order')
            else:
                messages.error(request, 'No order was found to delete.')
                return redirect('home')
        else:
            messages.warning(request, 'Sorry, your order is already being processed.')
            return redirect('home')
    return redirect('home')

def home(request):
    context = {}
    time = timezone.now()
    context['time'] = time
    menu = MenuItem.objects.filter(days_available__name=timezone.localtime(timezone.now()).date().strftime("%A"))
    context['menu'] = menu
    context['orders_open'] = Transaction.accepting_orders()
    if request.user.is_authenticated:
        context['user'] = request.user
        context['balance'] = request.user.profile.current_balance
        context['transaction'] = todays_transaction(request.user.profile)
        if request.user.profile.role == Profile.STAFF:
            if request.user.profile.students.all():
                context['homeroom_teacher'] = True
        if context['transaction']:
            return redirect('todays-order')
    else:
        context['user'] = None
    return render(request, 'web/user/user.html', context=context)

@login_required
def submit_order(request):
    if request.method == 'POST':
        if Transaction.accepting_orders():
            if request.POST.__contains__('itemID'):
                if not todays_transaction(request.user.profile):
                    menu_item = MenuItem.objects.get(id=request.POST.get('itemID'))
                    try:
                        transaction = Transaction(
                            amount=menu_item.cost,
                            description=menu_item.name,
                            transaction_type = Transaction.DEBIT,
                            transactee=request.user.profile
                        )
                        transaction.save()
                        transaction.menu_items.add(menu_item, through_defaults={'quantity': 1 })
                        messages.success(request, 'Your order was successfully submitted.')
                        return redirect('todays-order')
                    except Exception as e:
                        logger.exception('An exception occured when trying to create a transaction: {}'.format(e))
                        messages.error(request, 'There was a problem submitting your order.')
                        return redirect('home')
                else:
                    messages.warning(request, 'You have already submitted an order today.')
                    return redirect('todays-order')
        else:
            messages.warning(request, 'Sorry, the cafeteria is no longer accepting orders today.')
            return redirect('home')
    else:
        return redirect('home')

@login_required
def admin_dashboard(request):
    context = {}
    time = timezone.localtime(timezone.now())
    context['time'] = time
    context['user'] = request.user
    order_count = {}
    orders = Transaction.objects.filter(submitted__date=time.date())
    for order in orders:
        for line_item in order.line_item.all():
            if line_item.menu_item.name in order_count:
                order_count[line_item.menu_item.name] = order_count[line_item.menu_item.name] + line_item.quantity
            else:
                order_count[line_item.menu_item.name] = line_item.quantity
    context['order_count'] = order_count
    context['orders'] = orders
    return render(request, 'web/admin/admin.html', context=context)

def orders_for_homeroom(staff: Profile):
    orders = MenuLineItem.objects.filter(
        Q(transaction__transactee__in=staff.students.all())
        | Q(transaction__transactee=staff)
    ).filter(transaction__submitted__date=timezone.localdate(timezone.now()).date())
    if orders.count() == 0:
        return None
    else:
        homeroom_orders = {
            'teacher': staff,
            'orders': orders
        }
        return homeroom_orders

@login_required
def homeroom_orders_report(request):
    todays_orders = []
    for staff in Profile.objects.filter(role=Profile.STAFF).order_by('grade_level', 'user__last_name'):
        homeroom_order = orders_for_homeroom(staff)
        if homeroom_order:
            todays_orders.append(homeroom_order)
    if todays_orders:
        buffer = io.BytesIO()
        styles = getSampleStyleSheet()
        grade_style = copy.copy(styles['Title'])
        grade_style.fontSize = 28
        grade_style.spaceBefore = 26
        group_title_style = copy.copy(styles['Title'])
        group_title_style.fontSize = 34
        group_title_style.spaceAfter = 32
        group_count_style = copy.copy(styles['Title'])
        group_count_style.fontSize = 34
        group_count_style.spaceAfter = 46
        normal_style = styles['Normal']
        normal_style.fontSize = 12
        normal_style.leading = 16
        title_style = styles['Title']
        title_style.fontSize = 42
        document = platypus.BaseDocTemplate(buffer, pagesize=letter)
        frames = []
        frame_width = document.width / 2.0
        title_frame_height = 1.5 * inch
        title_frame_bottom = document.height + document.bottomMargin - title_frame_height
        title_frame = platypus.Frame(document.leftMargin, title_frame_bottom, document.width, title_frame_height)
        frames.append(title_frame)
        for frame in range(2):
            left_margin = document.leftMargin + (frame * frame_width)
            column = platypus.Frame(left_margin, document.bottomMargin, frame_width, title_frame_bottom - (2 * inch), leftPadding=20, rightPadding=20, showBoundary=1)
            frames.append(column)
        template = platypus.PageTemplate(frames=frames)
        document.addPageTemplates(template)
        data = []
        for orders in todays_orders:
            teacher = orders['teacher']
            title = teacher.user.last_name + ' - ' + teacher.room
            data.append(platypus.Paragraph(title, title_style))
            if not teacher.grade_level:
                grade_level = 'Staff'
            else:
                grade_level = 'Grade: ' + str(teacher.grade_level)
            data.append(platypus.Paragraph(grade_level, grade_style))
            data.append(platypus.FrameBreak())
            order_groups = orders['orders'].values('menu_item__short_name').annotate(sum=Sum('quantity'))
            for group in order_groups:
                data.append(platypus.Paragraph(group['menu_item__short_name'], group_title_style))
                data.append(platypus.Paragraph(str(group['sum']), group_count_style))
                for student in orders['orders'].filter(menu_item__short_name=group['menu_item__short_name']):
                    name = student.transaction.transactee.name()
                    data.append(platypus.Paragraph(name, normal_style))
                data.append(platypus.FrameBreak())
            if len(order_groups) < 2:
                data.append(platypus.FrameBreak())
        document.build(data)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='homeroom_orders.pdf')
    else:
        messages.warning(request, 'No orders were found for today.')
        return redirect('admin')