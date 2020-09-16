from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required, login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from geonode.groups import views
from django.utils.translation import ugettext_lazy as _

import logging

from geonode_dominode.tasks import task_sync_geoserver

logger = logging.getLogger('geonode_dominode')


class GroupDetailView(views.GroupDetailView):
    """
    Mixes a detail view (the group) with a ListView (the members).
    """

    model = get_user_model()
    template_name = "groups/group_detail_override.html"
    paginate_by = None
    group = None


@login_required
@permission_required('groups.can_sync_geoserver')
def sync_geoserver(request):
    """
    :type request: django.http.HttpRequest
    """
    if request.method == 'POST':
        group_slug = request.POST.get('group-slug')
        workspace_name = group_slug.replace('-editor', '')
        redirect = request.POST.get('redirect')
        user = request.user.get_username()
        logger.debug('Receiving GeoServer sync requests.')
        logger.debug('Group name: {}'.format(group_slug))
        logger.debug('Workspace name: {}'.format(workspace_name))
        logger.debug('User name: {}'.format(user))
        task_sync_geoserver.delay(workspace_name, user)
        messages.success(
            request, _(
                'GeoServer layers are being synced in the background. '
                'This process may take a while to complete. '
                'You will be notified via email when it is done.'))
        return HttpResponseRedirect(redirect_to=redirect)
    return HttpResponseBadRequest()
