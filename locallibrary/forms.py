import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import BookInstance
class RenewBookForm(forms.ModelForm):
    def clean_renewal_date(self):
        data=self.cleaned_data["due_back"]
        if data< datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        if data>datetime.date.today()+datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        return data
    class Meta:
        model=BookInstance
        fields=['due_back']
        labels={"due_back":_("Renewal date")}
        help_text={"due_back":_("Enter a date between now and 4 weeks (default 3).")}

"""
from django import forms
**Validation for just one field
class MyForm(forms.Form):
    username = forms.CharField(max_length=50)

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        return username
            ________________________________________________________________________
from django import forms
**Validations for more just one field
class ContactForm(forms.Form):
    name = forms.CharField(max_length=50)
    has_phone = forms.BooleanField(required=False)
    phone_number = forms.CharField(max_length=15, required=False)

    def clean(self):
        cleaned_data = super().clean()
        has_phone = cleaned_data.get("has_phone")
        phone_number = cleaned_data.get("phone_number")

        if has_phone and not phone_number:
            raise forms.ValidationError("Please provide a phone number if you have selected the option.")

"""