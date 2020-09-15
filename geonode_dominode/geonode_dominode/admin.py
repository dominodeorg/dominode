from django.contrib import admin

from geonode_dominode.models import CLI


class CLIAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug', 'command')
    search_fields = ('name', 'slug')


admin.site.register(CLI, CLIAdmin)
