import copy
import io
import logging
import os

from collections import Counter
from typing import Dict, Union
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, Sum
from django.db.models.query import QuerySet
from django.forms import formset_factory, modelformset_factory
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from constance import config

from reportlab import platypus
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from cafeteria.decorators import admin_access_allowed
from cafeteria.forms import GeneralForm, SchoolsModelForm, UserOrderForm
from cafeteria.models import LunchPeriod, School
from cafeteria.pdfgenerators import entree_report_by_period, lunch_card_for_users
from cafeteria.pdfgenerators import orders_report_by_homeroom, order_report_for_limited_items
from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import MenuLineItem
from transactions.models import Transaction


logger = logging.getLogger(__file__)
LIMITED_ITEMS_KEY = f'{timezone.localdate()}'


# Helper functions
def orders_for_homeroom(staff: Profile):
    orders = MenuLineItem.objects.filter(
        Q(transaction__transactee__in=staff.students.all())
        | Q(transaction__transactee=staff)
    ).filter(transaction__submitted__date=timezone.localdate())
    homeroom_orders = {
        'teacher': staff,
        'orders': orders
    }
    return homeroom_orders


def remove_soldout_items(items_count: Dict, queryset: QuerySet) -> QuerySet:
    filtered_queryset = queryset
    for item in queryset:
        if items_count.get(item.name, -1) >= item.max_num:
            filtered_queryset = filtered_queryset.exclude(name=item.name)
    return filtered_queryset


def todays_transaction(profile: Profile) -> Transaction:
    try:
        transactions = Transaction.objects.filter(
            transactee=profile,
            transaction_type=Transaction.DEBIT,
            submitted__date=timezone.localdate(),
        )
        return transactions.latest('submitted')
    except:
        return None


def item_limit_reached(item: MenuItem) -> bool:
    if item.limited:
        todays_orders = cache.get(f'{timezone.localdate()}')
        if not todays_orders:
            return False
        num_item_orders = todays_orders.get(item.name, -1)
        if num_item_orders >= item.max_num:
            return True
    return False


# Student/Staff views
@login_required
def delete_order(request):
    if request.method == 'POST':
        if Transaction.accepting_orders():
            transaction_id = request.POST.get('itemID')
            if transaction_id:
                transaction = Transaction.objects.get(id=transaction_id)
                try:
                    for menu_line_item in transaction.line_item.all():
                        if menu_line_item.menu_item.limited:
                            todays_limited_items = cache.get(f'{timezone.localdate()}')
                            if todays_limited_items:
                                limited_item_count = todays_limited_items.get(menu_line_item.menu_item.name)
                                if limited_item_count:
                                    todays_limited_items[menu_line_item.menu_item.name] = limited_item_count - menu_line_item.quantity
                                    cache.set(f'{timezone.localdate()}', todays_limited_items, timeout=None)
                    transaction.delete()
                    messages.success(
                        request, 'Your order was successfully deleted.')
                    return redirect('home')
                except Exception as e:
                    logger.exception(
                        f'An exception occured when trying to delete a transaction. {e}')
                    messages.error(
                        request, 'There was a problem deleting your order.')
                    return redirect('todays-order')
            else:
                messages.error(request, 'No order was found to delete.')
                return redirect('home')
        else:
            messages.warning(
                request, 'Sorry, your order is already being processed.')
            return redirect('home')
    return redirect('home')


