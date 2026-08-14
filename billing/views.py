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
from .services import extract_meter_reading
from django.contrib import messages
from django.contrib.auth import login

@login_required
def home(request):
    username = request.user.username

    if len(username) > 4:
        masked_username = (
            username[:2] +
            "*" * (len(username) - 4) +
            username[-2:]
        )
    else:
        masked_username = "*" * len(username)

    context = {
        "masked_username": masked_username,
    }

    return render(request, "billing/home.html", context)

@login_required
def add_meter_reading(request):

    # --------------------------------------------------
    # MONTH ORDER
    # --------------------------------------------------
    month_numbers = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
    }

    # --------------------------------------------------
    # GET USER'S LATEST METER READING
    # --------------------------------------------------
    last_reading = MeterReading.objects.filter(
        user=request.user
    ).order_by(
        '-reading_date',
        '-id'
    ).first()

    # --------------------------------------------------
    # POST REQUEST
    # --------------------------------------------------
    if request.method == 'POST':

        form = MeterReadingForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            meter_reading = form.save(commit=False)

            # --------------------------------------------------
            # ASSIGN LOGGED-IN USER
            # --------------------------------------------------
            meter_reading.user = request.user

            # Get selected month
            selected_month = meter_reading.month

            # --------------------------------------------------
            # CHECK DUPLICATE MONTH
            # --------------------------------------------------
            existing = Bill.objects.filter(
                user=request.user,
                meter_reading__month=selected_month
            ).exists()

            if existing:
                return render(
                    request,
                    'billing/add_meter_reading.html',
                    {
                        'form': form,
                        'last_reading': last_reading,
                        'error': (
                            'Bill already exists for this month. '
                            'Please select the next billing month.'
                        )
                    }
                )

            # --------------------------------------------------
            # FIRST METER READING
            # --------------------------------------------------
            if last_reading is None:

                meter_reading.previous_reading = 0

            # --------------------------------------------------
            # SUBSEQUENT METER READINGS
            # --------------------------------------------------
            else:

                last_month = last_reading.month

                last_month_number = month_numbers.get(
                    last_month
                )

                selected_month_number = month_numbers.get(
                    selected_month
                )

                # Validate month names
                if (
                    last_month_number is None
                    or selected_month_number is None
                ):
                    return render(
                        request,
                        'billing/add_meter_reading.html',
                        {
                            'form': form,
                            'last_reading': last_reading,
                            'error': 'Invalid billing month selected.'
                        }
                    )

                # --------------------------------------------------
                # DETERMINE NEXT MONTH
                # --------------------------------------------------
                if last_month_number == 12:
                    expected_month_number = 1
                else:
                    expected_month_number = last_month_number + 1

                # --------------------------------------------------
                # PREVENT SKIPPING MONTHS
                # --------------------------------------------------
                if selected_month_number != expected_month_number:

                    next_month = next(
                        month
                        for month, number in month_numbers.items()
                        if number == expected_month_number
                    )

                    return render(
                        request,
                        'billing/add_meter_reading.html',
                        {
                            'form': form,
                            'last_reading': last_reading,
                            'error': (
                                f'Your latest meter reading is for '
                                f'{last_month}. '
                                f'Please submit the {next_month} '
                                f'reading next.'
                            )
                        }
                    )

                # --------------------------------------------------
                # AUTOMATICALLY SET PREVIOUS READING
                # --------------------------------------------------
                meter_reading.previous_reading = (
                    last_reading.current_reading
                )

            # --------------------------------------------------
            # VALIDATE CURRENT READING
            # --------------------------------------------------
            if meter_reading.current_reading <= meter_reading.previous_reading:

                return render(
                    request,
                    'billing/add_meter_reading.html',
                    {
                        'form': form,
                        'last_reading': last_reading,
                        'error': (
                            'Current reading must be greater than '
                            f'the previous reading '
                            f'({meter_reading.previous_reading}).'
                        )
                    }
                )

            # --------------------------------------------------
            # CALCULATE UNITS USED
            # --------------------------------------------------
            meter_reading.units_used = (
                meter_reading.current_reading
                - meter_reading.previous_reading
            )

            # --------------------------------------------------
            # METER IMAGE REQUIRED
            # --------------------------------------------------
            if not meter_reading.meter_image:

                return render(
                    request,
                    'billing/add_meter_reading.html',
                    {
                        'form': form,
                        'last_reading': last_reading,
                        'error': (
                            'Meter image is required. '
                            'Please upload a clear image of your '
                            'electricity meter.'
                        )
                    }
                )

            # --------------------------------------------------
            # SAVE METER READING
            # --------------------------------------------------
            meter_reading.save()

            # --------------------------------------------------
            # OCR VERIFICATION
            # --------------------------------------------------
            if meter_reading.meter_image:

                print(
                    "Saved Image Path:",
                    meter_reading.meter_image.path
                )

                ocr_result = extract_meter_reading(
                    meter_reading.meter_image.path
                )

                # --------------------------------------------------
                # OCR COULD NOT READ IMAGE
                # --------------------------------------------------
                if ocr_result is None:

                    meter_reading.delete()

                    return render(
                        request,
                        'billing/add_meter_reading.html',
                        {
                            'form': form,
                            'last_reading': last_reading,
                            'error': (
                                'Unable to read the uploaded meter image. '
                                'Please upload a clearer image.'
                            )
                        }
                    )

                # --------------------------------------------------
                # CONVERT OCR RESULT TO INTEGER
                # --------------------------------------------------
                try:

                    ocr_reading = int(ocr_result)

                except (ValueError, TypeError):

                    meter_reading.delete()

                    return render(
                        request,
                        'billing/add_meter_reading.html',
                        {
                            'form': form,
                            'last_reading': last_reading,
                            'error': (
                                'OCR detected an invalid meter reading.'
                            )
                        }
                    )

                # --------------------------------------------------
                # COMPARE OCR READING WITH ENTERED READING
                # --------------------------------------------------
                entered_reading = int(
                    meter_reading.current_reading
                )

                if ocr_reading != entered_reading:

                    meter_reading.delete()

                    return render(
                        request,
                        'billing/add_meter_reading.html',
                        {
                            'form': form,
                            'last_reading': last_reading,
                            'error': (
                                f'OCR detected {ocr_reading}, '
                                f'but you entered {entered_reading}. '
                                'Please verify your meter reading.'
                            )
                        }
                    )

            # --------------------------------------------------
            # CALCULATE ELECTRICITY BILL
            # --------------------------------------------------
            total_amount = calculate_bill(
                meter_reading.units_used
            )

            # --------------------------------------------------
            # CREATE BILL
            # --------------------------------------------------
            Bill.objects.create(
                user=request.user,
                meter_reading=meter_reading,
                total_amount=total_amount,
                bill_status='Unpaid'
            )

            # --------------------------------------------------
            # SUCCESS
            # --------------------------------------------------
            return redirect('bill_history')

    # --------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------
    else:

        form = MeterReadingForm()

    # --------------------------------------------------
    # DISPLAY PAGE
    # --------------------------------------------------
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

    bill_id = request.GET.get("bill_id")

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

            # Restore the customer's authenticated session
            login(
                request,
                bill.user,
                backend="django.contrib.auth.backends.ModelBackend"
            )

            messages.success(
                request,
                "Payment completed successfully."
            )

            return redirect("payment_history")

        except Bill.DoesNotExist:

            messages.error(
                request,
                "Bill not found."
            )

    return redirect("home")

def payhere_cancel(request):
    return HttpResponse("Payment was cancelled.")


def payhere_notify(request):
    print("PAYHERE NOTIFY HIT")
    print(request.POST)
    return HttpResponse("OK")