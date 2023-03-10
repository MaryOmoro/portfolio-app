from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .decorators import *
from .forms import PostForm, CustomUserCreationForm, ProfileForm, UserForm, ContactForm
from .filters import PostFilter
from .models import *
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.http import JsonResponse




def home(request):
	posts = Post.objects.filter(active=True, featured=True)[0:3]

	context = {'posts':posts}
	return render(request, 'base/index.html', context)

def posts(request):
	posts = Post.objects.filter(active=True)
	myFilter = PostFilter(request.GET, queryset=posts)
	posts = myFilter.qs
    
	if request.method == 'POST':
	    page = request.GET.get('page')

	paginator = Paginator(posts, 5)

	try:
		posts = paginator.page('page')
	except PageNotAnInteger:
		posts = paginator.page(1)
	except EmptyPage:
		posts = paginator.page(paginator.num_pages)

	context = {'posts':posts, 'myFilter':myFilter}
	return render(request, 'base/posts.html', context)

def post(request, slug):
	post = Post.objects.get(slug=slug)

	if request.method == 'POST':
		PostComment.objects.create(
			author=request.user.profile,
			post=post,
			body=request.POST['comment']
			)
		messages.success(request, "Your comment was successfuly posted!")

		return redirect('post', slug=post.slug)


	context = {'post':post}
	return render(request, 'base/post.html', context)

def profile(request):
	return render(request, 'base/profile.html')


@admin_only
@login_required(login_url="home")
def createPost(request):
	form = PostForm()

	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
		return redirect('posts')

	context = {'form':form}
	return render(request, 'base/post_form.html', context)


@admin_only
@login_required(login_url="home")
def updatePost(request, slug):
	post = Post.objects.get(slug=slug)
	form = PostForm(instance=post)

	if request.method == 'POST':
		form = PostForm(request.POST, request.FILES, instance=post)
		if form.is_valid():
			form.save()
		return redirect('posts')

	context = {'form':form}
	return render(request, 'base/post_form.html', context)

@admin_only
@login_required(login_url="home")
def deletePost(request, slug):
	post = Post.objects.get(slug=slug)

	if request.method == 'POST':
		post.delete()
		return redirect('posts')
	context = {'item':post}
	return render(request, 'base/delete.html', context)



def contact(request):
	form_class = ContactForm
	form = form_class(request.POST or None)

	if request.method == "POST" and request.accepts('text/html, */*'):
		form = ContactForm(request.POST)
	    
		if form.is_valid():
			name = form.cleaned_data['name']
			email = form.cleaned_data['email']
			content = form.cleaned_data['content']
			form.save()
			messages.success(request, "Thanks for reaching out")
			return JsonResponse({"name":name}, status=200)
			
			
	    
		else:
			errors = form.errors.as_json()
			return JsonResponse({"errors": errors}, status=400)
			
	return render(request, "base/contact.html", {"form": form})
			
		
    
	template = render_to_string('base/contact_template.html', {
		'name':request.POST['name'],
		'email':request.POST['email'],
		'message':request.POST['message'],
		})
			
	email = EmailMessage(request.POST['subject'],
		template,
		settings.EMAIL_HOST_USER,
		['']
		)
		
	email.fail_silently=False
	email.send("SEND")
	
	messages.success(request, "Thanks for reaching out")	
	
	return render(request, 'base/contact.html')

def loginPage(request):
	if request.user.is_authenticated:
		return redirect('home')

	if request.method == 'POST':
		email = request.POST.get('email')
		password =request.POST.get('password')

		try:
			user = User.objects.get(email=email)
			user = authenticate(request, username=user.username, password=password)
		except:
			messages.error(request, 'User with this email does not exists')
			return redirect('login')
			
		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.error(request, 'Email OR password is incorrect')

	context = {}
	return render(request, 'base/login.html', context)

def registerPage(request):
	form = CustomUserCreationForm()
	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.save()
			messages.success(request, 'Account successfuly created!')

			user = authenticate(request, username=user.username, password=request.POST['password1'])

			if user is not None:
				login(request, user)

			next_url = request.GET.get('next')
			if next_url == '' or next_url == None:
				next_url = 'home'
			return redirect(next_url)
		else:
			messages.error(request, 'An error has occured with registration')
	context = {'form':form}
	return render(request, 'base/register.html', context)

def logoutUser(request):
	logout(request)
	return redirect('home')

@login_required(login_url="home")
def userAccount(request):
	profile = request.user.profile

	context = {'profile':profile}
	return render(request, 'base/account.html', context)

@login_required(login_url="home")
def updateProfile(request):
	user = request.user
	profile = user.profile
	form = ProfileForm(instance=profile)
	if request.method == 'POST':
		user_form = UserForm(request.POST, instance=user)
		if user_form.is_valid():
			user_form.save()

		form = ProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save()
			return redirect('account')


	context = {'form':form}
	return render(request, 'base/profile_form.html', context)


def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "base/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'admin@example.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					
					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("home")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="base/password/password_reset.html", context={"password_reset_form":password_reset_form})	