def home(request):
    context = {}
    if config.CLOSED_FOR_SUMMER:
        context['closed'] = True
        return render(request, 'user/closed.html', context=context)

    context['orders_open'] = Transaction.accepting_orders()
    if request.user.is_authenticated:
        try:
            if request.user.profile.role == Profile.GUARDIAN:
                return redirect('guardian')
        except Exception as e:
            logger.exception(f'An exception occured for user {request.user}: {e}')
            return redirect('django_auth_adfs:logout')

        if todays_transaction(request.user.profile):
            return redirect('todays-order')

        context['user'] = request.user
        current_balance = request.user.profile.current_balance
        if current_balance <= -(config.DEBT_LIMIT):
            context['debt_exceeded'] = True
            context['debt_limit'] = config.DEBT_LIMIT
        context['balance'] = current_balance
        if request.method == 'POST':
            if context['orders_open']:
                OrderFormSet = formset_factory(UserOrderForm)
                formset = OrderFormSet(request.POST, prefix='order_form')
                if formset.is_valid():
                    ordered_items_list = []
                    for item in formset.cleaned_data:
                        try:
                            ordered_items_list.append(item['menu_item'])
                        except Exception as e:
                            logger.exception(f'An exception occured when an order was submitted: {e}')

                    if len(ordered_items_list) < 1:
                        messages.error(request, 'You must select at least one item.')
                        return redirect('home')
                    else:
                        counted_items = Counter(ordered_items_list)
                        description = ''
                        cost = 0
                        for item in counted_items:
                            if not item_limit_reached(item):
                                if description:
                                    description = description + ', '
                                description = description + f'({counted_items[item]}) {item.name}'
                                cost = cost + (item.cost * counted_items[item])
                            else:
                                messages.warning(request, f'{item.name} has already sold out. Please select a different item.')
                                return redirect('home')
                        if todays_transaction(request.user.profile):
                            messages.warning(request, 'Your have already placed an order today.')
                            return redirect('todays-order')
                        try:
                            transaction = Transaction(
                                amount=cost,
                                description=description,
                                transaction_type=Transaction.DEBIT,
                                transactee=request.user.profile
                            )
                            transaction.save()
                            for item in counted_items:
                                transaction.menu_items.add(item, through_defaults={'quantity': counted_items[item]})
                                todays_limited_items = cache.get(f'{timezone.localdate()}')
                                if todays_limited_items:
                                    todays_limited_items[item.name] = todays_limited_items.get(item.name, 0) + 1
                                    cache.set(f'{timezone.localdate()}', todays_limited_items)
                                else:
                                    todays_limited_items = {item.name: 1}
                                    cache.set(f'{timezone.localdate()}', todays_limited_items)
                            messages.success(request, 'Your order was successfully submitted.')
                            return redirect('todays-order')
                        except Exception as e:
                            logger.exception(f'An exception occured when trying to create a transaction: {e}')
                            messages.error(request, 'There was a problem submitting your order.')
                            return redirect('home')

        else:
            if request.user.profile.role == Profile.STAFF:
                if request.user.profile.students.all():
                    context['homeroom_teacher'] = True

            queryset = MenuItem.objects.filter(days_available__name=timezone.localdate().strftime("%A")).filter(app_only=False)
            todays_limited_items = cache.get(f'{timezone.localdate()}')
            if todays_limited_items:
                queryset = remove_soldout_items(todays_limited_items, queryset)
            context['menu_items'] = queryset.count()
            if request.user.profile.role == Profile.STUDENT:
                student_grade = request.user.profile.grade
                lunch_period = student_grade.lunch_period
                queryset = queryset.filter(lunch_period=lunch_period)
            else:
                queryset = queryset.filter(category=MenuItem.ENTREE)
            OrderFormSet = formset_factory(UserOrderForm)
            context['formset'] = OrderFormSet(form_kwargs={'queryset': queryset}, prefix='order_form')
    else:
        context['user'] = None
    return render(request, 'user/new_order.html', context=context)


@login_required
def submit_order(request):
    if request.method == 'POST':
        if Transaction.accepting_orders():
            if request.POST.__contains__('itemID'):
                if not todays_transaction(request.user.profile):
                    menu_item = MenuItem.objects.get(
                        id=request.POST.get('itemID'))
                    if menu_item not in MenuItem.objects.filter(days_available__name=timezone.localdate(timezone.now()).strftime("%A")):
                        logger.warning('{} attempted to order a {}, which is not available today.'.format(
                            request.user.profile.name, menu_item))
                        messages.error(
                            request, 'The {} is not available today. Please select from the available options.'.format(menu_item))
                        return redirect('home')
                    try:
                        transaction = Transaction(
                            amount=menu_item.cost,
                            description=menu_item.name,
                            transaction_type=Transaction.DEBIT,
                            transactee=request.user.profile
                        )
                        transaction.save()
                        transaction.menu_items.add(
                            menu_item, through_defaults={'quantity': 1})
                        messages.success(
                            request, 'Your order was successfully submitted.')
                        return redirect('todays-order')
                    except Exception as e:
                        logger.exception(
                            'An exception occured when trying to create a transaction: {}'.format(e))
                        messages.error(
                            request, 'There was a problem submitting your order.')
                        return redirect('home')
                else:
                    messages.warning(
                        request, 'You have already submitted an order today.')
                    return redirect('todays-order')
        else:
            messages.warning(
                request, 'Sorry, the cafeteria is no longer accepting orders today.')
            return redirect('home')
    else:
        return redirect('home')


