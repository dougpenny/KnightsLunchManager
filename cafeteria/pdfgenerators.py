import copy
import io

from typing import List

from reportlab import platypus
from reportlab.lib import enums
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from django.http import FileResponse
from django.utils import timezone


def orders_report_by_homeroom(todays_orders: List) -> FileResponse:
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    
    # create some styles and the base document
    normal_style = copy.copy(styles['Normal'])
    normal_style.fontSize = 12
    normal_style.leading = 14
    item_count_style = copy.copy(styles['Normal'])
    item_count_style.fontSize = 14
    item_count_style.leading = 16
    title_style = copy.copy(styles['Title'])
    title_style.fontSize = 26
    margin = inch * 0.5
    document = platypus.BaseDocTemplate(buffer, pagesize=letter, rightMargin=margin, leftMargin=margin, topMargin=margin, bottomMargin=margin)
    
    # create the title frame
    title_frame_height = inch * 0.5
    title_frame_bottom = document.height + document.bottomMargin - title_frame_height
    title_frame = platypus.Frame(document.leftMargin, title_frame_bottom, document.width - document.rightMargin, title_frame_height)
    frames = [title_frame]
    
    # create three frames to hold the list of orders for each item
    item_frame_height = inch * 2.0
    student_frame_height = title_frame_bottom - (inch * 2.25) - document.bottomMargin
    frame_width = document.width / 3.0
    for frame in range(3):
        left_margin = document.leftMargin + (frame * frame_width)
        column = platypus.Frame(left_margin, document.bottomMargin + item_frame_height, frame_width, student_frame_height, id='student-frame-{}'.format(frame))
        frames.append(column)
    
    # create a frame to hold the list of item totals
    column = platypus.Frame(document.leftMargin, document.bottomMargin, document.width, item_frame_height, id='item-frame')
    frames.append(column)

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
        title = teacher.user.last_name
        data.append(platypus.Paragraph(title, title_style))
        data.append(platypus.FrameBreak())
        for item in item_orders:
            content = [platypus.Paragraph('<b><u>{}</u></b>'.format(item.name), normal_style)]
            for student in item_orders[item]:
                content.append(platypus.Paragraph(student, normal_style))
            content.append(platypus.Paragraph('<br/><br/>', normal_style))
            data.append(platypus.KeepTogether(content))
        data.append(platypus.FrameBreak('item-frame'))
        data.append(platypus.HRFlowable())
        content = []
        for item in item_counts:
            content.append(platypus.Paragraph('{} - <b>{}</b>'.format(item.name, item_counts[item]), item_count_style))
        data.append(platypus.BalancedColumns(content, nCols = 2, topPadding=(0.25 * inch)))
        data.append(platypus.PageBreak())
    document.build(data)
    buffer.seek(0)
    today = timezone.now()
    report_name = 'class_orders_{}-{}-{}.pdf'.format(today.year, today.month, today.day)
    return FileResponse(buffer, as_attachment=True, filename=report_name)