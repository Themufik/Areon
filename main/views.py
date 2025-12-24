from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Course, Lesson, Comment, Progress, UserProfile




def index(request):
    """Главная страница"""
    courses = Course.objects.all().order_by('-created_at')[:6]
    
    context = {
        'courses': courses,
        'total_courses': Course.objects.count(),
        'total_users': User.objects.count(),
        'total_lessons': Lesson.objects.count(),
    }
    return render(request, 'main/index.html', context)


def course_list(request):
    """Список всех курсов с фильтрацией"""
    courses = Course.objects.all()
    categories = Category.objects.all()
    
    selected_category = request.GET.get('category')
    if selected_category:
        courses = courses.filter(category_id=selected_category)
    
    search_query = request.GET.get('search', '')
    if search_query:
        courses = courses.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'main/course_list.html', context)


def course_detail(request, course_id):
    """Страница курса"""
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    comments = course.comments.all().order_by('-created_at')
    
    completed_lessons = []
    progress_percent = 0
    
    if request.user.is_authenticated:
        completed = Progress.objects.filter(
            user=request.user,
            lesson__course=course,
            completed=True
        ).values_list('lesson_id', flat=True)
        completed_lessons = list(completed)
        
        total_lessons = lessons.count()
        if total_lessons > 0:
            progress_percent = int((len(completed_lessons) / total_lessons) * 100)
    
    context = {
        'course': course,
        'lessons': lessons,
        'comments': comments,
        'completed_lessons': completed_lessons,
        'progress_percent': progress_percent,
    }
    return render(request, 'main/course_detail.html', context)


@login_required
def course_create(request):
    """Создание курса"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        
        if not name or not description or not category_id:
            messages.error(request, 'Заполните все поля!')
            return redirect('course_create')
        
        course = Course.objects.create(
            author=request.user,
            name=name,
            description=description,
            category_id=category_id
        )
        
        messages.success(request, 'Курс успешно создан!')
        return redirect('course_detail', course_id=course.id)
    
    categories = Category.objects.all()
    return render(request, 'main/course_form.html', {'categories': categories})


@login_required
def course_edit(request, course_id):
    """Редактирование курса"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого курса!')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        course.name = request.POST.get('name')
        course.description = request.POST.get('description')
        course.category_id = request.POST.get('category')
        course.save()
        
        messages.success(request, 'Курс обновлен!')
        return redirect('course_detail', course_id=course.id)
    
    categories = Category.objects.all()
    context = {
        'course': course,
        'categories': categories,
    }
    return render(request, 'main/course_form.html', context)


@login_required
def course_delete(request, course_id):
    """Удаление курса"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этого курса!')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Курс удален!')
        return redirect('course_list')
    
    return render(request, 'main/course_delete_confirm.html', {'course': course})


def lesson_detail(request, lesson_id):
    """Страница урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    all_lessons = course.lessons.all().order_by('order')
    
    current_index = list(all_lessons).index(lesson)
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    
    is_completed = False
    if request.user.is_authenticated:
        is_completed = Progress.objects.filter(
            user=request.user,
            lesson=lesson,
            completed=True
        ).exists()
    
    context = {
        'lesson': lesson,
        'course': course,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'is_completed': is_completed,
    }
    return render(request, 'main/lesson_detail.html', context)


@login_required
def lesson_create(request, course_id):
    """Создание урока"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.author != request.user:
        messages.error(request, 'У вас нет прав для добавления уроков в этот курс!')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        order = request.POST.get('order', 0)
        file = request.FILES.get('file')
        
        lesson = Lesson.objects.create(
            course=course,
            title=title,
            description=description,
            content = content,
            order=order,
            file=file
        )
        
        messages.success(request, 'Урок создан!')
        return redirect('course_detail', course_id=course.id)
    
    next_order = course.lessons.count() + 1
    
    context = {
        'course': course,
        'next_order': next_order,
    }
    return render(request, 'main/lesson_form.html', context)




@login_required
def lesson_delete(request, lesson_id):
    """Удаление урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    if course.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этого урока!')
        return redirect('lesson_detail', lesson_id=lesson.id)
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Урок удален!')
        return redirect('course_detail', course_id=course.id)
    
    return render(request, 'main/lesson_delete_confirm.html', {'lesson': lesson})


