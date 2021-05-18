from django.views.generic import TemplateView

class LidarView(TemplateView):
    template_name = "lidar/potree/data/viewer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lidar_permission'] = self.request.user.is_authenticated 
        return context
