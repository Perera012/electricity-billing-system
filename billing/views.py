from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from .forms import MeterReadingForm
from .models import MeterReading, Bill, Payment
from .utils import calculate_bill
import hashlib
from decimal import Decimal

def home(request):
    return render(request, 'billing/home.html')

@login_required
def add_meter_reading(request):

    # Get user's latest reading
    last_reading = MeterReading.objects.filter(
        user=request.user
    ).order_by(
        '-reading_date',
        '-id'
    ).first()

    if request.method == 'POST':

        form = MeterReadingForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            meter_reading = form.save(
                commit=False
            )

            # Check duplicate month

            existing = Bill.objects.filter(
                user=request.user,
                meter_reading__month=meter_reading.month
            ).exists()

            if existing:

                return render(
                    request,
                    'billing/add_meter_reading.html',
                    {
                        'form': form,
                        'last_reading': last_reading,
                        'error': 'Bill already exists for this month.'
                    }
                )

            meter_reading.user = request.user

            # Auto set previous reading

            if last_reading:

                meter_reading.previous_reading = (
                    last_reading.current_reading
                )

            else:

                meter_reading.previous_reading = 0

            # Validate current reading

            if (
                meter_reading.current_reading <=
                meter_reading.previous_reading
            ):

                return render(
                    request,
                    'billing/add_meter_reading.html',
                    {
                        'form': form,
                        'last_reading': last_reading,
                        'error':
                        f'Current reading must be greater than the previous reading ({meter_reading.previous_reading}).'
                    }
                )

            # Calculate units used

            meter_reading.units_used = (
                meter_reading.current_reading -
                meter_reading.previous_reading
            )

            meter_reading.save()

            total_amount = calculate_bill(
                meter_reading.units_used
            )

            Bill.objects.create(
                user=request.user,
                meter_reading=meter_reading,
                total_amount=total_amount,
                bill_status='Unpaid'
            )

            return redirect(
                'bill_history'
            )

    else:

        form = MeterReadingForm()

    return render(
        request,
        'billing/add_meter_reading.html',
        {
            'form': form,
            'last_reading': last_reading
        }
    )


@login_required
def bill_history(request):

    search = request.GET.get('search')

    bills = Bill.objects.filter(
        user=request.user
    )

    if search:
        bills = bills.filter(
            meter_reading__month__icontains=search
        )

    bills = bills.order_by('-created_at')

    return render(
        request,
        'billing/bill_history.html',
        {
            'bills': bills,
            'search': search
        }
    )

@login_required
def bill_detail(request, bill_id):

    bill = Bill.objects.get(
        id=bill_id,
        user=request.user
    )

    return render(
        request,
        'billing/bill_detail.html',
        {'bill': bill}
    )

@login_required
def make_payment(request, bill_id):

    bill = Bill.objects.get(
        id=bill_id,
        user=request.user
    )

    merchant_id = "1236737"

    merchant_secret = "MTM5OTkzMjk3NTQyNDYxNjk0ODcxNTk2MzI3Nzk2MjU4MTc3NjUzMg=="

    order_id = order_id = str(bill.id)

    amount = format(
        Decimal(bill.total_amount),
        ".2f"
    )

    currency = "LKR"

    hashed_secret = hashlib.md5(
        merchant_secret.encode()
    ).hexdigest().upper()

    hash_value = hashlib.md5(
        (
            merchant_id +
            order_id +
            amount +
            currency +
            hashed_secret
        ).encode()
    ).hexdigest().upper()

    print("Merchant ID:", merchant_id)
    print("Order ID:", order_id)
    print("Amount:", amount)
    print("Currency:", currency)

    
    return render(
        request,
        'billing/payment_page.html',
        {
            'bill': bill,
            'hash': hash_value,
            'order_id': order_id
        }
    )

@login_required
def payment_history(request):

    payments = Payment.objects.filter(
        user=request.user
    ).order_by('-payment_date')

    return render(
        request,
        'billing/payment_history.html',
        {'payments': payments}
    )


@staff_member_required
def admin_dashboard(request):

    total_users = User.objects.count()

    total_bills = Bill.objects.count()

    paid_bills = Bill.objects.filter(
        bill_status="Paid"
    ).count()

    unpaid_bills = Bill.objects.filter(
        bill_status="Unpaid"
    ).count()

    total_revenue = sum(
        payment.bill.total_amount
        for payment in Payment.objects.all()
    )

    context = {
        'total_users': total_users,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
        'total_revenue': total_revenue,
    }

    return render(
        request,
        'billing/admin_dashboard.html',
        context
    )

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.conf import settings
import os


