#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

from gi.repository import GObject, Gtk, Gdk, Gedit

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
            if doc.is_untouched():
                continue
            if doc.get_location() is None:
                continue
            doc.save(0)


class FocusAutoSavePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FocusAutoSavePlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.instances = {}

    def do_activate(self):
        self.instances[self.window] = AutosaveWindow(self, self.window)

    def do_deactivate(self):
        self.instances[self.window].deactivate()
        del self.instances[self.window]

    def do_update_state(self):
        self.instances[self.window].update_ui()


