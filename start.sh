#!/bin/bash
# Time-stamp: <2021-02-23 20:38:13>

#
# Colors for Apple Terminal
#
function list_colors {
    cat ./resources/colors.csv
}

function grep_apple_color {
    grep "$*" ./resources/colors.csv
}

function get_apple_color {
    egrep "(^|,)$*(,|\t)" ./resources/colors.csv | cut -f 6
}

function set_foreground_color {
    color=$(get_apple_color $*)
    if [ "$color" != "" ] ; then
        osascript -e "tell application \"Terminal\" to set normal text color of window 1 to ${color}"
        echo "Normal test color set to: $*: $color"
    fi
}

function set_background_color {
    color=$(get_apple_color $*)
    if [ "$color" != "" ] ; then
        osascript -e "tell application \"Terminal\" to set background color of window 1 to ${color}"
        echo "Background color set to: $*: $color"
    fi
}

function set_theme {
    set_foreground_color $1
    set_background_color $2
}

function set_font {
    osascript -e "tell application \"Terminal\" to set the font name of window 1 to \"$1\""
    osascript -e "tell application \"Terminal\" to set the font size of window 1 to $2"
}


set_foreground_color Yellow
echo Running...
set_foreground_color Red
python3 simulation_test.py
set_foreground_color Black
