from django.conf.urls import url
from lidar.views import LidarView

urlpatterns = [
    url(r'^view/?$',
        LidarView.as_view(),
        name='lidar-map'), 
      ]