from django.contrib import admin
from geonode.groups.models import GroupProfile
from geonode.layers.models import Layer
from guardian.admin import GuardedModelAdmin


class GroupProfileAdmin(GuardedModelAdmin):
    pass

class LayerAdmin(GuardedModelAdmin):
    pass


# we unregister the standard geonode GroupProfile admin and then replace it
# with our own, which is based on django-guardian (and allows setting object-
# level permissions
admin.site.unregister(GroupProfile)
admin.site.register(GroupProfile, GroupProfileAdmin)

admin.site.unregister(Layer)
admin.site.register(Layer, LayerAdmin)
