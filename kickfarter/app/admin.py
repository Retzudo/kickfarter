from app.models import *
from django.contrib import admin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Pledge)
class PledgeAdmin(admin.ModelAdmin):
    pass


@admin.register(RewardTier)
class RewardTierAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    pass