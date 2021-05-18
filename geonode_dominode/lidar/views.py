from django.views.generic import TemplateView
from django.conf import settings

class LidarView(TemplateView):
    template_name = "lidar/potree/data/viewer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['BUCKET_URL'] = settings.LIDAR_BUCKET
        context['lidar_permission'] = self.request.user.is_authenticated 
        return context
