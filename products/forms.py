from django import forms
from parler.forms import TranslatableModelForm
from users.models import Contact
from .models import Review
import re



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        return name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            raise forms.ValidationError("Email is required.")
        if not re.match(regex, email):
            raise forms.ValidationError("Invalid email format.")
        return email

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if not message:
            raise forms.ValidationError("Message is required.")
        return message


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'class':'form-control','min':1,'max':5}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Share your experience...'}))

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def clean_comment(self):
        comment = self.cleaned_data.get('comment','').strip()
        if len(comment) > 2000:
            raise forms.ValidationError('Comment too long (max 2000 characters).')
        return comment
