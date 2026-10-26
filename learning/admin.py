from django.contrib import admin
from .models import ChildProfile, LearningProgress


class LearningProgressInline(admin.TabularInline):
    model = LearningProgress
    extra = 0
    readonly_fields = ("updated_at",)


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("nickname", "parent", "age_band", "preferred_language", "created_at")
    list_filter = ("age_band", "preferred_language", "created_at")
    search_fields = ("nickname", "parent__username", "parent__email")
    readonly_fields = ("created_at", "updated_at", "guardian_acknowledged_at")
    inlines = (LearningProgressInline,)


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ("child", "world_id", "xp", "lessons_completed", "progress_percent", "updated_at")
    list_filter = ("world_id",)
    search_fields = ("child__nickname", "child__parent__username")
    readonly_fields = ("updated_at",)