# Guardian specific views
@login_required(login_url=('/oidc' + reverse('oidc_authentication_init', urlconf='mozilla_django_oidc.urls')))
def guardian_home(request):
    context = {}
    menu = MenuItem.objects.filter(
        days_available__name=timezone.localdate(timezone.now()).strftime("%A"))
    context['menu'] = menu
    context['orders_open'] = Transaction.accepting_orders()
    context['ps_url'] = os.getenv('POWERSCHOOL_URL')
    if request.user.is_authenticated:
        context['guardian'] = request.user
        guardian = Profile.objects.get(user=request.user)
        context['children'] = guardian.children.all()
    else:
        context['guardian'] = None
        context['children'] = None
    return render(request, 'guardian/guardian.html', context=context)


@login_required(login_url=('/oidc' + reverse('oidc_authentication_init', urlconf='mozilla_django_oidc.urls')))
def guardian_submit_order(request):
    if request.method == 'POST':
        print(request.POST)
        return redirect('guardian')

    # if request.method == 'POST':
    #     if Transaction.accepting_orders():
    #         if request.POST.__contains__('student'):
    #             for key in request.POST:
    #                 if key[:7] == 'student':
    #                     student = Profile.objects.get(key[8:])
    #                     if not todays_transaction(student):
    #                         menu_item = MenuItem.objects.get(
    #                             id=request.POST.get('itemID'))
    #                         if menu_item not in MenuItem.objects.filter(days_available__name=timezone.localdate(timezone.now()).strftime("%A")):
    #                             logger.warning('{} attempted to order a {}, which is not available today.'.format(
    #                                 request.user.profile.name, menu_item))
    #                             messages.error(
    #                                 request, 'The {} is not available today. Please select from the available options.'.format(menu_item))
    #                             return redirect('home')
    #                         try:
    #                             transaction = Transaction(
    #                                 amount=menu_item.cost,
    #                                 description=menu_item.name,
    #                                 transaction_type=Transaction.DEBIT,
    #                                 transactee=request.user.profile
    #                             )
    #                             transaction.save()
    #                             transaction.menu_items.add(
    #                                 menu_item, through_defaults={'quantity': 1})
    #                             messages.success(
    #                                 request, 'Your order was successfully submitted.')
    #                             return redirect('todays-order')
    #                         except Exception as e:
    #                             logger.exception(
    #                                 'An exception occured when trying to create a transaction: {}'.format(e))
    #                             messages.error(
    #                                 request, 'There was a problem submitting your order.')
    #                             return redirect('guardian')
    #                     else:
    #                         messages.warning(
    #                             request, 'You have already submitted an order today.')
    #                         return redirect('todays-order')
    #     else:
    #         messages.warning(
    #             request, 'Sorry, the cafeteria is no longer accepting orders today.')
    #         return redirect('guardian')
    else:
        return redirect('guardian')


def get_item_counts(orders: QuerySet[Transaction]) -> Dict:
    count = {}
    for order in orders:
        for line_item in order.line_item.all():
            if line_item.menu_item.category == MenuItem.ENTREE:
                if line_item.menu_item in count:
                    count[line_item.menu_item] = count[line_item.menu_item] + line_item.quantity
                else:
                    count[line_item.menu_item] = line_item.quantity
    return count


def get_limited_item_orders(orders: QuerySet[Transaction]) -> Union[Dict, None]:
    limited_order = {}
    for order in orders:
        for line_item in order.line_item.all():
            if line_item.menu_item.limited:
                current_orders = limited_order.get(line_item.menu_item, list())
                current_orders.append(order.transactee)
                limited_order[line_item.menu_item] = current_orders

    if len(limited_order) == 0:
        return None
    else:
        return limited_order


