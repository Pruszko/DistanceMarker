from distancemarker.settings.config_param import g_configParams


def serializeConfigParams():
    return {
        "decimal-precision": g_configParams.decimalPrecision(),
        "text-size": g_configParams.textSize(),
        "text-color": _serializeColorTuple(g_configParams.textColor()),
        "text-alpha": g_configParams.textAlpha(),
        "draw-text-outline": g_configParams.drawTextOutline(),
        "draw-text-shadow": g_configParams.drawTextShadow(),
        "draw-distance-unit": g_configParams.drawDistanceUnit()
    }


def _serializeColorTuple(colorTuple):
    red, green, blue = colorTuple

    color = 0
    color |= red << 16
    color |= green << 8
    color |= blue

    return color
