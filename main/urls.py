from django.urls import path
from . import views

urlpatterns = [
    # Авторизация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Главная страница
    path('', views.index, name='index'),




    
    # Курсы
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/create/', views.course_create, name='course_create'),
    path('course/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    
    # Уроки
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('course/<int:course_id>/lesson/create/', views.lesson_create, name='lesson_create'),
    path('lesson/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lesson/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('lesson/<int:lesson_id>/complete/', views.lesson_complete, name='lesson_complete'),
    
    # Комментарии
    path('course/<int:course_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    
    # Категории
    path('categories/', views.category_list, name='category_list'),
    
    # Профиль - ВАЖНО: profile/edit/ ПЕРЕД profile/<username>/
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.profile, name='profile'),


]
