import logging

from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin

from distancemarker.settings.config_param import g_configParams
from distancemarker.utils import overrideIn
from distancemarker.flash.distance_marker_flash import DistanceMarkerFlash


logger = logging.getLogger(__name__)


g_distanceMarkerFlash = None


@overrideIn(VehicleMarkerPlugin)
def start(func, self):
    func(self)

    try:
        global g_distanceMarkerFlash
        if g_distanceMarkerFlash is None and g_configParams.enabled():
            g_distanceMarkerFlash = DistanceMarkerFlash(self._clazz)
            g_distanceMarkerFlash.active(True)
    except:
        logger.error("Failed to create distance marker app", exc_info=True)


@overrideIn(VehicleMarkerPlugin)
def stop(func, self):
    func(self)

    try:
        global g_distanceMarkerFlash
        if g_distanceMarkerFlash is not None:
            g_distanceMarkerFlash.close()
            g_distanceMarkerFlash = None
    except:
        logger.error("Failed to close distance marker app", exc_info=True)
