import json
import logging

import ResMgr
from helpers import getClientLanguage


logger = logging.getLogger(__name__)

# if this is set to some language code, then below code will treat game language as that
# used only for debugging
DEBUG_LANGUAGE = None


DEFAULT_TRANSLATIONS_MAP = {}
TRANSLATIONS_MAP = {}


def loadTranslations():
    defaultTranslationsMap = _loadLanguage("en")

    global DEFAULT_TRANSLATIONS_MAP
    DEFAULT_TRANSLATIONS_MAP = defaultTranslationsMap if defaultTranslationsMap is not None else {}

    if DEBUG_LANGUAGE is not None:
        language = DEBUG_LANGUAGE
        logger.info("Client language (debug): %s", language)
    else:
        language = getClientLanguage()
        logger.info("Client language: %s", language)

    translationsMap = _loadLanguage(language)

    if translationsMap is not None:
        logger.info("Translations for language %s detected" % language)
        global TRANSLATIONS_MAP
        TRANSLATIONS_MAP = translationsMap
    else:
        logger.info("Translations for language %s not present, fallback to en" % language)


def _loadLanguage(language):
    translationsRes = ResMgr.openSection("gui/distancemarker/translations/translations_%s.json" % language)
    if translationsRes is None:
        return None

    translationsStr = str(translationsRes.asBinary)
    return json.loads(translationsStr, encoding="UTF-8")


class TranslationBase(object):

    def __init__(self, tokenName):
        self._tokenName = tokenName
        self._value = None

    def __get__(self, instance, owner=None):
        if self._value is None:
            self._value = self._generateTranslation()
        return self._value

    def _generateTranslation(self):
        raise NotImplementedError()


class TranslationElement(TranslationBase):

    def _generateTranslation(self):
        global TRANSLATIONS_MAP
        if self._tokenName in TRANSLATIONS_MAP:
            return TRANSLATIONS_MAP[self._tokenName]

        global DEFAULT_TRANSLATIONS_MAP
        return DEFAULT_TRANSLATIONS_MAP[self._tokenName]


class TranslationList(TranslationBase):

    def _generateTranslation(self):
        global TRANSLATIONS_MAP
        if self._tokenName in TRANSLATIONS_MAP:
            return "".join(TRANSLATIONS_MAP[self._tokenName])

        global DEFAULT_TRANSLATIONS_MAP
        return "".join(DEFAULT_TRANSLATIONS_MAP[self._tokenName])


class Tr(object):
    # common
    MODNAME = TranslationElement("modname")
    CHECKED = TranslationElement("checked")
    UNCHECKED = TranslationElement("unchecked")
    DEFAULT_VALUE = TranslationElement("defaultValue")

    # intro
    INTRO_LABEL = TranslationElement("intro.label")
    INTRO_HEADER = TranslationElement("intro.header")
    INTRO_BODY = TranslationList("intro.body")
    INTRO_NOTE = TranslationList("intro.note")

    # visibility settings
    VISIBILITY_SETTINGS_LABEL = TranslationElement("visibility-settings.label")

    DISPLAY_MODE_HEADER = TranslationElement("display-mode.header")
    DISPLAY_MODE_BODY = TranslationList("display-mode.body")
    DISPLAY_MODE_OPTION_ALWAYS = TranslationElement("display-mode.option.always")
    DISPLAY_MODE_OPTION_ON_ALT_PRESSED = TranslationElement("display-mode.option.on-alt-pressed")

    MARKER_TARGET_HEADER = TranslationElement("marker-target.header")
    MARKER_TARGET_BODY = TranslationList("marker-target.body")
    MARKER_TARGET_OPTION_ALLY_AND_ENEMY = TranslationElement("marker-target.option.ally-and-enemy")
    MARKER_TARGET_OPTION_ONLY_ENEMY = TranslationElement("marker-target.option.only-enemy")

    # position settings
    POSITION_SETTINGS_LABEL = TranslationElement("position-settings.label")

    ANCHOR_POSITION_HEADER = TranslationElement("anchor-position.header")
    ANCHOR_POSITION_BODY = TranslationList("anchor-position.body")
    ANCHOR_POSITION_OPTION_TANK_MARKER = TranslationElement("anchor-position.option.tank-marker")
    ANCHOR_POSITION_OPTION_TANK_CENTER = TranslationElement("anchor-position.option.tank-center")
    ANCHOR_POSITION_OPTION_TANK_BOTTOM = TranslationElement("anchor-position.option.tank-bottom")

    LOCK_POSITION_OFFSETS_HEADER = TranslationElement("lock-position-offsets.header")
    LOCK_POSITION_OFFSETS_BODY = TranslationList("lock-position-offsets.body")

    ANCHOR_HORIZONTAL_OFFSET_HEADER = TranslationElement("anchor-horizontal-offset.header")
    ANCHOR_HORIZONTAL_OFFSET_BODY = TranslationList("anchor-horizontal-offset.body")

    ANCHOR_VERTICAL_OFFSET_HEADER = TranslationElement("anchor-vertical-offset.header")
    ANCHOR_VERTICAL_OFFSET_BODY = TranslationList("anchor-vertical-offset.body")

    # visual settings
    VISUAL_SETTINGS_LABEL = TranslationElement("visual-settings.label")

    DECIMAL_PRECISION_HEADER = TranslationElement("decimal-precision.header")
    DECIMAL_PRECISION_BODY = TranslationList("decimal-precision.body")

    TEXT_SIZE_HEADER = TranslationElement("text-size.header")
    TEXT_SIZE_BODY = TranslationList("text-size.body")

    TEXT_COLOR_HEADER = TranslationElement("text-color.header")
    TEXT_COLOR_BODY = TranslationList("text-color.body")

    TEXT_ALPHA_HEADER = TranslationElement("text-alpha.header")
    TEXT_ALPHA_BODY = TranslationList("text-alpha.body")

    DRAW_TEXT_SHADOW_HEADER = TranslationElement("draw-text-shadow.header")
    DRAW_TEXT_SHADOW_BODY = TranslationList("draw-text-shadow.body")
