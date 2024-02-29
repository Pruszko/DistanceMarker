CONFIG_TEMPLATE = """{
    // To generate default config, delete config file and launch a game again

    // Global features toggle
    // Valid values: true/false (default: true)
    //
    // When set to false, it globally disables all features of this mod
    // however it does not remove mod presence itself. 
    "enabled": %(enabled)s,

    // Valid values: ["always", "on-alt-pressed"]
    // Default value: "on-alt-pressed"
    //
    // Configures when marker should be displayed:
    // - "always"         - displays marker always,
    // - "on-alt-pressed" - when ALT key is being pressed.
    "display-mode": %(display-mode)s,

    // Valid values: ["ally-and-enemy", "only-enemy"]
    // Default value: "ally-and-enemy"
    //
    // Configures when marker should be displayed:
    // - "ally-and-enemy" - for all tanks,
    // - "only-enemy"     - only for enemies.
    "marker-target": %(marker-target)s,

    // Valid values: ["tank-marker", "tank-center", "tank-bottom"]
    // Default value: "tank-marker"
    //
    // Position at which markers are initially displayed with zero offsets:
    // - "tank-marker" - at standard tank marker position,
    // - "tank-center" - at tank center position,
    // - "tank-bottom" - at tank bottom position.
    "anchor-position": %(anchor-position)s,

    // Valid values: true/false (default: false)
    //
    // When set to true, marker position can no longer be edited during battle.
    // Useful if you want to prevent accidental change.
    "lock-position-offsets": %(lock-position-offsets)s,

    // Valid values: integer between -150 and 150 (default 24)
    //
    // Controls horizontal marker offset relative to anchor position, in pixels.
    // Positive values moves marker to right side, negative values - to left side.
    //
    // Hint: Offsets can be visually edited during battle by dragging markers
    // with mouse while CTRL key is being held.
    // Offsets will be saved in configuration on battle finish or manual exit.
    "anchor-horizontal-offset": %(anchor-horizontal-offset)s,

    // Valid values: integer between -150 and 150 (default 16)
    // 
    // Controls vertical marker offset relative to anchor position, in pixels.
    // Positive values moves marker upwards, negative values - downwards.
    //
    // Hint: Offsets can be visually edited during battle by dragging markers
    // with mouse while CTRL key is being held.
    // Offsets will be saved in configuration on battle finish or manual exit.
    "anchor-vertical-offset": %(anchor-vertical-offset)s,

    // Valid values: integer between 0 and 2 (for default behavior: 0)
    //
    // Decimal precision of displayed distance
    "decimal-precision": %(decimal-precision)s,

    // Valid values: integer between 6 and 24 (for default behavior: 11)
    //
    // Size of text displayed in marker.
    "text-size": %(text-size)s,

    // Valid value: 3-element array of numbers between 0 and 255
    // Default value: [255, 255, 255] (this is white color)
    //
    // Colors text displayed in marker using red, green and blue components.
    // You can use color picker from internet to visually choose desired color.
    "text-color": %(text-color)s,

    // Valid values: number between 0.0 and 1.0 (default 1.0)
    //
    // Controls transparency of text in markers:
    // - value 1.0 means full visibility,
    // - value 0.0 means zero visibility.
    "text-alpha": %(text-alpha)s,

    // Valid values: true/false (default: true)
    //
    // When set to true, text is additionally displayed with smooth gradient shadow.
    // Useful when text blends with background.
    "draw-text-shadow": %(draw-text-shadow)s,

    // DO NOT touch "__version__" field
    // It is used by me to seamlessly update config file :)
    "__version__": 1
}"""
