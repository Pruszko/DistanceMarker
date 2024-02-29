from AvatarInputHandler import AvatarInputHandler

from distancemarker.flash.distance_marker_flash import DistanceMarkerFlash
from distancemarker.utils import overrideIn


@overrideIn(AvatarInputHandler)
def handleMouseEvent(func, self, dx, dy, dz):
    result = func(self, dx, dy, dz)

    DistanceMarkerFlash.onMouseEvent(dx, dy)

    return result
