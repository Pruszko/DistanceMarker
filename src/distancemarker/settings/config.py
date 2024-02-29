from distancemarker.settings import getDefaultConfigTokens, ConfigException
from distancemarker.settings.config_file import g_configFiles
from distancemarker.settings.config_param import g_configParams
from distancemarker.settings.migrations import performConfigMigrations
from distancemarker.utils import *

logger = logging.getLogger(__name__)


class Config(object):

    fileSemaphore = ObservingSemaphore()

    def __init__(self):
        self.__loadedSuccessfully = False

    @fileSemaphore.withIgnoringLock(returnForIgnored=None)
    def reloadSafely(self):
        try:
            self.__loadConfigFileToParams()
            self.__updateModSettingsApiIfPresent()
        except ConfigException as e:
            logger.warning("Failed to load (or create) config")
            displayDialog(e.message)
        except Exception:
            logger.error("Failed to load (or create) config due to unknown error.", exc_info=True)
            displayDialog("Failed to load (or create) config due to unknown error.\n"
                          "Contact mod developer for further support with provided logs.")

    def persistParamsSafely(self):
        try:
            rawSerializedSettings = {
                tokenName: param.jsonValue for tokenName, param in g_configParams.items()
            }

            self.updateConfigSafely(rawSerializedSettings)
            self.__updateModSettingsApiIfPresent()
        except Exception:
            logger.error("Failed to save updated marker position offset.", exc_info=True)

    @fileSemaphore.withIgnoringLock(returnForIgnored=None)
    def updateConfigSafely(self, rawSerializedSettings):
        # if something is wrong with config file JSON syntax when the game
        # is just booting up, then ModsSettingsAPI will have default values for our params
        # what results in callback on settings save with default config values
        # what effectively would override user config with almost-default settings
        #
        # by this, we will allow overriding user config only, if it was lately successfully read
        # so when user typo actually occur, neither his config nor his changes will reset
        # and display warning dialog window informing that he messed up something
        #
        # I think (or rather I hope) this is more important
        # than autocorrecting invalid changes (which in result auto-rollbacks user changes)
        #
        # this only applies to invalid config JSON syntax (or file-access errors), not values alone
        # because values will still be autocorrected (but only invalid ones)
        if not self.__loadedSuccessfully:
            displayDialog("Configuration saving cancelled, because last performed manual config load failed.\n"
                          "Correct any typos in config file and restart game before trying to use GUI.")
            return

        try:
            # try to at least prepare config files with ignoring any exceptions
            #
            # we don't want exactly to load config file, because
            # it will be overridden anyway, but at least try to perform directories/migrations
            self.__prepareConfigFilesSafely()

            logger.info("Starting config saving ...")

            serializedSettings = getDefaultConfigTokens()
            serializedSettings.update(rawSerializedSettings)

            g_configFiles.config.writeConfigTokens(serializedSettings)

            logger.info("Finished config saving.")

            # reload config again to update our mod internal config state
            # with changes written to config file
            self.__loadConfigFileToParams()
        except ConfigException as e:
            logger.error("Failed to save config file")
            displayDialog(e.message)
        except Exception:
            logger.error("Failed to save config file due to unknown reason.", exc_info=True)
            displayDialog("Failed to save config file due to unknown reason.\n"
                          "Contact mod developer for further support with provided logs.")

    def __loadConfigFileToParams(self):
        logger.info("Starting config loading ...")
        self.__loadedSuccessfully = False

        self.__prepareConfigFiles()

        configDict = g_configFiles.config.loadConfigDict()

        for tokenName, param in g_configParams.items():
            value = param.readValueFromConfigDict(configDict)
            value = value if value is not None else param.defaultValue

            param.jsonValue = value

        self.__loadedSuccessfully = True
        logger.info("Finished config loading.")

    def __prepareConfigFilesSafely(self):
        try:
            self.__prepareConfigFiles()
        except ConfigException:
            logger.error("Failed to prepare config files, but continue anyway.")
        except Exception:
            logger.error("Failed to prepare config files, but continue anyway.", exc_info=True)

    def __prepareConfigFiles(self):
        performConfigMigrations()
        g_configFiles.createMissingConfigFiles()

    @staticmethod
    def __updateModSettingsApiIfPresent():
        from distancemarker import g_distanceMarkerMod
        if g_distanceMarkerMod.isModsSettingsApiPresent:
            from distancemarker.support.mods_settings_api_support import onConfigFileReload
            from distancemarker.support.mods_settings_api_support import settingsChangedSemaphore

            with settingsChangedSemaphore:
                onConfigFileReload()


g_config = Config()
