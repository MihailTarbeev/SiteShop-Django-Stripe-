import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Повтор пароля", widget=forms.PasswordInput())

    class Meta:
        model = get_user_model()
        fields = ["email", "first_name",
                  "last_name", "password1", "password2"]
        labels = {
            "email": "E-mail",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Этот E-mail уже зарегистрирован")
        return email

    # def save(self, commit=True):
    #     User = get_user_model()
    #     user = User.objects.create_user(
    #         email=self.cleaned_data['email'],
    #         password=self.cleaned_data['password1'],
    #         first_name=self.cleaned_data['first_name'],
    #         last_name=self.cleaned_data['last_name'],
    #     )
    #     return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True,
                               label="Логин", widget=forms.TextInput())
    email = forms.CharField(disabled=True,
                            label="E-mail", widget=forms.TextInput())

    class Meta:
        model = get_user_model()
        fields = ["photo", "username", "email",
                  "first_name", "last_name"]
        labels = {
            'first_name': "Имя",
            "last_name": "Фамилия",
        }
