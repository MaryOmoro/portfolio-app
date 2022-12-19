from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name="home"),
	path('posts/', views.posts, name="posts"),
	path('post/<slug:slug>/', views.post, name="post"),
	path('profile/', views.profile, name="profile"),

	path('create_post/', views.createPost, name="create_post"),
	path('update_post/<slug:slug>/', views.updatePost, name="update_post"),
	path('delete_post/<slug:slug>/', views.deletePost, name="delete_post"),


	path('send_email/', views.sendEmail, name="send_email"),

	path('login/', views.loginPage, name="login"),
	path('register/', views.registerPage, name="register"),
	path('logout/', views.logoutUser, name="logout"),

	path('account/', views.userAccount, name="account"),
	path('update_profile/', views.updateProfile, name="update_profile"),

	path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="main/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password/password_reset_complete.html'), name='password_reset_complete'),      

]