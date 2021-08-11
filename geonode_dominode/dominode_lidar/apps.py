import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DominodeLidarConfig(AppConfig):
    name = 'dominode_lidar'