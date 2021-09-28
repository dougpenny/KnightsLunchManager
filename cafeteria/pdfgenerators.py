import collections
import copy
import io

from pathlib import Path
from typing import Dict, List

from reportlab import platypus
from reportlab.graphics.barcode import qr
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm

from django.http import FileResponse
from django.utils import timezone

from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import MenuLineItem


def entree_report_by_period(lunch_periods: Dict) -> FileResponse:
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    
    # create some styles and the base document
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 26
    entree_style = copy.copy(styles['Normal'])
    entree_style.fontSize = 22
    entree_style.spaceAfter = 56
    entree_style.alignment = TA_CENTER
    staff_style = copy.copy(styles['Normal'])
    staff_style.fontSize = 22
    staff_style.spaceAfter = 24
    staff_style.alignment = TA_CENTER
    margin = 0.5*inch
    document = platypus.BaseDocTemplate(buffer, pagesize=letter, rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)

    # create the title frame
    title_frame_height = 0.5*inch
    title_frame_bottom = document.height + document.bottomMargin - title_frame_height
    title_frame = platypus.Frame(document.leftMargin, title_frame_bottom, document.width, title_frame_height)
    frames = [title_frame]
    
    # create a frame to hold entree counts
    frame = platypus.Frame(document.leftMargin, document.bottomMargin, document.width, document.height - title_frame_height - 1.0*inch, id='entree-frame')
    frames.append(frame)

    template = platypus.PageTemplate(frames=frames)
    document.addPageTemplates(template)

    data = []
    for period in lunch_periods:
        if len(lunch_periods[period]) > 0:
            title = period.display_name
            data.append(platypus.Paragraph('<u>{}</u>'.format(title), title_style))
            if not period.floating_staff:
                for item in lunch_periods[period]:
                    if item.pizza:
                        left_over_slices = lunch_periods[period][item] % item.slices_per
                        pizzas = lunch_periods[period][item] // item.slices_per
                        pizza_string = 'pizzas' if pizzas > 1 else 'pizza'
                        slice_string = 'slices' if left_over_slices > 1 else 'slice'
                        if left_over_slices == 0:
                            data.append(platypus.Paragraph('<u>{}</u><br/><br/><b>{}</b> {}'.format(item, pizzas, pizza_string), entree_style))
                        else:
                            data.append(platypus.Paragraph('<u>{}</u><br/><br/><b>{}</b> {}<br/><br/><b>{}</b> {}'.format(item, pizzas, pizza_string, left_over_slices, slice_string), entree_style))
                    else:
                        data.append(platypus.Paragraph('{} - <b>{}</b>'.format(item, lunch_periods[period][item]), entree_style))
                data.append(platypus.PageBreak())
            else:
                item_orders = {}
                for order in lunch_periods[period]:
                    staff = order.transactee.name()
                    line_item = MenuLineItem.objects.filter(transaction=order)
                    for item in line_item:
                        if item.quantity > 1:
                            staff = staff + ' ({})'.format(item.quantity)
                        if item.menu_item in item_orders:
                            item_orders[item.menu_item].append(staff)
                        else:
                            item_orders[item.menu_item] = [staff]
                item_orders = collections.OrderedDict(sorted(item_orders.items(), key=lambda menu_item: menu_item[0].sequence))
                for item in item_orders:
                    content = [platypus.Paragraph('<b><u>{}</u></b>'.format(item.name), staff_style)]
                    for staff in item_orders[item]:
                        content.append(platypus.Paragraph(staff, staff_style))
                    content.append(platypus.Paragraph('<br/><br/>', staff_style))
                    data.append(platypus.KeepTogether(content))
    document.build(data)
    buffer.seek(0)
    today = timezone.now()
    report_name = 'lunch_periods_{}-{}-{}.pdf'.format(today.year, today.month, today.day)
    return FileResponse(buffer, as_attachment=True, filename=report_name)