@login_required
def lesson_edit(request, lesson_id):
    """Редактирование урока"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if lesson.course.author != request.user:
        messages.error(request, 'У вас нет прав для редактирования этого урока!')
        return redirect('lesson_detail', lesson_id=lesson.id)

    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.description = request.POST.get('description')
        lesson.content = request.POST.get('content')
        lesson.order = request.POST.get('order')

        if 'file' in request.FILES:
            lesson.file = request.FILES['file']

        lesson.save()

        messages.success(request, 'Урок обновлен!')
        return redirect('lesson_detail', lesson_id=lesson.id)

    context = {
        'lesson': lesson,
        'course': lesson.course,
    }
    return render(request, 'main/lesson_form.html', context)

@login_required
def lesson_complete(request, lesson_id):
    """Отметить урок как завершенный"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    progress, created = Progress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    if progress.completed:
        progress.completed = False
        messages.info(request, 'Урок отмечен как не завершенный')
    else:
        progress.mark_completed()
        messages.success(request, 'Урок завершен! 🎉')
    
    return redirect('lesson_detail', lesson_id=lesson.id)


@login_required
def comment_create(request, course_id):
    """Создание комментария"""
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        text = request.POST.get('text')
        
        if text:
            Comment.objects.create(
                author=request.user,
                course=course,
                text=text
            )
            messages.success(request, 'Комментарий добавлен!')
        
    return redirect('course_detail', course_id=course_id)


@login_required
def comment_delete(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.author == request.user:
        course_id = comment.course.id
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('course_detail', course_id=course_id)
    
    messages.error(request, 'У вас нет прав для удаления этого комментария!')
    return redirect('course_detail', course_id=comment.course.id)


def category_list(request):
    """Список категорий"""
    categories = Category.objects.annotate(
        course_count=Count('courses')
    )
    
    context = {
        'categories': categories,
    }
    return render(request, 'main/category_list.html', context)


def profile(request, username):
    """Профиль пользователя"""
    profile_user = get_object_or_404(User, username=username)
    
    user_profile, created = UserProfile.objects.get_or_create(user=profile_user)
    
    # Созданные курсы
    created_courses = Course.objects.filter(author=profile_user)
    
    # Курсы в процессе - где есть хотя бы один завершенный урок, но не все
    completed_lesson_ids = Progress.objects.filter(
        user=profile_user,
        completed=True
    ).values_list('lesson__course_id', flat=True).distinct()
    
    in_progress_courses = []
    for course_id in completed_lesson_ids:
        course = Course.objects.get(id=course_id)
        total = course.lessons.count()
        completed = Progress.objects.filter(
            user=profile_user,
            lesson__course=course,
            completed=True
        ).count()
        
        # Если не все уроки завершены - курс в процессе
        if completed < total:
            course.progress_percent = int((completed / total) * 100) if total > 0 else 0
            in_progress_courses.append(course)
    
    # Завершенные курсы - где ВСЕ уроки завершены
    completed_courses = []
    for course_id in completed_lesson_ids:
        course = Course.objects.get(id=course_id)
        total = course.lessons.count()
        completed = Progress.objects.filter(
            user=profile_user,
            lesson__course=course,
            completed=True
        ).count()
        
        # Если все уроки завершены
        if total > 0 and completed == total:
            completed_courses.append(course)
    
    # Общий прогресс
    total_progress = Progress.objects.filter(
        user=profile_user,
        completed=True
    ).count()
    
    context = {
        'profile_user': profile_user,
        'created_courses': created_courses,
        'created_courses_count': created_courses.count(),
        'in_progress_courses': in_progress_courses,
        'completed_courses': completed_courses,
        'completed_courses_count': len(completed_courses),
        'total_progress': total_progress,
    }
    return render(request, 'main/profile.html', context)

@login_required
def profile_edit(request):
    """Редактирование профиля"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        profile.bio = bio
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Профиль обновлен!')
        return redirect('profile', username=request.user.username)
    
    context = {
        'profile': profile,
    }
    return render(request, 'main/profile_edit.html', context)


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('index')
    else:
        form = UserCreationForm()
    
    return render(request, 'main/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('index')
    else:
        form = AuthenticationForm()
    
    return render(request, 'main/login.html', {'form': form})


@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('index')