#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

import datetime

from gi.repository import GObject, Gedit, Gio, Gdk
from pathlib import Path

def on_key_press(widget, event):
  global Ctrl_S
  if event.state == Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_s:
      Ctrl_S = True

# You can change here the default folder for unsaved files.
dirname = Path("~/.gedit_unsaved/").expanduser()

Ctrl_S = False

class FocusAutoSavePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FocusAutoSavePlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def on_focus_out_event(self, widget, focus):
        global Ctrl_S
        if Ctrl_S:
            # skip to user specified file name
            Ctrl_S = False
            return
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
                Path(dirname).mkdir(parents=True, exist_ok=True)
                filename = str(dirname/now.strftime(f"%Y%m%d-%H%M%S-{n+1}.txt"))
                doc.get_file().set_location(Gio.file_parse_name(filename))
            # save the document
            Gedit.commands_save_document(self.window, doc)

    def do_activate(self):
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)
        self.ctrl_s = self.window.connect("key-press-event", on_key_press)

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        self.window.disconnect(self.ctrl_s)
        del self.signal, self.ctrl_s



