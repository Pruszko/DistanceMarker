import BigWorld
import GUI
import SCALEFORM
import Math
import logging

from gui import DEPTH_OF_VehicleMarker, InputHandler
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent, ExternalFlashSettings
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

logger = logging.getLogger(__name__)


class DistanceMarkerFlashMeta(BaseDAAPIModule):
    pass


class DistanceMarkerFlash(ExternalFlashComponent, DistanceMarkerFlashMeta):

    def __init__(self):
        super(DistanceMarkerFlash, self).__init__(
            ExternalFlashSettings("DistanceMarkerFlash",
                                  "DistanceMarkerFlash.swf",
                                  "root", None)
        )

        self.createExternalComponent()
        self._configureApp()

        self._isAltPressed = False
        self._emptyList = []

        screenResolution = GUI.screenResolution()

        # state per frame render
        self._tempMatrix = Math.Matrix()
        self._currentViewProjectionMatrix = Math.Matrix()

        self._currentScreenWidth = screenResolution[0]
        self._currentScreenHeight = screenResolution[1]
        self._currentFrameData = {
            "screenWidth": self._currentScreenWidth,
            "screenHeight": self._currentScreenHeight,
            "observedVehicles": self._emptyList
        }

        InputHandler.g_instance.onKeyUp += self._onKeyUp
        InputHandler.g_instance.onKeyDown += self._onKeyDown

    def close(self):
        InputHandler.g_instance.onKeyUp -= self._onKeyUp
        InputHandler.g_instance.onKeyDown -= self._onKeyDown

        super(DistanceMarkerFlash, self).close()

    def _configureApp(self):
        # this is needed, otherwise everything will be white
        self.movie.backgroundAlpha = 0.0

        # scales the app to match 1:1 pixels of app to screen
        self.movie.scaleMode = SCALEFORM.eMovieScaleMode.NO_SCALE

        # this does something
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE

        # depth sorting, required to be placed properly between other apps
        self.component.position.z = DEPTH_OF_VehicleMarker - 0.02

        # this also does something
        self.component.focus = False
        self.component.moveFocus = False

        # those below just don't work
        # I've lost way too much time to attempt to do so
        #
        # it is properly positioned by DistanceMarkerFlash in AS3 as a workaround
        #
        # self.component.horizontalPositionMode = GUI.Simple.ePositionMode.CLIP
        # self.component.verticalPositionMode = GUI.Simple.ePositionMode.CLIP
        # self.component.horizontalAnchor = GUI.Simple.eHAnchor.LEFT
        # self.component.verticalAnchor = GUI.Simple.eVAnchor.TOP
        #
        # self.component.widthMode = GUI.Simple.eSizeMode.CLIP
        # self.component.heightMode = GUI.Simple.eSizeMode.CLIP
        #
        # self.component.position[0] = -1
        # self.component.position[1] = 1
        #
        # self.component.size = (1, 1)

    def _onKeyUp(self, event):
        self._isAltPressed = event.isAltDown()

    def _onKeyDown(self, event):
        self._isAltPressed = event.isAltDown()

    # IMPORTANT
    # this method is called by a swf app every frame in-between game logic
    # even on its pause in replays
    #
    # this will be called extremely frequently
    # we have to be very concise in terms of optimisation and object allocation
    # the same goes for SWF app
    def py_requestFrameData(self):
        screenResolution = GUI.screenResolution()

        self._currentFrameData["screenWidth"] = self._currentScreenWidth = screenResolution[0]
        self._currentFrameData["screenHeight"] = self._currentScreenHeight = screenResolution[1]
        self._currentFrameData["observedVehicles"] = self._emptyList

        if not self._isAltPressed:
            # if ALT key is not pressed, return small constant data
            return self._currentFrameData

        # player may not be present during context switching (for example replay backward rewind)
        if BigWorld.player() is None:
            return self._currentFrameData

        currentVehicleID = -1
        currentVehicle = BigWorld.player().getVehicleAttached()

        if currentVehicle is not None:
            # use vehicle id for exclusion not to display marker for our tank
            currentVehicleID = currentVehicle.id

            playerPositionProvider = currentVehicle.matrix
        elif BigWorld.camera() is not None:
            # player vehicle may not be present yet
            #
            # use camera position if available
            playerPositionProvider = BigWorld.camera().matrix
        else:
            # if even this is not present, stop displaying markers until anything is present
            return self._currentFrameData

        self._tempMatrix.set(playerPositionProvider)
        currentPlayerPosition = self._tempMatrix.translation

        self._updateViewProjectionMatrix()

        self._currentFrameData["observedVehicles"] = [
            self._serializeObservedVehicle(currentPlayerPosition, vehicle)
            for vehicle in BigWorld.player().vehicles
            if vehicle.isAlive() and vehicle.id != currentVehicleID
        ]

        return self._currentFrameData

    def _updateViewProjectionMatrix(self):
        proj = BigWorld.projection()
        aspect = BigWorld.getAspectRatio()

        self._currentViewProjectionMatrix.perspectiveProjection(proj.fov, aspect, proj.nearPlane, proj.farPlane)
        self._currentViewProjectionMatrix.preMultiply(BigWorld.camera().matrix)

    def _serializeObservedVehicle(self, currentPlayerPosition, vehicle):
        # projected point has scaled x and y between -1 and 1
        # where x starts from left -1 to right 1
        # and y starts from bottom -1 to top 1
        #
        # for AS3, we will need them scaled between 0 and 1 and have inverted y
        # because (0, 0) point in Flash starts from top left
        #
        # here we will only normalize it between 0 and 1 and invert y
        # and swf app will use it properly according to full screen
        self._tempMatrix.set(vehicle.matrix)
        vehiclePosition = self._tempMatrix.translation

        currentDistance = (vehiclePosition - currentPlayerPosition).length
        vehiclePosition.y += 2.0

        projectedVehiclePosition2d, isPointOnScreen = self._projectPointWithVisibilityResult(vehiclePosition)

        normalizedVehiclePositionX = 0.5 + 0.5 * projectedVehiclePosition2d.x
        normalizedVehiclePositionY = 0.5 - 0.5 * projectedVehiclePosition2d.y

        x = normalizedVehiclePositionX * self._currentScreenWidth
        y = normalizedVehiclePositionY * self._currentScreenHeight

        return {
            "id": str(vehicle.id),
            "currentDistance": currentDistance,
            "x": x,
            "y": y,
            "isVisible": isPointOnScreen
        }

    def _projectPointWithVisibilityResult(self, point):
        posInClip = Math.Vector4(point.x, point.y, point.z, 1)
        posInClip = self._currentViewProjectionMatrix.applyV4Point(posInClip)

        if point.lengthSquared != 0.0:
            visible = posInClip.w > 0 and -1 <= posInClip.x / posInClip.w <= 1 and -1 <= posInClip.y / posInClip.w <= 1
        else:
            visible = False

        if posInClip.w != 0:
            posInClip = posInClip.scale(1 / posInClip.w)

        return posInClip, visible
