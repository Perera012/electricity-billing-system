from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path(
        'add-reading/',
        views.add_meter_reading,
        name='add_meter_reading'
    ),

    path(
        'bill-history/',
        views.bill_history,
        name='bill_history'
    ),

    path(
        'bill/<int:bill_id>/',
        views.bill_detail,
        name='bill_detail'
    ),

    path(
        'pay/<int:bill_id>/',
        views.make_payment,
        name='make_payment'
    ),

    path(
        'payment-history/',
        views.payment_history,
        name='payment_history'
    ),

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'download-bill/<int:bill_id>/',
        views.download_bill,
        name='download_bill'
    ),

    # PAYHERE URLS

    path(
        'payhere-success/',
        views.payhere_success,
        name='payhere_success'
    ),

    path(
        'payhere-cancel/',
        views.payhere_cancel,
        name='payhere_cancel'
    ),

    path(
        'payhere-notify/',
        views.payhere_notify,
        name='payhere_notify'
    ),
]