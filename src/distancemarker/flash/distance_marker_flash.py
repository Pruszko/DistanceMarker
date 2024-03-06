import BigWorld
import GUI
import Keys
import SCALEFORM
import Math
import logging

from Event import EventManager, Event
from gui import DEPTH_OF_VehicleMarker, InputHandler
from gui.Scaleform.daapi.view.external_components import ExternalFlashComponent, ExternalFlashSettings
from gui.Scaleform.flash_wrapper import InputKeyMode
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

from distancemarker.flash import serializeConfigParams
from distancemarker.settings import clamp
from distancemarker.settings.config import g_config
from distancemarker.settings.config_param import g_configParams, DisplayMode, AnchorPosition, MarkerTarget

logger = logging.getLogger(__name__)


# very simple pool to avoid allocating dict that much
class _SimpleDictPool(object):

    def __init__(self):
        self.pool = []

    def __getitem__(self, item):
        return self.pool[item]

    def ensureLength(self, length):
        lackingCount = length - len(self.pool)
        if lackingCount <= 0:
            return

        for i in range(lackingCount):
            self.pool.append({})


class DistanceMarkerFlashMeta(BaseDAAPIModule):

    def as_applyConfig(self, serializedConfig):
        if self._isDAAPIInited():
            return self.flashObject.as_applyConfig(serializedConfig)

    def as_isPointInMarker(self, mouseX, mouseY):
        if self._isDAAPIInited():
            return self.flashObject.as_isPointInMarker(mouseX, mouseY)


