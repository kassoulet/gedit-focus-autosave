#!/bin/bash
set -e
set -x

TS=$(date +"%Y-%m-%d_%H-%M-%S")
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
sleep 1

# Create output directory (bind-mounted to host)
mkdir -p /output

# Create a test file
echo "initial" > test.txt

# Enable the plugin
gsettings set org.gnome.gedit.plugins active-plugins "['focus_autosave']"
gsettings get org.gnome.gedit.plugins active-plugins
gsettings get org.gnome.gedit.plugins active-plugins | grep 'focus_autosave'

gsettings get org.gnome.gedit.plugins.focus-autosave temp-path
gsettings get org.gnome.gedit.plugins.focus-autosave temp-path | grep "~/.gedit_unsaved"

if [ -f "~/.gedit_unsaved" ]; then echo "~/.gedit_unsaved must not exist"; exit 1; fi

test() {
    filename=$1 # Input filename
    file_pattern=$2 # Output file pattern

    # Run gedit and redirect logs
    G_MESSAGES_DEBUG=all gedit $filename 2>&1 | tee /output/gedit_${TS}.log &

    sleep 3  # Give it time to start

    # Type new text without manual save
    xdotool type "autosave check - "

    # Capture screenshot
    import -window root "/output/screenshot_${TS}_edited.png" || true

    # Simulate focus change
    WID=$(xdotool search --onlyvisible --name "gedit" | head -1)
    xdotool windowunmap $WID   # Hide window (simulate losing focus)

    sleep 2
    
    # Expand the pattern to find the file
    # We use eval to expand the tilde and wildcard
    files=( $(eval ls -1 "$file_pattern") )
    found_file="${files[0]}"

    if [ -z "$found_file" ]; then
        echo "Error: No file found matching pattern '$file_pattern'"
        exit 1
    fi

    echo $PWD
    echo ~
    echo "========"
    ls -l "$found_file" || true
    cat "$found_file" || true
    echo "========"
 
    # Verify autosave worked
    grep "autosave check" "$found_file"

    echo "✅ Test passed."
}

# Test with empty session
test "" '~/.gedit_unsaved/*.txt'
rm -f "~/.gedit_unsaved/*.txt"

test "" '~/.gedit_unsaved/*.txt'

rm -rf "~/.gedit_unsaved/"

# Test with opened file
test "test.txt" "test.txt"

echo "✅ All tests passed."
