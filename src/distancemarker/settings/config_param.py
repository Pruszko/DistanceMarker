from distancemarker.settings.config_param_types import *
from distancemarker.settings.translations import Tr


class DisplayMode(object):

    ALWAYS = "always"
    ON_ALT_PRESSED = "on-alt-pressed"


class AnchorPosition(object):

    TANK_MARKER = "tank-marker"
    TANK_CENTER = "tank-center"
    TANK_BOTTOM = "tank-bottom"


class MarkerTarget(object):

    ALLY_AND_ENEMY = "ally-and-enemy"
    ONLY_ENEMY = "only-enemy"


class ConfigParams(object):

    def __init__(self):
        self.enabled = BooleanParam(
            ["enabled"],
            defaultValue=True, disabledValue=False
        )

        # visibility settings
        self.displayMode = OptionsParam(
            ["display-mode"],
            [
                Option(DisplayMode.ALWAYS, 0, Tr.DISPLAY_MODE_OPTION_ALWAYS),
                Option(DisplayMode.ON_ALT_PRESSED, 1, Tr.DISPLAY_MODE_OPTION_ON_ALT_PRESSED)
            ],
            defaultValue=DisplayMode.ALWAYS
        )
        self.markerTarget = OptionsParam(
            ["marker-target"],
            [
                Option(MarkerTarget.ALLY_AND_ENEMY, 0, Tr.MARKER_TARGET_OPTION_ALLY_AND_ENEMY),
                Option(MarkerTarget.ONLY_ENEMY, 1, Tr.MARKER_TARGET_OPTION_ONLY_ENEMY)
            ],
            defaultValue=MarkerTarget.ALLY_AND_ENEMY
        )

        # position settings
        self.anchorPosition = OptionsParam(
            ["anchor-position"],
            [
                Option(AnchorPosition.TANK_MARKER, 0, Tr.ANCHOR_POSITION_OPTION_TANK_MARKER),
                Option(AnchorPosition.TANK_CENTER, 1, Tr.ANCHOR_POSITION_OPTION_TANK_CENTER),
                Option(AnchorPosition.TANK_BOTTOM, 2, Tr.ANCHOR_POSITION_OPTION_TANK_BOTTOM)
            ],
            defaultValue=AnchorPosition.TANK_MARKER
        )
        self.lockPositionOffsets = BooleanParam(
            ["lock-position-offsets"],
            defaultValue=False
        )
        self.anchorHorizontalOffset = StepperParam(
            ["anchor-horizontal-offset"],
            castFunction=int,
            minValue=-150, step=1, maxValue=150,
            defaultValue=24
        )
        self.anchorVerticalOffset = StepperParam(
            ["anchor-vertical-offset"],
            castFunction=int,
            minValue=-150, step=1, maxValue=150,
            defaultValue=16
        )

        # visual settings
        self.decimalPrecision = SliderParam(
            ["decimal-precision"],
            castFunction=int,
            minValue=0, step=1, maxValue=3,
            defaultValue=0
        )
        self.textSize = SliderParam(
            ["text-size"],
            castFunction=int,
            minValue=6, step=1, maxValue=24,
            defaultValue=11
        )
        self.textColor = ColorParam(
            ["text-color"],
            defaultValue=(255, 255, 255)
        )
        self.textAlpha = SliderParam(
            ["text-alpha"],
            castFunction=float,
            minValue=0.0, step=0.01, maxValue=1.0,
            defaultValue=1.0
        )
        self.drawTextOutline = BooleanParam(
            ["draw-text-outline"],
            defaultValue=True
        )
        self.drawTextShadow = BooleanParam(
            ["draw-text-shadow"],
            defaultValue=True
        )
        self.drawDistanceUnit = BooleanParam(
            ["draw-distance-unit"],
            defaultValue=True
        )

    @staticmethod
    def items():
        return PARAM_REGISTRY.items()


g_configParams = ConfigParams()
