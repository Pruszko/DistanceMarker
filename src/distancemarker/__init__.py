import logging


logger = logging.getLogger(__name__)


class DistanceMarkerMod(object):

    def __init__(self):
        pass

    # try-except with logged exception here is more than important, because
    # when mod is initialized and some incompatibility occurs, it may break this (or other) mods
    # mainly because:
    # - AttributeError is silently ignored by mod loading code
    #   what can lead to very weird "lack of errors" where game state is corrupted
    #   due to unexpected module loading errors
    # - other exceptions may basically break loading of other mods
    #
    # by this, at least we will see what is broken
    try:
        logger.info("Initializing DistanceMarker mod ...")

        # it is good to know from the logs which client may have compatibility problems
        # it's not obviously logged anywhere by any client, or I am just blind
        from distancemarker.utils import getClientType
        logger.info("Client type: %s", getClientType())

        # make sure to invoke all hooks
        import distancemarker.hooks

        logger.info("DistanceMarker mod initialized")
    except Exception:
        logger.error("Error occurred while initializing DistanceMarker mod", exc_info=True)

        from distancemarker.utils import displayDialog
        displayDialog("Error occurred while initializing DistanceMarker mod.\n"
                      "Contact mod developer with error logs for further support.")

    def fini(self):
        pass


g_distanceMarkerMod = DistanceMarkerMod()
