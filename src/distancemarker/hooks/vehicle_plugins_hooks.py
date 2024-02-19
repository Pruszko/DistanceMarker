from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin

from distancemarker.utils import overrideIn
from distancemarker.flash.distance_marker_flash import DistanceMarkerFlash

g_distanceMarkerFlash = None


@overrideIn(VehicleMarkerPlugin)
def start(func, self):
    func(self)

    global g_distanceMarkerFlash
    if g_distanceMarkerFlash is None:
        g_distanceMarkerFlash = DistanceMarkerFlash()
        g_distanceMarkerFlash.active(True)


@overrideIn(VehicleMarkerPlugin)
def stop(func, self):
    func(self)

    global g_distanceMarkerFlash
    if g_distanceMarkerFlash is not None:
        g_distanceMarkerFlash.close()
        g_distanceMarkerFlash = None
