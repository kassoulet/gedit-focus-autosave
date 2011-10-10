#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

from gi.repository import GObject, Gtk, Gdk, Gedit, Gio
import datetime


class FocusAutoSavePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FocusAutoSavePlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def on_focus_out_event(self, widget, focus):

        for doc in self.window.get_unsaved_documents():
            if doc.is_untouched():
                # nothing to do
                continue
            if doc.is_untitled():
                # provide a default filename
                now = datetime.datetime.now();
                filename = now.strftime("/tmp/gedit.unsaved.%Y%m%d-%H%M%S.txt");
                doc.set_location(Gio.file_parse_name(filename))
            # save the document
            Gedit.commands_save_document(self.window, doc)

    def do_activate(self):
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        del self.signal