# Admin dashboard views
@login_required
@admin_access_allowed
def admin_dashboard(request):
    context = {}
    time = timezone.localtime()
    context['time'] = time
    context['user'] = request.user
    orders = Transaction.objects.filter(submitted__date=time.date())
    context['limited_item_orders'] = get_limited_item_orders(orders)
    context['total_item_counts'] = get_item_counts(orders)
    lunch_period_counts = {}
    for lunch_period in LunchPeriod.objects.all():
        lunch_period_counts[lunch_period] = get_item_counts(orders.filter(transactee__grade__lunch_period=lunch_period))
    staff_orders = orders.filter(transactee__grade=None).filter(transactee__role=Profile.STAFF)
    staff_period = LunchPeriod.objects.get(floating_staff=True)
    if staff_orders and staff_period:
        lunch_period_counts[staff_period] = staff_orders
    context['period_item_counts'] = lunch_period_counts
    context['orders'] = orders
    context['debtors'] = Profile.objects.filter(active=True).filter(current_balance__lt=0).order_by('current_balance', 'user__last_name')[:5]
    first_lunch = LunchPeriod.objects.filter(sort_order=0).first()
    context['first_lunch'] = first_lunch
    return render(request, 'admin/admin.html', context=context)


@login_required
@admin_access_allowed
def general_settings(request):
    if request.method == 'POST':
        general_form = GeneralForm(request.POST, prefix='general')
        if general_form.is_valid():
            form_data = general_form.cleaned_data
            config.OPEN_TIME = form_data['open_time']
            config.CLOSE_TIME = form_data['close_time']
            config.CURRENT_YEAR = form_data['current_year']
            config.CLOSED_FOR_SUMMER = form_data['closed_for_summer']
            config.REPORTS_EMAIL = form_data['reports_email']
            config.BALANCE_EXPORT_PATH = form_data['balance_export_path']
            config.NEW_CARD_FEE = form_data['new_card_fee']
            config.DEBT_LIMIT = form_data['debt_limit']
            messages.success(request, 'The general settings were successfully updated.')
        return redirect('general-settings')
    else:
        context = {}
        context['general_form'] = GeneralForm(prefix='general', initial={
            'open_time': config.OPEN_TIME,
            'close_time': config.CLOSE_TIME,
            'current_year': config.CURRENT_YEAR,
            'closed_for_summer': config.CLOSED_FOR_SUMMER,
            'reports_email': config.REPORTS_EMAIL,
            'balance_export_path': config.BALANCE_EXPORT_PATH,
            'new_card_fee': config.NEW_CARD_FEE,
            'debt_limit': config.DEBT_LIMIT,
        })
    return render(request, 'admin/general_settings.html', context=context)


@login_required
@admin_access_allowed
def schools_settings(request):
    SchoolsFormSet = modelformset_factory(School, form=SchoolsModelForm, extra=0)
    if request.method == 'POST':
        schools_form = SchoolsFormSet(request.POST, prefix='schools')
        if schools_form.is_valid():
            schools_form.save()
            messages.success(request, 'The school settings were successfully updated.')
        return redirect('schools-settings')
    else:
        context = {}
        context['schools_count'] = School.objects.count()
        context['schools_formset'] = SchoolsFormSet(prefix='schools')
    return render(request, 'admin/schools_settings.html', context=context)


def students_grouped_by_homeroom(staff: QuerySet[Profile], above_grade: int = -1):
    grouped = []
    no_homeroom = []
    for teacher in staff:
        if not teacher.grade:
            no_homeroom.append(teacher)
        else:
            students = teacher.students.all()
            if students and teacher.grade.value > above_grade:
                grouped.append(teacher)
                for student in students:
                    grouped.append(student)
            else:
                no_homeroom.append(teacher)
    grouped.extend(no_homeroom)
    return grouped