def lunch_card_for_users(profiles: List[Profile]) -> FileResponse:
    buffer = io.BytesIO()
    card_width = 86*mm
    card_height = 54*mm
    margin = 2*mm
    document = platypus.BaseDocTemplate(buffer, pagesize=(card_width, card_height), rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)

    styles = getSampleStyleSheet()
    normal_style = copy.copy(styles['Normal'])
    normal_style.fontSize = 16
    normal_style.leading = 18
    normal_style.alignment = TA_CENTER
    role_style = copy.copy(styles['Normal'])
    role_style.fontSize = 8
    role_style.leading = 8
    role_style.textTransform = 'uppercase'
    role_style.alignment = TA_CENTER
    small_style = copy.copy(styles['Heading2'])
    small_style.fontSize = 10
    small_style.leading = 10
    small_style.spaceBefore = 0
    small_style.spaceAfter = 0
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 20
    title_style.leading = 20
    title_style.spaceBefore = 0
    title_style.spaceAfter = 0

    qr_size = 37*mm
    top_offset = 4*mm
    role_height = 8*mm
    title_height = card_height - qr_size - top_offset
    
    frames = [platypus.Frame(document.leftMargin, card_height - title_height - top_offset, document.width, title_height, id="title-frame")]
    frames.append(platypus.Frame(document.leftMargin, document.bottomMargin, document.width - qr_size, qr_size, id="image-frame"))
    frames.append(platypus.Frame(document.leftMargin, document.bottomMargin, document.width - qr_size, qr_size, id="misc-frame"))
    frames.append(platypus.Frame(document.leftMargin, 0, 12*mm, 9*mm, id="number-frame"))
    frames.append(platypus.Frame(document.leftMargin, 0, document.width - qr_size, role_height, id="role-frame"))
    frames.append(platypus.Frame(card_width - qr_size, document.bottomMargin - margin, qr_size, qr_size, id="qr-frame"))
    template = platypus.PageTemplate(frames=frames)
    document.addPageTemplates(template)

    image_path = Path(__file__).resolve(strict=True).parent / 'report_images/knights-head.jpg'
    image = platypus.Image(image_path, width=30*mm, height=30*mm)

    data = []
    for profile in profiles:
        profile.cards_printed = profile.cards_printed + 1
        profile.save()
        name = platypus.Paragraph(profile.name(), title_style)
        data.append(platypus.KeepInFrame(card_width, title_height, content=[name]))
        data.append(platypus.FrameBreak('image-frame'))
        data.append(image)
        data.append(platypus.FrameBreak('misc-frame'))
        data.append(platypus.Paragraph('NRCA Cafeteria<br/>Lunch Card', normal_style))
        if profile.cards_printed > 1:
            data.append(platypus.FrameBreak('number-frame'))
            data.append(platypus.Paragraph('R{}'.format(profile.cards_printed), small_style))
        data.append(platypus.FrameBreak('role-frame'))
        data.append(platypus.Paragraph(profile.get_role_display(), role_style))
        data.append(platypus.FrameBreak('qr-frame'))
        data.append(qr.QrCode(str(profile.lunch_uuid), qrBorder=0))
        data.append(platypus.PageBreak())
    document.build(data)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='lunch_cards.pdf')