@login_required
def download_bill(request, bill_id):

    bill = Bill.objects.get(
        id=bill_id,
        user=request.user
    )

    reading = bill.meter_reading

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="Bill_{bill.id}.pdf"'
    )

    p = canvas.Canvas(response)



    logo_path = os.path.join(
        settings.BASE_DIR,
        'billing',
        'static',
        'images',
        'logo.png'
    )

    if os.path.exists(logo_path):
        p.drawImage(
            logo_path,
            40,
            740,
            width=60,
            height=60
        )

   

    p.setFont("Helvetica-Bold", 20)
    p.drawString(
        120,
        770,
        "Smart Electricity Billing System"
    )

    p.setStrokeColor(colors.darkred)
    p.line(40, 730, 550, 730)

  
    p.setFont("Helvetica-Bold", 12)

    p.drawString(40, 700, f"Bill Number:")
    p.drawString(150, 700, f"#{bill.id}")

    p.drawString(40, 675, "Generated Date:")
    p.drawString(
        150,
        675,
        bill.created_at.strftime("%d-%m-%Y")
    )

 

    p.setFillColor(colors.lightgrey)
    p.rect(40, 600, 500, 50, fill=1)

    p.setFillColor(colors.black)

    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 630, "Customer Information")

    p.setFont("Helvetica", 12)

    p.drawString(
        50,
        610,
        f"Customer Name: {bill.user.username}"
    )

    p.drawString(
        300,
        610,
        f"Month: {reading.month}"
    )


    p.setFillColor(colors.lightgrey)
    p.rect(40, 470, 500, 100, fill=1)

    p.setFillColor(colors.black)

    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 550, "Meter Reading Details")

    p.setFont("Helvetica", 12)

    p.drawString(
        50,
        525,
        f"Previous Reading: {reading.previous_reading}"
    )

    p.drawString(
        50,
        500,
        f"Current Reading: {reading.current_reading}"
    )

    p.drawString(
        50,
        475,
        f"Units Used: {reading.units_used}"
    )

  
    p.setFillColor(colors.lightgrey)
    p.rect(40, 340, 500, 90, fill=1)

    p.setFillColor(colors.black)

    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 410, "Billing Information")

    p.setFont("Helvetica", 12)

    p.drawString(
        50,
        385,
        f"Amount Due: Rs. {bill.total_amount}"
    )

    p.drawString(
        50,
        360,
        f"Bill Status: {bill.bill_status}"
    )

  

    if bill.bill_status == "Paid":

        p.setFillColor(colors.green)

    else:

        p.setFillColor(colors.red)

    p.rect(400, 360, 100, 30, fill=1)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)

    p.drawString(
        425,
        372,
        bill.bill_status
    )


    p.setFillColor(colors.black)

    p.line(40, 250, 550, 250)

    p.setFont("Helvetica", 11)

    p.drawString(
        120,
        220,
        "Thank you for using our system"
    )

    p.drawString(
        80,
        200,
        "Smart Electricity Billing & Online Payment Management"
    )

    p.showPage()
    p.save()

    return response
def payhere_success(request):

    bill_id = request.GET.get('bill_id')

    print("SUCCESS CALLBACK HIT")
    print("Bill ID:", bill_id)

    if bill_id:

        try:
            bill = Bill.objects.get(id=bill_id)

            payment_exists = Payment.objects.filter(
                bill=bill,
                payment_status="Success"
            ).exists()

            if not payment_exists:

                Payment.objects.create(
                    user=bill.user,
                    bill=bill,
                    payment_method="PayHere",
                    transaction_reference=f"PAYHERE-{bill.id}",
                    payment_status="Success"
                )

                bill.bill_status = "Paid"
                bill.save()

                print("Payment recorded")

            else:
                print("Duplicate payment prevented")

        except Bill.DoesNotExist:
            print("Bill not found")

    return redirect('bill_history')

def payhere_cancel(request):

    return HttpResponse(
        "Payment was cancelled."
    )


def payhere_notify(request):

    print("PAYHERE NOTIFY HIT")
    print(request.POST)

    return HttpResponse("OK")

