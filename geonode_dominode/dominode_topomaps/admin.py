from django.contrib import admin
from geonode.layers.models import Layer
from guardian.admin import GuardedModelAdmin


class LayerAdmin(GuardedModelAdmin):
    pass


admin.site.unregister(Layer)
admin.site.register(Layer, LayerAdmin)
