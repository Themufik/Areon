from django.contrib import admin
from .models import Category, Course, Lesson, Comment, Progress, UserProfile, Masage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_courses_count']
    search_fields = ['name']   #попробовать добавить в поиск по курсам связанным с категорией
    def get_courses_count(self,obj):
        return obj.courses.count()
    get_courses_count.short_description = "Количество курсов"
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админка для курсов"""
    list_display = ['name', 'author', 'category', 'created_at', 'get_lessons_count']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description', 'author__username']
    date_hierarchy = 'created_at'
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    get_lessons_count.short_description = 'Количество уроков'  ## добавить возможность убирать категории поиска (сейчас работает по принцыпу выберу одно. А после будет по принципу выбери те что нужны)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админка для уроков"""
    list_display = ['title', 'course', 'order', 'created_at'] #проверить можно ли самостоятельно менять порядок
    list_filter = ['course', 'created_at']
    search_fields = ['title', 'description', 'course__name',] #понять схуяли не работает добовление поиска по чему то
    ordering = ['course', 'order']
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев"""
    list_display = ['author', 'get_course', 'text_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username', 'course__name']
    date_hierarchy = 'created_at'
    
    def get_course(self, obj):
        return obj.course.name
    get_course.short_description = 'Курс'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    """Админка для прогресса"""
    list_display = ['user', 'get_course', 'lesson', 'completed', 'updated_at']
    list_filter = ['completed', 'updated_at']
    search_fields = ['user__username', 'lesson__title', 'lesson__course__name']
    date_hierarchy = 'updated_at'
    
    def get_course(self, obj):
        return obj.lesson.course.name
    get_course.short_description = 'Курс'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админка для профилей"""
    list_display = ['user', 'created_at', 'get_courses_created']
    search_fields = ['user__username', 'bio']
    date_hierarchy = 'created_at'
    
    def get_courses_created(self, obj):
        return obj.user.created_courses.count()
    get_courses_created.short_description = 'Создано курсов'
    
    
    
    
    
    
    
    
