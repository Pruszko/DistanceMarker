from AvatarInputHandler import AvatarInputHandler
from Event import Event

from distancemarker.utils import overrideIn


onMouseEvent = Event()


@overrideIn(AvatarInputHandler)
def handleMouseEvent(func, self, dx, dy, dz):
    result = func(self, dx, dy, dz)

    onMouseEvent(dx, dy)

    return result
