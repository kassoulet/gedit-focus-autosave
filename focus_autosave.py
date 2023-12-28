#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

import datetime

from gi.repository import GObject, Gedit, Gio, Gdk
from pathlib import Path

# You can change here the default folder for unsaved files.
dirname = Path("~/.gedit_unsaved/").expanduser()


class FocusAutoSavePlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "FocusAutoSavePlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.other_action = False

    def do_activate(self):
        self.actions, self.ids = [], []
        for action in ("save", "save-as", "save-all", "close", "close-all", "open", "quickopen",
                       "config-spell", "check-spell", "inline-spell-checker", "print", "docinfo",
                       "replace", "quran"):
            if action in self.window.list_actions():
                self.actions.append(self.window.lookup_action(action))
                self.ids.append(self.actions[-1].connect("activate", self.on_action))
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)
        self.other_action_signal = self.window.connect("key-press-event", self.on_key_press)

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        self.window.disconnect(self.other_action_signal)
        del self.signal, self.other_action_signal
        for action,id_ in zip(self.actions, self.ids):
            action.disconnect(id_)
            del id_

    def on_action(self, *_):
        file = self.window.get_active_document().get_file()
        if file.get_location() is None:
            self.other_action = True

    def on_key_press(self, widget, event):
        if event.state == Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_q:
            self.other_action = True

    def on_focus_out_event(self, widget, focus):
        if self.other_action:
            # skip to user specified file name
            self.other_action = False
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