def orders_report_by_homeroom(todays_orders: List) -> FileResponse:
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    
    # create some styles and the base document
    normal_style = copy.copy(styles['Normal'])
    normal_style.fontSize = 12
    normal_style.leading = 14
    entree_count_style = copy.copy(styles['Normal'])
    entree_count_style.fontSize = 18
    entree_count_style.leading = 24
    item_count_style = copy.copy(styles['Normal'])
    item_count_style.fontSize = 14
    item_count_style.leading = 16
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 26
    margin = 0.5*inch
    bottom_margin = 0.25*inch
    document = platypus.BaseDocTemplate(buffer, pagesize=letter, rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=bottom_margin)
    
    # create the title frame
    title_frame_height = 0.5*inch
    title_frame_bottom = document.height + document.bottomMargin - title_frame_height
    title_frame = platypus.Frame(document.leftMargin, title_frame_bottom, document.width, title_frame_height)
    frames = [title_frame]
    
    # create a frame for a message when there are no orders
    no_orders_frame = platypus.Frame(document.leftMargin, document.height / 2.0, document.width, 1.0*inch, id='no-orders-frame')
    frames.append(no_orders_frame)

    # create three frames to hold the list of orders for each item
    entree_frame_height = 1.0*inch
    item_frame_height = 1.5*inch
    student_frame_height = title_frame_bottom - entree_frame_height - item_frame_height - document.bottomMargin
    frame_width = document.width / 3.0
    for frame in range(3):
        left_margin = document.leftMargin + (frame * frame_width)
        column = platypus.Frame(left_margin, document.bottomMargin + item_frame_height + entree_frame_height, frame_width, student_frame_height, id='student-frame-{}'.format(frame))
        frames.append(column)
    
     # create a frame for a horizontal divider
    frame = platypus.Frame(document.leftMargin, document.bottomMargin + item_frame_height + entree_frame_height, document.width, 0.25*inch, id='divider-frame')
    frames.append(frame)

    # create two frames to hold the entree item totals
    frame_width = document.width / 2.0
    for frame in range(2):
        left_margin = document.leftMargin + (frame * frame_width)
        column = platypus.Frame(left_margin, item_frame_height + document.bottomMargin, frame_width, entree_frame_height, id='entree-frame-{}'.format(frame))
        frames.append(column)

    # create a frame to hold the list of item totals
    frame = platypus.Frame(document.leftMargin, document.bottomMargin, document.width, item_frame_height, id='item-frame')
    frames.append(frame)

    template = platypus.PageTemplate(frames=frames)
    document.addPageTemplates(template)
    
    data = []
    for orders in todays_orders:
        item_orders = {}
        item_counts = {}
        teacher = orders['teacher']
        for item in orders['orders']:
            student = item.transaction.transactee.name()
            if item.quantity > 1:
                student = student + ' ({})'.format(item.quantity)
            if item.menu_item in item_orders:
                item_orders[item.menu_item].append(student)
            else:
                item_orders[item.menu_item] = [student]
            if item.menu_item in item_counts:
                item_counts[item.menu_item] = item_counts[item.menu_item] + item.quantity
            else:
                item_counts[item.menu_item] = item.quantity
        item_orders = collections.OrderedDict(sorted(item_orders.items(), key=lambda menu_item: menu_item[0].sequence))
        item_counts = collections.OrderedDict(sorted(item_counts.items(), key=lambda menu_item: menu_item[0].sequence))
        title = teacher.user.last_name
        data.append(platypus.Paragraph('<u>{}</u>'.format(title), title_style))
        if len(item_orders) > 0:
            data.append(platypus.FrameBreak('student-frame-0'))
            for item in item_orders:
                content = [platypus.Paragraph('<b><u>{}</u></b>'.format(item.name), normal_style)]
                for student in item_orders[item]:
                    content.append(platypus.Paragraph(student, normal_style))
                content.append(platypus.Paragraph('<br/><br/>', normal_style))
                data.append(platypus.KeepTogether(content))
            data.append(platypus.FrameBreak('divider-frame'))
            data.append(platypus.HRFlowable())
            data.append(platypus.FrameBreak('entree-frame-0'))
            item_content = []
            for item in item_counts:
                if item.category == MenuItem.ENTREE:
                    data.append(platypus.Paragraph('{} - <b>{}</b>'.format(item.short_name, item_counts[item]), entree_count_style))
                else:
                    item_content.append(platypus.Paragraph('{} - <b>{}</b>'.format(item.name, item_counts[item]), item_count_style))
            data.append(platypus.FrameBreak('item-frame'))
            if item_content:
                data.append(platypus.BalancedColumns(item_content, nCols = 2))
        else:
            data.append(platypus.FrameBreak('no-orders-frame'))
            data.append(platypus.Paragraph('No Orders Today', title_style))
        data.append(platypus.PageBreak())
    document.build(data)
    buffer.seek(0)
    today = timezone.now()
    report_name = 'class_orders_{}-{}-{}.pdf'.format(today.year, today.month, today.day)
    return FileResponse(buffer, as_attachment=True, filename=report_name)