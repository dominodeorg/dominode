import os
import re
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.gdal import DataSource
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.views import generic
from geonode.layers.models import Layer
from geonode.people.models import Profile

from dominode_topomaps.constants import TOPOMAP_DOWNLOAD_PERM_CODE


class TopomapListView(LoginRequiredMixin, generic.ListView):
    queryset = Layer.objects.filter(
        title__contains=(
            settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_SEARCH_PATTERN)
    )
    template_name = 'dominode_topomaps/topomap_list.html'
    context_object_name = 'topomaps'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # For each returned layer we need to provide also a version
        # and series value, in order to be able to build urls
        layers = context['object_list']
        topomaps_info = []
        pattern = r'lsd_published-topomap-series-1-(?P<scale>\d+)_v(?P<version>[\d\.]+)'
        for l in layers:
            match = re.match(pattern, l.title)
            try:
                info = {
                    'scale': int(match.group('scale')),
                    'version': match.group('version'),
                    'layer': l
                }
            except:
                # TODO: What to do if it doesn't match? Just skips?
                #  It happens when it uses the same prefix, but malformed
                #  scale/version value.
                info = {}
            topomaps_info.append(info)

        context['topomaps'] = topomaps_info
        return context


class TopomapSheetsListView(LoginRequiredMixin, generic.ListView):
    model = Layer
    template_name = 'dominode_topomaps/topomap_sheets_list.html'
    context_object_name = 'sheets'
    
    def get_queryset(self):
        version = self.kwargs.get('version')
        scale = self.kwargs.get('scale')
        prefix = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_SEARCH_PATTERN
        # must be an exact match
        return self.model.objects.filter(
            title=f'{prefix}-1-{scale}_v{version}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get possible index from the feature lists
        layer: Layer = context['object_list'].first()
        wfs_link = layer.link_set.filter(name='GeoJSON').first()
        # replace into internal URL for local environment
        # public geoserver name
        internal_geoserver_base_url = urlparse(settings.GEOSERVER_LOCATION).netloc
        wfs_base_url = urlparse(wfs_link.url).netloc
        ds = DataSource(wfs_link.url.replace(
            wfs_base_url, internal_geoserver_base_url))
        wfs_layer = ds[0]
        sheet_info = []
        version = self.kwargs.get('version')
        scale = self.kwargs.get('scale')
        for feature in wfs_layer:
            try:
                info = {
                    'index': feature.get('index') or feature.get('Index')
                }
                # parse index into letter and number
                parsed_index = info['index'].split('-')
                letter = parsed_index[0]
                number = int(parsed_index[1])
                info['index_letter'] = letter
                info['index_number'] = number
                # check that the file exists
                dirpath = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_DIRPATH_PATTERN.format(
                    version=version,
                    scale=scale,
                    sheet=info['index']
                )
                file_pattern = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_FILE_PATTERN.format(
                    version=version,
                    scale=scale,
                    sheet=info['index']
                )
                paper_sizes = []
                for root, dirs, files in os.walk(dirpath):
                    for f in files:
                        match = re.match(file_pattern, f)
                        if match:
                            size = match.group('paper_size')
                            paper_sizes.append(size)
                info['paper_sizes'] = paper_sizes
            except:
                # TODO: what to do if failed to retrieve index
                info = {}
            sheet_info.append(info)
        sheet_info = sorted(sheet_info, key=lambda o: (o['index_letter'], o['index_number']))
        context['scale'] = scale
        context['version'] = version
        context['sheets'] = sheet_info
        context['layer'] = layer
        context['allow_download'] = self.request.user.has_perm(
            f'layers.{TOPOMAP_DOWNLOAD_PERM_CODE}', obj=layer)
        return context


class TopomapSheetDetailView(LoginRequiredMixin, generic.DetailView):
    model = Layer
    context_object_name = 'sheet'
    template_name = 'dominode_topomaps/topomap_detail.html'

    def get_queryset(self):
        version = self.kwargs.get('version')
        scale = self.kwargs.get('scale')
        prefix = \
            settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_SEARCH_PATTERN
        # must be an exact match
        return self.model.objects.filter(
            title=f'{prefix}-1-{scale}_v{version}')

    def get_object(self, queryset=None):
        layer = self.get_queryset().first()
        version = self.kwargs.get('version')
        scale = self.kwargs.get('scale')
        sheet = self.kwargs.get('sheet')
        # check that the file exists
        dirpath = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_DIRPATH_PATTERN.format(
            version=version,
            scale=scale,
            sheet=sheet
        )
        file_pattern = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_FILE_PATTERN.format(
            version=version,
            scale=scale,
            sheet=sheet
        )
        paper_sizes = []
        for root, dirs, files in os.walk(dirpath):
            for f in files:
                match = re.match(file_pattern, f)
                if match:
                    size = match.group('paper_size')
                    paper_sizes.append(size)
        # Check if user can download
        user: Profile = self.request.user
        # Our object is the paper size details
        return {
            'layer': layer,
            'title': layer.title,
            'paper_sizes': paper_sizes,
            'version': version,
            'scale': scale,
            'sheet': sheet,
            'allow_download': user.has_perm(
                f'layers.{TOPOMAP_DOWNLOAD_PERM_CODE}', obj=layer)
        }

    def get(self, request, *args, **kwargs):
        is_download = kwargs.get('download')
        self.object = self.get_object()
        if not is_download:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            if not self.object['allow_download']:
                raise PermissionDenied()
            version = self.kwargs.get('version')
            scale = self.kwargs.get('scale')
            sheet = self.kwargs.get('sheet')
            paper_size = self.kwargs.get('paper_size')
            # download the file
            filename = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_FILE_FORMAT.format(
                version=version,
                scale=scale,
                sheet=sheet,
                paper_size=paper_size
            )
            dirpath = settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_DIRPATH_PATTERN.format(
                version=version,
                scale=scale,
                sheet=sheet,
            )
            fullpath_pdf = os.path.join(dirpath, filename)
            try:
                return FileResponse(
                    open(fullpath_pdf, 'rb'),
                    as_attachment=True,
                    filename=filename
                )
            except FileNotFoundError:
                raise Http404()
