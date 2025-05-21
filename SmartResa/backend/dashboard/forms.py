from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
from .models import CustomUser, Reservation

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'name@ensam-casa.ma',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control'
        })
    )

    error_messages = {
        'invalid_login': "Invalid email/password combination.",
        'inactive': "This account is inactive.",
    }

class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'At least 8 characters'
        }),
        min_length=8
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'role', 'filiere', 'year']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@ensam-casa.ma'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe'
            }),
            'role': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'filiere': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select your filière'),
                ('GI', 'Genie Informatique'),
                ('GM', 'Genie Mecanique'),
                ('GP', 'Genie Physique'),
            ]),
            'year': forms.Select(attrs={'class': 'form-select'}, choices=CustomUser.YEAR_CHOICES),
        }

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'student':
            if not cleaned_data.get('filiere'):
                self.add_error('filiere', 'Filière is required for students')
            if not cleaned_data.get('year'):
                self.add_error('year', 'Academic year is required for students')
        else:
            if cleaned_data.get('filiere'):
                self.add_error('filiere', 'Filière should only be set for students')
            if cleaned_data.get('year'):
                self.add_error('year', 'Academic year should only be set for students')

        return cleaned_data

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now().strftime('%Y-%m-%dT%H:%M')
        self.fields['start_time'].widget.attrs['min'] = now
        self.fields['end_time'].widget.attrs['min'] = now

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        now = timezone.now()

        if start_time and start_time < now:
            self.add_error('start_time', "Cannot reserve seats in the past")
        
        if start_time and end_time:
            if end_time <= start_time:
                self.add_error('end_time', "End time must be after start time")
            elif (end_time - start_time).total_seconds() < 1800:
                self.add_error(None, "Minimum reservation time is 30 minutes")

        return cleaned_data
class BlockSeatForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    duration = forms.IntegerField(
        label="Block Duration (hours)",
        min_value=1,
        max_value=72
    )