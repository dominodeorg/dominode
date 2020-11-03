import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
)
from django.views import (
    generic,
    View
)
from django.shortcuts import get_object_or_404
from geonode.base.auth import get_or_create_token

from .models import PublishedTopoMapIndexSheetLayer
from . import utils

logger = logging.getLogger(__name__)


class TopoMapLayerMixin:

    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        version = self.kwargs.get('version')
        series = self.kwargs.get('series')
        if version is None or series is None:
            raise AttributeError(
                f'Generic detail view {self.__class__.__name__} must be '
                f'called with a suitable version and series parameters in the '
                f'URLconf'
            )
        queryset = queryset.filter(
            name__contains=version).filter(name__contains=series)
        return get_object_or_404(queryset)


class TopomapListView(generic.ListView):
    queryset = PublishedTopoMapIndexSheetLayer.objects.all()
    template_name = 'dominode_topomaps/topomap-list.html'
    context_object_name = 'topomaps'
    paginate_by = 20


class TopomapDetailView(generic.DetailView):
    model = PublishedTopoMapIndexSheetLayer
    template_name = 'dominode_topomaps/topomap-detail.html'
    context_object_name = 'topomap'

    def get_object(self, queryset=None):
        queryset = queryset if queryset is not None else self.get_queryset()
        version = self.kwargs.get('version')
        series = self.kwargs.get('series')
        if version is None or series is None:
            raise AttributeError(
                f'Generic detail view {self.__class__.__name__} must be '
                f'called with a suitable version and series parameters in the '
                f'URLconf'
            )
        queryset = queryset.filter(
            name__contains=version).filter(name__contains=series)
        return get_object_or_404(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object: PublishedTopoMapIndexSheetLayer
        geoserver_admin_user = get_user_model().objects.get(
            username=settings.OGC_SERVER_DEFAULT_USER)
        access_token = get_or_create_token(geoserver_admin_user)
        published_sheets = self.object.get_published_sheets(
            use_public_wfs_url=False, geoserver_access_token=access_token)
        sheets_info = []
        for sheet_index in published_sheets:
            sheet_paths = utils.find_sheet(
                self.object.series, self.object.version, sheet_index)
            if sheet_paths is not None:
                sheets_info.append({
                    'index': sheet_index,
                    'paper_sizes': sheet_paths.keys()
                })
        sheets_info = sorted(sheets_info, key=lambda x: x['index'])
        context['sheets'] = sheets_info
        context['allow_download'] = self.request.user.has_perm(
            'download_resourcebase', self.object.resourcebase_ptr)
        return context


class SheetDetailView(TopoMapLayerMixin, generic.DetailView):
    model = PublishedTopoMapIndexSheetLayer
    template_name = 'dominode_topomaps/topomap-sheet-detail.html'
    context_object_name = 'layer'

    def get(
            self,
            request: HttpRequest,
            sheet: str,
            *args,
            **kwargs
    ):
        self.object = self.get_object()
        can_download = self.request.user.has_perm(
            'download_resourcebase', self.object.resourcebase_ptr)

        if not can_download:
            raise Http404()

        sheet_paths = utils.find_sheet(
            self.object.series, self.object.version, sheet) or {}

        context = self.get_context_data(
            object=self.object,
            sheet=sheet,
            paper_sizes=sheet_paths.keys(),
            can_download=can_download
        )
        return self.render_to_response(context)


class TopomapSheetDownloadView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(
            self,
            request: HttpRequest,
            version: str,
            series: int,
            sheet: str,
            paper_size: str,
            *args,
            **kwargs
    ):
        queryset = PublishedTopoMapIndexSheetLayer.objects.filter(
            name__contains=version).filter(name__contains=series)
        topomap_layer = get_object_or_404(queryset)
        logger.debug(f'topomap_layer: {topomap_layer}')
        can_download = self.request.user.has_perm(
            'download_resourcebase', topomap_layer.resourcebase_ptr)
        if not can_download:
            raise Http404()
        else:
            available_sheet_paths = utils.find_sheet(series, version, sheet) or {}
            sheet_path = available_sheet_paths.get(paper_size)
            if sheet_path is not None:
                return FileResponse(
                    open(sheet_path, 'rb'),
                    as_attachment=True,
                    filename=sheet_path.name
                )
            else:
                raise Http404()
