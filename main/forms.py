from django import forms


class UserRegisterForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True)
    password = forms.CharField(max_length=50, required=True)
    name = forms.CharField(max_length=100, required=True)
    gender = forms.CharField(max_length=20, required=True)
    birth_place = forms.CharField(max_length=50, required=True)
    birth_date = forms.DateField(required=True)
    city = forms.CharField(max_length=50, required=True)
    podcaster = forms.BooleanField(required=False)
    artist = forms.BooleanField(required=False)
    songwriter = forms.BooleanField(required=False)


class LabelRegisterForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True)
    password = forms.CharField(max_length=50, required=True)
    name = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=50, required=True)


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50, required=True)
    password = forms.CharField(max_length=50, required=True)