@login_required
@admin_access_allowed
def operations(request):
    if request.method == 'POST':
        if request.POST['action'] == 'print-cards':
            staff = Profile.objects.filter(role=Profile.STAFF).filter(active=True)
            if request.POST['group'] == 'NEW':  # No lunch card previously printed
                profiles = Profile.objects.filter(active=True)\
                    .exclude(pending=True).filter(cards_printed=0).filter(grade__value__gt=2)
            elif request.POST['group'] == 'STAFF':  # Staff without a Homeroom
                profiles = staff.filter(grade=None)
            elif request.POST['group'] == 'ALL':  # All Students & Staff
                profiles = students_grouped_by_homeroom(staff, 2)
            else:
                school = School.objects.get(id=request.POST['group'])
                staff = staff.filter(grade__in=school.grades.all())
                profiles = students_grouped_by_homeroom(staff, 2)
            if profiles:
                return lunch_card_for_users(profiles)
            else:
                messages.info(request, 'No users found to print cards for.')
        return redirect('operations')
    else:
        context = {}
        context['pending_count'] = Profile.objects.filter(pending=True).count()
        context['schools'] = School.objects.filter(active=True)
    return render(request, 'admin/operations.html', context=context)


@login_required
@admin_access_allowed
def homeroom_orders_report(request):
    todays_orders = []
    for staff in Profile.objects.filter(role=Profile.STAFF).order_by('grade', 'user__last_name'):
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
        title_frame_bottom = document.height + \
            document.bottomMargin - title_frame_height
        title_frame = platypus.Frame(
            document.leftMargin, title_frame_bottom, document.width, title_frame_height)
        frames.append(title_frame)
        for frame in range(2):
            left_margin = document.leftMargin + (frame * frame_width)
            column = platypus.Frame(left_margin, document.bottomMargin, frame_width,
                                    title_frame_bottom - (2 * inch), leftPadding=20, rightPadding=20, showBoundary=1)
            frames.append(column)
        template = platypus.PageTemplate(frames=frames)
        document.addPageTemplates(template)
        data = []
        for orders in todays_orders:
            teacher = orders['teacher']
            title = teacher.user.last_name + ' - ' + teacher.room
            data.append(platypus.Paragraph(title, title_style))
            if not teacher.grade:
                grade_level = 'Staff'
            else:
                grade_level = teacher.grade.display_name
            data.append(platypus.Paragraph(grade_level, grade_style))
            data.append(platypus.FrameBreak())
            order_groups = orders['orders'].values(
                'menu_item__short_name').annotate(sum=Sum('quantity'))
            for group in order_groups:
                data.append(platypus.Paragraph(
                    group['menu_item__short_name'], group_title_style))
                data.append(platypus.Paragraph(
                    str(group['sum']), group_count_style))
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


@login_required
@admin_access_allowed
def entree_orders_report(request):
    time = timezone.localtime(timezone.now())
    orders = Transaction.objects.filter(submitted__date=time.date())
    lunch_period_counts = {}
    for lunch_period in LunchPeriod.objects.all():
        lunch_period_counts[lunch_period] = get_item_counts(orders.filter(transactee__grade__lunch_period=lunch_period))
    staff_orders = orders.filter(transactee__grade=None).filter(transactee__role=Profile.STAFF)
    staff_period = LunchPeriod.objects.get(floating_staff=True)
    if staff_orders and staff_period:
        lunch_period_counts[staff_period] = staff_orders
    if lunch_period_counts:
        return entree_report_by_period(lunch_period_counts)
    else:
        messages.warning(request, 'No orders were found for today.')
        return redirect('admin')


@login_required
@admin_access_allowed
def limited_items_order_report(request, menu_item_id):
    limited_orders = {}
    orders = Transaction.objects.filter(submitted__date=timezone.localdate())
    for order in orders:
        for line_item in order.line_item.all():
            if line_item.menu_item.id == menu_item_id:
                current_orders = limited_orders.get(line_item.menu_item, list())
                current_orders.append(order)
                limited_orders[line_item.menu_item] = current_orders
    if limited_orders:
        return order_report_for_limited_items(limited_orders)
    else:
        messages.warning(request, 'No limited item orders were found for today.')
        return redirect('admin')


@login_required
@admin_access_allowed
def lunch_period_order_report(request, lunch_period_id):
    todays_orders = []
    lunch_period = LunchPeriod.objects.get(id=lunch_period_id)
    for staff in Profile.objects.filter(role=Profile.STAFF).filter(grade__lunch_period=lunch_period):
        class_order = orders_for_homeroom(staff)
        if class_order:
            todays_orders.append(class_order)
    if todays_orders:
        return orders_report_by_homeroom(todays_orders)
    else:
        messages.warning(request, 'No orders were found for today.')
        return redirect('admin')
