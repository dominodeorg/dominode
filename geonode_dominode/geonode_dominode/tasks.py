from io import StringIO

from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from geonode.geoserver.helpers import gs_slurp

from geonode_dominode.celeryapp import app

logger = get_task_logger(__name__)


@app.task(queue='geonode_dominode')
def task_cli_sync_geoserver(workspace_name, username):
    # construct management command arguments
    out = StringIO()
    result = gs_slurp(
        ignore_errors=False,
        verbosity=1,
        owner=username,
        console=out,
        workspace=workspace_name,
        store=None,
        filter=None,
        skip_unadvertised=True,
        skip_geonode_registered=True,
        remove_deleted=True,
        permissions={
            'users': {
                'AnonymousUser': []
            }
        },
        execute_signals=True)

    # Send email to user
    User = get_user_model()
    user = User.objects.get(username=username)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = '{} <{}>'.format(username, user.email)
    subject = _('[Task Complete] Sync GeoServer')
    context = {
        'username': username,
        'output': out.getvalue(),
        'result': result
    }
    text_content = render_to_string(
        'email/task_complete.txt', context=context)
    html_content = render_to_string(
        'email/task_complete.html', context=context)
    send_mail(
        subject,
        text_content,
        from_email,
        [to_email],
        html_message=html_content)
    return True
