import os
import logging

from distancemarker.settings import copy, deleteEmptyFolderSafely, toBool, ConfigException
from distancemarker.settings.config_file import g_configFiles

logger = logging.getLogger(__name__)


class ConfigVersion(object):

    V2_1_0 = 1
    V2_2_0 = 2

    CURRENT = V2_2_0


def performConfigMigrations():
    try:
        if not g_configFiles.config.exists():
            return

        configDict = g_configFiles.config.loadConfigDict()

        if isVersion(configDict, ConfigVersion.CURRENT):
            return

        v2_2_0_addTextOutlineAndDistanceUnitParameters(configDict)

        g_configFiles.config.writeConfigDict(configDict)
    except ConfigException:
        logger.error("Failed to perform config file migration.")
        raise
    except Exception:
        logger.error("Failed to perform config file migration.", exc_info=True)
        raise ConfigException("Failed to perform config file migration due to unknown error.\n"
                              "Contact mod developer for further support with provided logs.")


def v2_2_0_addTextOutlineAndDistanceUnitParameters(configDict):
    if not isVersion(configDict, ConfigVersion.V2_1_0):
        return

    logger.info("Migrating config file from version 2.1.x to 2.2.x ...")

    configDict["draw-text-outline"] = False
    configDict["draw-distance-unit"] = True
    progressVersion(configDict)

    logger.info("Migration finished.")


def progressVersion(configDict):
    if "__version__" not in configDict:
        configDict["__version__"] = ConfigVersion.V2_1_0
        return

    configDict["__version__"] = int(configDict["__version__"]) + 1


def isVersion(configDict, version):
    if "__version__" not in configDict:
        return ConfigVersion.V2_1_0 == version

    return int(configDict["__version__"]) == version
