from django.urls import path

from . import views

urlpatterns = [
    path(
        '',
        views.LidarmapListView.as_view(),
        name='lidar-list'
    ),
    path(
        'v<str:version>/series-<int:series>/<str:las>/',
        views.SheetDetailView.as_view(),
        name='lidar-sheet-detail',
    ),
    path(
        'v<str:version>/series-<int:series>/<str:las>/<str:url_download>/',
        views.LidarSheetDownloadView.as_view(),
        name='lidar-sheet-download',
    ),
]
