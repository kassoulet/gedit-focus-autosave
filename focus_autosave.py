#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>


import gedit
import tempfile

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
        for doc in self.window.get_unsaved_documents():
            uri = doc.get_uri()
            print uri
            if uri is None:
                temp_fd, temp_path = tempfile.mkstemp(".txt","gedit-unsaved-")
                print 'temp:', temp_path
                doc.save_as("file://" + temp_path, doc.get_encoding(),0)
            doc.save(0)


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

