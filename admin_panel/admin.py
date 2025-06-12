from django.contrib import admin
from . models import *
# Register your models here.


admin.site.register(Coupon)
admin.site.register(Task)
admin.site.register(Story)
admin.site.register(DailyCheckIn)
admin.site.register(Giveaway)
admin.site.register(GiveawayParticipation)
admin.site.register(Announcement)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    search_fields = ('title',)
    list_filter = ('category',)