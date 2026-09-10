#!/bin/bash

MAIN="/sys/class/backlight/gmux_backlight"
TB="/sys/class/backlight/appletb_backlight"

MAIN_SAVE="/run/proxmox-lid-main-brightness"
TB_SAVE="/run/proxmox-lid-touchbar-brightness"

if grep -q "closed" /proc/acpi/button/lid/*/state; then

    # Save current brightness, but don't overwrite saved value with 0
    if [ -r "$MAIN/brightness" ]; then
        CURRENT=$(cat "$MAIN/brightness")
        [ "$CURRENT" -gt 0 ] && echo "$CURRENT" > "$MAIN_SAVE"
        echo 0 > "$MAIN/brightness"
    fi

    if [ -r "$TB/brightness" ]; then
        CURRENT=$(cat "$TB/brightness")
        [ "$CURRENT" -gt 0 ] && echo "$CURRENT" > "$TB_SAVE"
        echo 0 > "$TB/brightness"
    fi

else

    # Restore previous values when lid opens
    if [ -f "$MAIN_SAVE" ]; then
        cat "$MAIN_SAVE" > "$MAIN/brightness"
    else
        echo 13325 > "$MAIN/brightness"
    fi

    if [ -f "$TB_SAVE" ]; then
        cat "$TB_SAVE" > "$TB/brightness"
    else
        echo 1 > "$TB/brightness"
    fi

fi