class DistanceMarkerFlash(ExternalFlashComponent, DistanceMarkerFlashMeta):

    _eventManager = EventManager()

    onMouseEvent = Event(_eventManager)

    def __init__(self, vehicleMarkerClass):
        super(DistanceMarkerFlash, self).__init__(
            ExternalFlashSettings("DistanceMarkerFlash",
                                  "DistanceMarkerFlash.swf",
                                  "root", None)
        )

        # VehicleMarker class
        self._vehicleMarkerClass = vehicleMarkerClass

        self.createExternalComponent()
        self._configureApp()

        # config state
        self._displayMode = g_configParams.displayMode()
        self._markerTarget = g_configParams.markerTarget()
        self._anchorPosition = g_configParams.anchorPosition()
        self._isOffsetChangeAllowed = not g_configParams.lockPositionOffsets()
        self._currentHorizontalAnchorOffset = g_configParams.anchorHorizontalOffset()
        self._currentVerticalAnchorOffset = -1 * g_configParams.anchorVerticalOffset()
        self._wereOffsetsEdited = False

        self._isDisplayingMarkers = self._displayMode == DisplayMode.ALWAYS
        self._isMarkerDragging = False

        if self._anchorPosition == AnchorPosition.TANK_MARKER:
            self._markerPositionProvider = self._vehicleMarkerPositionProvider
        elif self._anchorPosition == AnchorPosition.TANK_CENTER:
            self._markerPositionProvider = self._vehicleCenterPositionProvider
        else:
            self._markerPositionProvider = self._vehicleBottomPositionProvider

        # objects used for optimizations
        self._currentViewProjectionMatrix = Math.Matrix()
        self._tempMatrix = Math.Matrix()
        self._emptyList = []
        self._dictPool = _SimpleDictPool()

        # state per frame render
        screenResolution = GUI.screenResolution()
        self._currentScreenWidth = screenResolution[0]
        self._currentScreenHeight = screenResolution[1]
        self._currentFrameData = {
            "screenWidth": self._currentScreenWidth,
            "screenHeight": self._currentScreenHeight,
            "observedVehicles": self._emptyList
        }

        InputHandler.g_instance.onKeyUp += self._onKeyUp
        InputHandler.g_instance.onKeyDown += self._onKeyDown

        serializedConfig = serializeConfigParams()
        self.as_applyConfig(serializedConfig)

    def close(self):
        if self._isMarkerDragging:
            self.onMouseEvent -= self._onMarkerDragging
            self._isMarkerDragging = False

        InputHandler.g_instance.onKeyUp -= self._onKeyUp
        InputHandler.g_instance.onKeyDown -= self._onKeyDown

        super(DistanceMarkerFlash, self).close()

        if self._wereOffsetsEdited:
            g_configParams.anchorHorizontalOffset.value = self._currentHorizontalAnchorOffset
            g_configParams.anchorVerticalOffset.value = -1 * self._currentVerticalAnchorOffset
            g_config.persistParamsSafely()

    def _configureApp(self):
        # this is needed, otherwise everything will be white
        self.movie.backgroundAlpha = 0.0

        # scales the app to match 1:1 pixels of app to screen
        self.movie.scaleMode = SCALEFORM.eMovieScaleMode.NO_SCALE

        # this does something
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE

        # depth sorting, required to be placed properly between other apps
        self.component.position.z = DEPTH_OF_VehicleMarker - 0.02

        # don't capture input events
        # we have to deal with them python-side anyway
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
        if self._displayMode == DisplayMode.ON_ALT_PRESSED:
            self._isDisplayingMarkers = event.isAltDown()

        if self._isMarkerDragging and self._isLeftMouseButton(event):
            self._isMarkerDragging = False
            self.onMouseEvent -= self._onMarkerDragging

    def _onKeyDown(self, event):
        if self._displayMode == DisplayMode.ON_ALT_PRESSED:
            self._isDisplayingMarkers = event.isAltDown()

        cursor = GUI.mcursor()

        if (self._isDisplayingMarkers and self._isOffsetChangeAllowed
                and event.isCtrlDown() and self._isLeftMouseButton(event)
                and cursor.inWindow and cursor.inFocus):
            mouseX, mouseY = cursor.position
            screenX, screenY = self._toScreenPixelPosition(mouseX, mouseY)

            if self.as_isPointInMarker(screenX, screenY):
                self._isMarkerDragging = True
                self.onMouseEvent += self._onMarkerDragging

    @staticmethod
    def _isLeftMouseButton(event):
        return event.isMouseButton() and event.key == Keys.KEY_LEFTMOUSE

    def _onMarkerDragging(self, dx, dy):
        self._currentHorizontalAnchorOffset = clamp(g_configParams.anchorHorizontalOffset.minValue,
                                                    self._currentHorizontalAnchorOffset + dx,
                                                    g_configParams.anchorHorizontalOffset.maxValue)
        self._currentVerticalAnchorOffset = clamp(g_configParams.anchorVerticalOffset.minValue,
                                                  self._currentVerticalAnchorOffset + dy,
                                                  g_configParams.anchorVerticalOffset.maxValue)

        self._wereOffsetsEdited = True

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
        self._currentFrameData["observedVehicles"] = self._emptyList  # avoid allocating empty list in most cases

        if not self._isDisplayingMarkers:
            # if markers are not displayed, return small constant data
            return self._currentFrameData

        # player may not be present during context switching (for example replay backward rewind)
        player = BigWorld.player()
        if player is None:
            return self._currentFrameData

        # if GUI is hidden, hide markers as well
        avatarInputHandler = player.inputHandler
        if avatarInputHandler is not None and not avatarInputHandler.isGuiVisible:
            return self._currentFrameData

        currentVehicleID = -1
        currentVehicle = player.getVehicleAttached()

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

        vehicles = BigWorld.player().vehicles

        # to avoid allocating dict that much, we will use simple dict pooling
        #
        # to keep it fast and simple, following code contract is made:
        # - ensure pool length to be at least the length of vehicles set being serialized every frame
        #   - this in most common cases won't make any new objects
        # - every vehicle serialization method call must use independent dict from that pool
        # - every dict must have same structure
        #
        # we don't need "return to pool" logic, and we don't even want to do it
        # because returned dict must be valid until it is at least sent and serialized to SWF app
        # we can't hook into that when it happens
        # so to keep things simple, leave resulting objects as they are
        #
        # after all that, we can safely reference same dicts again in next frame
        self._dictPool.ensureLength(len(vehicles))
        self._currentFrameData["observedVehicles"] = [
            self._serializeObservedVehicle(currentPlayerPosition, vehicle, self._dictPool[poolIndex])
            for poolIndex, vehicle in enumerate(vehicles)
            if self._shouldDisplayForVehicle(vehicle, currentVehicleID)
        ]

        return self._currentFrameData

    def _shouldDisplayForVehicle(self, vehicle, currentVehicleID):
        if not vehicle.isAlive() or vehicle.id == currentVehicleID:
            return False

        if self._markerTarget == MarkerTarget.ALLY_AND_ENEMY:
            return True

        return BigWorld.player().team != vehicle.publicInfo["team"]

    def _updateViewProjectionMatrix(self):
        proj = BigWorld.projection()
        aspect = BigWorld.getAspectRatio()

        # basically: camera matrix * perspective projection = matrix used for 3d -> 2d projection
        self._currentViewProjectionMatrix.perspectiveProjection(proj.fov, aspect, proj.nearPlane, proj.farPlane)
        self._currentViewProjectionMatrix.preMultiply(BigWorld.camera().matrix)

    def _serializeObservedVehicle(self, currentPlayerPosition, vehicle, pooledVehicleDict):
        self._tempMatrix.set(vehicle.matrix)
        vehiclePosition = self._tempMatrix.translation

        currentDistance = (vehiclePosition - currentPlayerPosition).length

        markerPosition3d = self._markerPositionProvider(vehicle)
        projectedMarkerPosition2d, isPointOnScreen = self._projectPointWithVisibilityResult(markerPosition3d)

        x, y = self._toScreenPixelPosition(projectedMarkerPosition2d.x, projectedMarkerPosition2d.y)

        # modify and return pooled dict
        pooledVehicleDict["id"] = str(vehicle.id),
        pooledVehicleDict["currentDistance"] = currentDistance,
        pooledVehicleDict["x"] = x + self._currentHorizontalAnchorOffset,
        pooledVehicleDict["y"] = y + self._currentVerticalAnchorOffset,
        pooledVehicleDict["isVisible"] = isPointOnScreen

        return pooledVehicleDict

    def _vehicleMarkerPositionProvider(self, vehicle):
        # fetchMatrixProvider is decently cheap to call
        # at least I hope so
        # who knows what GUI.WGVehicleMarkersMatrixProvider does under the hood
        vehicleMarkerMatrixProvider = self._vehicleMarkerClass.fetchMatrixProvider(vehicle)

        self._tempMatrix.set(vehicleMarkerMatrixProvider)
        return self._tempMatrix.translation

    def _vehicleCenterPositionProvider(self, vehicle):
        self._tempMatrix.set(vehicle.matrix)
        vehicleCenterPosition = self._tempMatrix.translation
        vehicleCenterPosition.y += 2.0

        return vehicleCenterPosition

    def _vehicleBottomPositionProvider(self, vehicle):
        self._tempMatrix.set(vehicle.matrix)
        vehicleCenterPosition = self._tempMatrix.translation
        vehicleCenterPosition.y -= 1.0

        return vehicleCenterPosition

    # projected point and mouse point events have scaled x and y between -1 and 1
    # where x starts from left -1 to right 1
    # and y starts from bottom -1 to top 1
    #
    # for AS3, we will need them scaled between 0 and 1 and have inverted y
    # because (0, 0) point in Flash starts from top left
    #
    # then it is mapped to full screen resolution which swf app is aware of

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

    def _toScreenPixelPosition(self, x, y):
        normalizedX = 0.5 + 0.5 * x
        normalizedY = 0.5 - 0.5 * y

        # reuse any cached screen resolution there is from frame data requests
        return (normalizedX * self._currentScreenWidth,
                normalizedY * self._currentScreenHeight)
