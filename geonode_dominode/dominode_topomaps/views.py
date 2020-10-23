import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from geonode.layers.models import Layer


class TopomapListView(LoginRequiredMixin, generic.ListView):
    queryset = Layer.objects.filter(
        name__contains=(
            settings.DOMINODE_PUBLISHED_TOPOMAP_INDEX_SHEET_SEARCH_PATTERN)
    )
    template_name = 'dominode_topomaps/topomap_list.html'
    context_object_name = 'topomaps'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: for each returned layer we need to provide also a version
        #  and series value, in order to be able to build urls
        return context


class TopomapDetailView(LoginRequiredMixin, generic.DetailView):
    model = Layer
    template_name = 'dominode_topomaps/topomap_detail.html'
    context_object_name = 'topomap'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TopomapSheetDetailView(LoginRequiredMixin, generic.DetailView):
    context_object_name = 'sheet'

    def get_object(self, queryset=None):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
