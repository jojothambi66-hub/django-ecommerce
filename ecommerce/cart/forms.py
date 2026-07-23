from django import forms
from cart.models import Order
class OrderForm(forms.ModelForm):
    choices=[('online','Online'),('cod','COD')]
    payment_method=forms.ChoiceField(choices=choices)

    class Meta:
        model=Order
        fields=['address','phone','payment_method']