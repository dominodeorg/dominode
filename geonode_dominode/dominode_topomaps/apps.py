import logging

from django.apps import AppConfig

from dominode_topomaps.constants import TOPOMAP_DOWNLOAD_PERM_CODE

logger = logging.getLogger(__name__)


def run_setup_hooks(*args, **kwargs):
    try:
        create_topomap_download_permission()
    except BaseException:
        # content type initialization must run after first db initializations
        pass


class DominodeTopomapsConfig(AppConfig):
    name = 'dominode_topomaps'

    def ready(self):
        super(DominodeTopomapsConfig, self).ready()
        run_setup_hooks()


def create_topomap_download_permission():
    from django.contrib.auth.models import ContentType, Permission
    from geonode.layers.models import Layer
    content_type = ContentType.objects.get_for_model(Layer)
    perm, created = Permission.objects.get_or_create(
        codename=TOPOMAP_DOWNLOAD_PERM_CODE,
        name='Can download topomap',
        content_type=content_type
    )
    if created:
        logger.info(f'Created new permission: {perm}')
    return perm
