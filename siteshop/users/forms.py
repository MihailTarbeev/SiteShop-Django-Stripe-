import datetime
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Придумайте логин',
            'autocomplete': 'username',
            'autofocus': True
        })
    )

    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com',
            'autocomplete': 'email'
        })
    )

    first_name = forms.CharField(
        label='Имя',
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваше имя'
        })
    )

    last_name = forms.CharField(
        label='Фамилия',
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваша фамилия'
        })
    )

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input form-password',
            'placeholder': 'Создайте пароль'
        }),
    )

    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input form-password',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Этот логин уже занят')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите ваш логин',
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input form-password',
            'placeholder': '••••••••',
        })
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
