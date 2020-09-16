from io import StringIO

from celery.utils.log import get_task_logger
from django.core import management

from geonode_dominode.celeryapp import app

logger = get_task_logger(__name__)


@app.task(queue='geonode_dominode')
def task_cli_sync_geoserver(workspace_name, username):
    # construct management command arguments
    out, err = StringIO(), StringIO()
    result = management.call_command(
        'updatelayers',
        skip_geonode_registered=True,
        skip_unadvertised=True,
        remove_deleted=True,
        workspace=workspace_name,
        user=username,
        permissions='{"users": {"AnonymousUser": []}}',
        stdout=out,
        stderr=err
    )
    return out.getvalue(), err.getvalue()
