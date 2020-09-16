import asyncio
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required, login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest, \
    JsonResponse, HttpResponseRedirect
from geonode.groups import views
from django.utils.translation import ugettext_lazy as _

import logging

from geonode.groups.models import GroupProfile
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin

from geonode_dominode.models import CLI
from geonode_dominode.tasks import task_cli_sync_geoserver

logger = logging.getLogger('geonode_dominode')


class GroupDetailView(views.GroupDetailView):
    """
    Mixes a detail view (the group) with a ListView (the members).
    """

    model = get_user_model()
    template_name = "groups/group_detail_override.html"
    paginate_by = None
    group = None


class CLIListView(LoginRequiredMixin, PermissionRequiredMixin, views.ListView):

    model = CLI
    template_name = "cli/groups/list.html"
    permission_required = ('geonode_dominode.execute_cli', )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CLIListView, self).get_context_data(
            object_list=object_list, **kwargs)
        context['object'] = self.group
        return context

    def get(self, request, *args, **kwargs):
        group_slug = kwargs['slug']
        self.group = GroupProfile.objects.get(slug=group_slug)
        self.object_list = self.get_queryset().filter(
            groups=self.group)
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_(
                    "Empty list and '%(class_name)s.allow_empty' is "
                    "False.") % {
                                  'class_name': self.__class__.__name__,
                              })
        context = self.get_context_data()
        return self.render_to_response(context)


@login_required
@permission_required('geonode_dominode.execute_cli')
def cli_executor(request, cli_slug):
    cli = CLI.objects.get(slug=cli_slug)
    proc = cli.execute_command()
    stdout, stderr = asyncio.run(proc)
    return HttpResponse(stdout)


@login_required
@permission_required('groups.can_sync_geoserver')
def cli_sync_geoserver(request):
    """
    :type request: django.http.HttpRequest
    """
    if request.method == 'POST':
        workspace_name = request.POST.get('workspace-name')
        redirect = request.POST.get('redirect')
        user = request.user.get_username()
        logger.debug('Receiving GeoServer sync requests.')
        logger.debug('Workspace name: {}'.format(workspace_name))
        logger.debug('User name: {}'.format(user))
        task_cli_sync_geoserver.delay(workspace_name, user)
        messages.success(
            request, _('Sync GeoServer command is executed in the server.'))
        return HttpResponseRedirect(redirect_to=redirect)
    return HttpResponseBadRequest()
