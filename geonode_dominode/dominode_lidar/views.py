import logging
import typing

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
from django.template.response import TemplateResponse
from geonode.base.auth import get_or_create_token
from geonode.layers.views import layer_detail as geonode_layer_detail

from .models import PublishedLidarIndexSheetLayer
from . import utils
import os 
logger = logging.getLogger(__name__)


def layer_detail(
        request,
        layername,
        template='layers/layer_detail.html'
):
    """Override geonode default layer detail view

    This view overrides geonode's default layer detail view in order to add
    additional lidar-related data to the render context. This is done in
    order to show a list of existing lidar sheets

    Implementation is a bit unusual:

    - first we call the original geonode view
    - we grab the response and extract the original context from it
    - then we figure out if we need to add lidar-related information to the
      context and proceed to do so if necessary
    - finally we render a response similar to what the original geonode view
      does, but we pass it our custom template

    """

    default_response: TemplateResponse = geonode_layer_detail(
        request, layername, template=template)
    context = default_response.context_data
    layer = context.get('resource')
    try:

        lidar = PublishedLidarIndexSheetLayer.objects.get(pk=layer.id)
    except PublishedLidarIndexSheetLayer.DoesNotExist:
        context['lidar'] = None
    else:
        context['lidar'] = lidar
        sheets_info = _get_topomap_sheets(lidar)
        context['sheets'] = sheets_info
    logger.debug('inside custom layer_detail view')
    logger.debug(f'context: {context}')
    return TemplateResponse(request, template, context=context)


class LidarMapLayerMixin:

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


class LidarmapListView(generic.ListView):
    queryset = PublishedLidarIndexSheetLayer.objects.all()
    template_name = 'dominode_lidar/lidar-list.html'
    context_object_name = 'lidars'
    paginate_by = 20


# this is currently unused, left here for future reference, in case we decide
# to provide a detail view for lidar files
class LidarDetailView(LidarMapLayerMixin, generic.DetailView):
    model = PublishedLidarIndexSheetLayer
    template_name = 'dominode_lidar/lidar-detail.html'
    context_object_name = 'lidar'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sheets_info = _get_topomap_sheets(self.object)
        context['sheets'] = sheets_info
        return context


class SheetDetailView(LidarMapLayerMixin, generic.DetailView):
    model = PublishedLidarIndexSheetLayer
    template_name = 'dominode_lidar/lidar-sheet-detail.html'
    context_object_name = 'layer'

    def get(
            self,
            request: HttpRequest,
            version: str,
            series: int,
            las: str,
            *args,
            **kwargs
    ):
        self.object = self.get_object()
        can_download = self.request.user.has_perm(
            'download_resourcebase', self.object.resourcebase_ptr)

        #sheet_paths = utils.find_sheet(
        #    self.object.series, self.object.version, sheet) or {}

        context = self.get_context_data(
            object=self.object,
            las=las,
            #paper_sizes=sheet_paths.keys(),
            can_download=can_download,
            url_download="download"
        )
        return self.render_to_response(context)


class LidarSheetDownloadView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(
            self,
            request: HttpRequest,
            version: str,
            series: int,
            las: str,
            *args,
            **kwargs
    ):
        queryset = PublishedLidarIndexSheetLayer.objects.filter(
            name__contains=version).filter(name__contains=series)
        lidar_layer = get_object_or_404(queryset)
        logger.debug(f'lidar_layer: {lidar_layer}')
        can_download = self.request.user.has_perm(
            'download_resourcebase', lidar_layer.resourcebase_ptr)
        if not can_download:
            raise Http404()
        else:
            location_las = settings.DOMINODE_PUBLISHED_LIDAR["location_files"]
            las_path = os.path.join(location_las,las)
            available_path = os.path.exists(las_path )
            if available_path:
                return FileResponse(
                    open(las_path, 'rb'),
                    as_attachment=True,
                    filename=las
                )
            else:
                raise Http404()


def _get_lidar_sheets(
        lidar: PublishedLidarIndexSheetLayer
        ) -> typing.List:
    geoserver_admin_user = get_user_model().objects.get(
        username=settings.OGC_SERVER_DEFAULT_USER)
    access_token = get_or_create_token(geoserver_admin_user)
    las_files = lidar.get_published_sheets(
        use_public_wfs_url=False, geoserver_access_token=access_token)
    las_info = []
    location_lidar = settings.DOMINODE_PUBLISHED_LIDAR['location_files']

    for las in las_files:

        path_file = os.path.join(location_lidar,las)
        las_path = os.path.exists(path_file)

        if las_path:
            las_info.append({
                'index': las,
                'location': path_file
            })
    las_info = sorted(las_info, key=lambda x: x['index'])
    return las_info
