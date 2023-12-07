#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

from gi.repository import GObject, Gedit, Gio
import datetime
import os

# You can change here the default folder for unsaved files.
dirname = os.path.expanduser("~/.gedit_unsaved/")


def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
            os.makedirs(dir)


class FocusAutoSavePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FocusAutoSavePlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def on_focus_out_event(self, widget, focus):
        for n, doc in enumerate(self.window.get_unsaved_documents()):
            if doc.is_untouched():
                # nothing to do
                continue
            if doc.get_file().is_readonly():
                # skip read-only files
                continue
            if doc.get_file().get_location() is None:
                # provide a default filename
                now = datetime.datetime.now()
                assure_path_exists(dirname)
                filename = now.strftime(dirname + "%Y%m%d-%H%M%S-%%d.txt") % (n + 1)
                doc.get_file().set_location(Gio.file_parse_name(filename))
            # save the document
            Gedit.commands_save_document(self.window, doc)

    def do_activate(self):
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        del self.signal



