from django.urls import (
    path,
)
from guardian.decorators import permission_required_or_403

from . import views
from .constants import TOPOMAP_DOWNLOAD_PERM_CODE

urlpatterns = [
    path(
        '',
        views.TopomapListView.as_view(),
        name='topomap-list'
    ),
    path(
        'v<str:version>/series-<int:scale>/',
        views.TopomapSheetsListView.as_view(),
        name='topomap-sheets-list'
    ),
    path(
        'v<str:version>/series-<int:scale>/<str:sheet>/',
        views.TopomapSheetDetailView.as_view(),
        name='topomap-sheet'
    ),
    path(
        'v<str:version>/series-<int:scale>/<str:sheet>/<str:paper_size>/download',
        permission_required_or_403(f'layer.{TOPOMAP_DOWNLOAD_PERM_CODE}')(
            views.TopomapSheetDetailView.as_view()),
        name='topomap-sheet-download',
        kwargs={
            'download': True
        }
    ),
]
