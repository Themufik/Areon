from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):

    #Категории курсов (например: Программирование, Дизайн, Маркетинг). Думаю для начала сделать их статичными

    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Название категории"
    )

    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):

        return self.name


class Course(models.Model):


    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_courses',
        verbose_name="Автор курса"
    )
    

    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Категория",
    )
    

    name = models.CharField(
        max_length=200, 
        verbose_name="Название курса"
    )
    description = models.TextField(
        verbose_name="Описание курса"
    )
    

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
        
    

    
    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']  # Сортировка по дате
    
    def __str__(self):
        return self.name
    
    def get_total_lessons(self):
        """Получить общее количество уроков в курсе"""
        return self.lessons.count()



class Lesson(models.Model):


    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Курс"
    )
    

    title = models.CharField(
        max_length=200,
        verbose_name="Название урока"
    )
    description = models.TextField(
        verbose_name="Описание урока"
    )

    content = models.TextField(
        verbose_name="Содержание урока"
    )

    # Порядковый номер урока в курсе (интересная штука надо бы побольше попрактиковаться )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )
    
    # Файлы (видео, документы и т.д.)
    file = models.FileField(
        upload_to='lessons/files/',
        blank=True,
        null=True,
        verbose_name="Файл урока"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['course', 'order']  # Сортировка по курсу и порядку
        unique_together = ['course', 'order']  # Уникальный порядок в рамках курса
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Comment(models.Model):


    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор"
    )# Кто оставил комментарий
    

    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Курс"
    )
    

    text = models.TextField(
        verbose_name="Текст комментария"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-created_at']  # Новые комментарии первыми
    
    def __str__(self):
        return f"{self.author.username} - {self.course.name}"


class Progress(models.Model):

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, #после релиза добавить функцию что б не удолять прогресс пользователя
        related_name='user_progress',
        verbose_name="Пользователь"
    )
    
    # Какой урок проходит
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name="Урок"
    )
    
    # Завершен ли урок
    completed = models.BooleanField(
        default=False,
        verbose_name="Завершен"
    )
    

    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Начало"       #добавить измерение по пользователю
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено"
    )
    
    class Meta:
        verbose_name = "Прогресс"
        verbose_name_plural = "Прогресс"
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.user.username} - {self.lesson.title}"
    
    def mark_completed(self):

        self.completed = True
        self.save()
    
    @property
    def course(self):
        """Получить курс через урок""" #(тоже интересная штука)
        return self.lesson.course


class UserProfile(models.Model):

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    
    # Описание профиля
    bio = models.TextField(
        blank=True,
        verbose_name="О себе"
    )
    
    # Аватар
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    
    # Дата создания профиля
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def get_completed_courses(self):

        # Курсы, где все уроки завершены
        return Course.objects.filter(
            lessons__lesson_progress__user=self.user,
            lessons__lesson_progress__completed=True
        ).distinct()
        
        
        
class Masage(models.Model):
    name = models.CharField(
        unique= True,
        max_length= 10,
        blank= True)
    
    
    sername = models.TextField(
        blank= True
    )
    