#!/bin/bash
set -e
set -x

export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &
XVFB_PID=$!
sleep 1

# Function to retry commands
retry() {
    local retries=$1
    local command=$2
    local delay=$3
    for i in $(seq 1 $retries); do
        if $command; then
            return 0
        fi
        sleep $delay
    done
    echo "Command failed after $retries retries: $command"
    return 1
}

# Create a test file
echo "initial" > test.txt

# Enable the plugin
gsettings set org.gnome.gedit.plugins active-plugins "['focus_autosave']"
if ! gsettings get org.gnome.gedit.plugins active-plugins | grep -q 'focus_autosave'; then
    echo "Failed to enable plugin"
    exit 1
fi

# Check default temp path
if ! gsettings get org.gnome.gedit.plugins.focus-autosave temp-path | grep -q "$HOME/.gedit_unsaved"; then
    echo "Incorrect default temp path"
    exit 1
fi

if [ -e "$HOME/.gedit_unsaved" ]; then
    echo "$HOME/.gedit_unsaved must not exist"
    exit 1
fi

test_autosave() {
    local filename=$1
    local file_pattern=$2
    local gedit_pid

    # Run gedit and redirect logs
    G_MESSAGES_DEBUG=all gedit "$filename" &
    gedit_pid=$!

    # Wait for gedit window to appear
    if ! retry 10 "xdotool search --onlyvisible --name 'gedit' | grep ." 1; then
        echo "Gedit window not found"
        kill $gedit_pid
        exit 1
    fi

    # Type new text without manual save
    xdotool type "autosave check - "

    # Simulate focus change
    WID=$(xdotool search --onlyvisible --name "gedit" | head -1)
    xdotool windowunmap "$WID" # Hide window (simulate losing focus)

    # Wait for the autosaved file to appear
    local found_file
    if ! retry 10 "found_file=$(eval echo $file_pattern) && [ -f \"\$found_file\" ]" 1; then
        echo "Error: No file found matching pattern '$file_pattern'"
        kill $gedit_pid
        exit 1
    fi
    
    # Verify autosave worked
    if ! grep -q "autosave check" "$found_file"; then
        echo "Autosave verification failed"
        cat "$found_file"
        kill $gedit_pid
        exit 1
    fi

    # Clean up
    kill $gedit_pid
    wait $gedit_pid || true
    rm -f "$found_file"

    echo "✅ Test passed: $filename"
}

# Test with empty session
test_autosave "" "$HOME/.gedit_unsaved/*.txt"
test_autosave "" "$HOME/.gedit_unsaved/*.txt"

# Test with opened file
test_autosave "test.txt" "test.txt"

# Cleanup Xvfb
kill $XVFB_PID

echo "✅ All tests passed."
