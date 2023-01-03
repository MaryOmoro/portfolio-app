from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile



class CustomUserCreationForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
    
	def clean_email(self):
		email = self.cleaned_data['email']
		if not email:
			raise ValidationError("This field is required.")
		if User.objects.filter(email=self.cleaned_data['email']).count():
			raise ValidationError("Email is taken.")
		return self.cleaned_data['email']

class PostForm(ModelForm):

	class Meta:
		model = Post
		fields = '__all__'

		widgets = {
			'tags':forms.CheckboxSelectMultiple(),
		}

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email']
		

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = '__all__'
		exclude = ['user']


class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )