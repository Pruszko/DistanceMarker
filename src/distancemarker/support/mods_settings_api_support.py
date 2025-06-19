import logging

from distancemarker.settings.translations import Tr
from distancemarker.settings.config import g_config
from distancemarker.settings.config_param import g_configParams, createTooltip
from distancemarker.utils import ObservingSemaphore

from gui.modsSettingsApi import g_modsSettingsApi


logger = logging.getLogger(__name__)

modLinkage = "com.github.pruszko.distancemarker"


def registerSoftDependencySupport():
    template = {
        "modDisplayName": Tr.MODNAME,
        "enabled": g_configParams.enabled.defaultMsaValue,
        "column1":
            _createIntroPart() +
            _endSection() +
            _createVisibilitySettings() +
            _endSection() +
            _createPositionSettings(),
        "column2":
            _createVisualSettings()
    }

    # we purposely ignore ModsSettingsAPI capability of saving mod configuration
    # due to config file being "master" configuration
    #
    # also, I don't like going against "standard setup" of ModsSettingsAPI support, but
    # we still treat it only as a GUI, not a configuration framework
    #
    # so we also purposely always call setModTemplate instead of registerCallback
    # to keep always updated GUI template
    g_modsSettingsApi.setModTemplate(modLinkage, template, onModSettingsChanged)


# we cannot update ModsSettingsAPI settings without triggering onModSettingsChanged callback,
# so we will use "semaphore" to control when we want to ignore it
settingsChangedSemaphore = ObservingSemaphore()


# this is called only on manual config reload
def onConfigFileReload():
    msaSettings = {}

    for tokenName, param in g_configParams.items():
        msaSettings[tokenName] = param.msaValue

    logger.info("Synchronizing config file -> ModsSettingsAPI")
    g_modsSettingsApi.updateModSettings(modLinkage, newSettings=msaSettings)


@settingsChangedSemaphore.withIgnoringLock(returnForIgnored=None)
def onModSettingsChanged(linkage, newSettings):
    if linkage != modLinkage:
        return

    try:
        serializedSettings = {}
        for tokenName, param in g_configParams.items():
            if tokenName not in newSettings:
                continue

            value = param.fromMsaValue(newSettings[tokenName])
            jsonValue = param.toJsonValue(value)

            serializedSettings[param.tokenName] = jsonValue

        logger.info("Synchronizing ModsSettingsAPI -> config file")
        g_config.updateConfigSafely(serializedSettings)
    except Exception:
        logger.error("Error occurred while ModsSettingsAPI settings change.", exc_info=True)


def _endSection():
    return _emptyLine() + _horizontalLine()


def _innerSectionSeparator():
    return _emptyLine(4)


def _emptyLine(count=1):
    return [
        {
            "type": "Empty"
        }
    ] * count


def _horizontalLine():
    return [
        {
            "type": "Label",
            "text": "________________________________________"
        }
    ]


def _createIntroPart():
    return [
        {
            "type": "Label",
            "text": Tr.INTRO_LABEL,
            "tooltip": createTooltip(
                header=Tr.INTRO_HEADER,
                body=Tr.INTRO_BODY + "\n",
                note=Tr.INTRO_NOTE
            )
        }
    ]


def _createVisibilitySettings():
    return [{
        "type": "Label",
        "text": Tr.VISIBILITY_SETTINGS_LABEL
    }] + _emptyLine(2) + [
        g_configParams.displayMode.renderParam(
            header=Tr.DISPLAY_MODE_HEADER,
            body=Tr.DISPLAY_MODE_BODY
        ),
        g_configParams.markerTarget.renderParam(
            header=Tr.MARKER_TARGET_HEADER,
            body=Tr.MARKER_TARGET_BODY
        ),
    ]


def _createPositionSettings():
    return [{
        "type": "Label",
        "text": Tr.POSITION_SETTINGS_LABEL
    }] + _emptyLine(2) + [
        g_configParams.anchorPosition.renderParam(
            header=Tr.ANCHOR_POSITION_HEADER,
            body=Tr.ANCHOR_POSITION_BODY
        ),
        g_configParams.lockPositionOffsets.renderParam(
            header=Tr.LOCK_POSITION_OFFSETS_HEADER,
            body=Tr.LOCK_POSITION_OFFSETS_BODY
        ),
        g_configParams.anchorHorizontalOffset.renderParam(
            header=Tr.ANCHOR_HORIZONTAL_OFFSET_HEADER,
            body=Tr.ANCHOR_HORIZONTAL_OFFSET_BODY
        ),
        g_configParams.anchorVerticalOffset.renderParam(
            header=Tr.ANCHOR_VERTICAL_OFFSET_HEADER,
            body=Tr.ANCHOR_VERTICAL_OFFSET_BODY
        )
    ]


def _createVisualSettings():
    return [{
        "type": "Label",
        "text": Tr.VISUAL_SETTINGS_LABEL
    }] + _emptyLine(2) + [
        g_configParams.decimalPrecision.renderParam(
            header=Tr.DECIMAL_PRECISION_HEADER,
            body=Tr.DECIMAL_PRECISION_BODY
        ),
        g_configParams.textSize.renderParam(
            header=Tr.TEXT_SIZE_HEADER,
            body=Tr.TEXT_SIZE_BODY
        ),
        g_configParams.textColor.renderParam(
            header=Tr.TEXT_COLOR_HEADER,
            body=Tr.TEXT_COLOR_BODY
        ),
        g_configParams.textAlpha.renderParam(
            header=Tr.TEXT_ALPHA_HEADER,
            body=Tr.TEXT_ALPHA_BODY
        ),
        g_configParams.drawTextOutline.renderParam(
            header=Tr.DRAW_TEXT_OUTLINE_HEADER,
            body=Tr.DRAW_TEXT_OUTLINE_BODY
        ),
        g_configParams.drawTextShadow.renderParam(
            header=Tr.DRAW_TEXT_SHADOW_HEADER,
            body=Tr.DRAW_TEXT_SHADOW_BODY
        ),
        g_configParams.drawDistanceUnit.renderParam(
            header=Tr.DRAW_DISTANCE_UNIT_HEADER,
            body=Tr.DRAW_DISTANCE_UNIT_BODY
        )
    ]


# UtilsManager
def _createImg(src, width=None, height=None, vSpace=None, hSpace=None):
    template = "<img src='{0}' "

    absoluteUrl = "img://gui/distancemarker/" + src
    if width is not None:
        template += "width='{1}' "
    if height is not None:
        template += "height='{2}' "
    if vSpace is not None:
        template += "vspace='{3}' "
    if hSpace is not None:
        template += "hspace='{4}'  "

    template += "/>"
    return template.format(absoluteUrl, width, height, vSpace, hSpace)
