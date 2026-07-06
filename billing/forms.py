from django import forms
from .models import MeterReading


MONTH_CHOICES = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]


class MeterReadingForm(forms.ModelForm):

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = MeterReading

        fields = [
            'month',
            'current_reading',
            'meter_image'
        ]

        widgets = {

            'current_reading': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Current Reading'
                }
            ),

            'meter_image': forms.FileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }