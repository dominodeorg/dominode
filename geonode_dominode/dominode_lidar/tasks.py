from celery.utils.log import get_task_logger
from django.template.loader import render_to_string
from geonode.layers.models import Layer

from geonode_dominode.celeryapp import app
from .models import PublishedLidarIndexSheetLayer

logger = get_task_logger(__name__)


@app.task(queue='geonode_dominode')
def add_custom_featureinfo_template_lidar():
    """
    Add custom featureinfo template to layers that represent published lidar

    Published lidar layers feature download links that allow users to
    navigate to sheet detail page, where they may download individual lidar las file
    . The default presentation of these links is just to render them as
    normal text. This task provides a custom representation that uses proper
    html anchor tags to render these download links as buttons.

    """

    for lidar_layer in PublishedLidarIndexSheetLayer.objects.all():
        layer: Layer = lidar_layer.layer
        if layer.featureinfo_custom_template in ('', None):
            logger.debug(
                f'Adding custom featureinfo template to '
                f'layer {layer!r}...'
            )
            rendered = render_to_string('dominode_lidar/featureinfo.html')
            layer.featureinfo_custom_template = rendered
            layer.use_featureinfo_custom_template = True
            layer.save()
