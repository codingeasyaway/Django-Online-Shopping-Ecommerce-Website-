from django import forms
from .models import Order, Customer
from django.contrib.auth.models import User

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['ordered_by', 'shipping_address', 'mobile', 'email']
        widgets ={'ordered_by': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your Full Name..'}),
                  'shipping_address': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your Address..'}),
                  'mobile': forms.TextInput(attrs={'class': 'form-control','placeholder':'Enter your Phone Number..'},),
                  'email': forms.TextInput(attrs={'class':'form-control','placeholder':'Enter your Email Id..'}),
                 }

class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email id'}))
    class Meta:
        model = Customer
        fields =['username', 'password', 'email', 'full_name', 'address']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your address'}),
            }

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("This username is already exists.")
        return uname


class CustomerLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
