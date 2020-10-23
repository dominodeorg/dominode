from django.urls import (
    path,
)

from . import views

urlpatterns = [
    path(
        '',
        views.TopomapListView.as_view(),
        name='topomap-list'
    ),
    path(
        'v<str:version>/series-<int:scale>/',
        views.TopomapDetailView.as_view(),
        name='topomap-detail'
    ),
    path(
        'v<str:version>/series-<int:scale>/<str:sheet>/',
        views.TopomapSheetDetailView.as_view(),
        name='topomap-sheet'
    ),
]