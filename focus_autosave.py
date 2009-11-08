#!/usr/bin/python 
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>


import gedit

class AutosaveWindow:
    def __init__(self, plugin, window):
        self.window = window
        self.plugin = plugin

        self.window.connect("focus-out-event", self.on_focus_out_event)

    def deactivate(self):
        self.window = None
        self.plugin = None

    def update_ui(self):
        # Called whenever the window has been updated (active tab
        # changed, etc.) 
        pass

    def on_focus_out_event(self, widget, focus):
        gedit.commands.save_all_documents(self.window)


class AutosavePlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self.instances = {}

    def activate(self, window):
        self.instances[window] = AutosaveWindow(self, window)

    def deactivate(self, window):
        self.instances[window].deactivate()
        del self.instances[window]

    def update_ui(self, window):
        self.instances[window].update_ui()

