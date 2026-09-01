from AvatarInputHandler import AvatarInputHandler
from Event import Event

from distancemarker.utils import overrideIn


onMouseEvent = Event()


@overrideIn(AvatarInputHandler)
def handleMouseEvent(func, self, event):
    result = func(self, event)

    onMouseEvent(event.dx, event.dy)

    return result
