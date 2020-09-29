import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST
from geonode.groups import views
from geonode.groups.models import GroupProfile
from guardian.decorators import permission_required_or_403

from .tasks import task_sync_geoserver
from .constants import (
    GEOSERVER_SYNC_PERM_CODE,
)

DEPARTMENT_GROUP_PROFILE_SUFFIX = '-editor'
logger = logging.getLogger('geonode_dominode')


class GroupDetailView(views.GroupDetailView):
    template_name = "groups/group_detail_override.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'geoserver_sync_perm_name': GEOSERVER_SYNC_PERM_CODE,
            'is_department_group_profile': self.group.title.endswith(
                DEPARTMENT_GROUP_PROFILE_SUFFIX)
        })
        return ctx


@permission_required_or_403(
    f'groups.{GEOSERVER_SYNC_PERM_CODE}',
    (GroupProfile, 'title', 'group_slug')
)
@require_POST
def sync_geoserver(request, group_slug: str):
    workspace_name = group_slug.replace(DEPARTMENT_GROUP_PROFILE_SUFFIX, '')
    redirect = request.POST.get('redirect')
    logger.debug(f'Workspace name: {workspace_name}')
    logger.info(f'Sending geoserver sync task to the async queue...')
    task_sync_geoserver.delay(workspace_name, request.user.get_username())
    messages.success(
        request, _(
            'GeoServer layers are being synced in the background. '
            'This process may take a while to complete. '
            'You will be notified via email when it is done.'))
    return HttpResponseRedirect(redirect_to=redirect)
