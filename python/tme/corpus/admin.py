from models import Project
from django.contrib import admin

class ProjectAdmin(admin.ModelAdmin):
    fields = ('title', 'source', 'content', 'url', 'processed', 'source_link') 
    list_display = ('project_id', 'source_link', 'title', 'processed',)
    search_fields = ('title', 'source', 'content',)
    list_filter = ('processed',)
    readonly_fields = ('source_link',)
    def source_link(self, obj):
        if len(obj.url) > 1:
            return '<a href="%s" target="_blank">%s</a>' % (obj.url, obj.url)
        return 'Not available'
    source_link.allow_tags = True
    source_link.short_description = "Link"
admin.site.register(Project, ProjectAdmin)
