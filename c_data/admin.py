from django.contrib import admin
from .models import MusubiyaUser, CustomerData, Post

# Register your models here.

admin.site.register(MusubiyaUser)
admin.site.register(CustomerData)

class PostAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'message',)
    list_display_links = ('user_id', 'message',)

admin.site.register(Post,PostAdmin)
