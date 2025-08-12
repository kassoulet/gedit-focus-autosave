#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Save document when losing focus.
# Gautier Portet <kassoulet gmail.com>

import datetime
import gi

from gi.repository import GObject, Gedit, Gio, Gdk, Gtk

from pathlib import Path

gi.require_version("Gtk", "3.0")

# region ############### CONSTANTs #################################
DEFAULT_TEMP_PATH = Path("~/.gedit_unsaved").expanduser()
SETTINGS = Gio.Settings.new("org.gnome.gedit.plugins.focus-autosave")
SOURCE_DIR = Path(__file__).parent.resolve()
# endregion ############### CONSTANTs ###############################


class FocusAutoSavePlugin(
    GObject.Object,
    Gedit.WindowActivatable,
):
    __gtype_name__ = "FocusAutoSavePlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.other_action = False

    def do_activate(self):
        self.actions, self.ids = [], []
        for action in (
            "save",
            "save-as",
            "save-all",
            "close",
            "close-all",
            "open",
            "quickopen",
            "config-spell",
            "check-spell",
            "inline-spell-checker",
            "print",
            "docinfo",
            "replace",
            "quran",
        ):
            if action in self.window.list_actions():
                self.actions.append(self.window.lookup_action(action))
                self.ids.append(self.actions[-1].connect("activate", self.on_action))
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)
        self.other_action_signal = self.window.connect(
            "key-press-event", self.on_key_press
        )

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        self.window.disconnect(self.other_action_signal)
        del self.signal, self.other_action_signal
        for action, id_ in zip(self.actions, self.ids):
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
        now = datetime.datetime.now()
        temp_path = SETTINGS.get_string("temp-path")
        for n, doc in enumerate(self.window.get_unsaved_documents()):
            if doc.is_untouched():
                # nothing to do
                continue
            if doc.get_file().is_readonly():
                # skip read-only files
                continue

            if doc.get_file().get_location() is None and (temp_path) is not None:
                # provide a default filename
                filename = str(
                    Path(temp_path).expanduser()
                    / now.strftime(f"%Y%m%d-%H%M%S-{n+1}.txt")
                )
                doc.get_file().set_location(Gio.file_parse_name(filename))

            if doc.get_file().get_location():
                # save the document
                Path(temp_path).expanduser().mkdir(parents=True, exist_ok=True)
                assert (
                    Path(temp_path).expanduser().is_dir()
                ), f"{temp_path} is not a directory"
                Gedit.commands_save_document(self.window, doc)

    def do_create_configure_widget(self):
        # Just return your box, PeasGtk will automatically pack it into a box and show it.
        builder = Gtk.Builder()
        builder.add_from_file(str(SOURCE_DIR / "focus_autosave_config.glade"))
        builder.connect_signals(Handler(self))

        window = builder.get_object("window")
        self.untitled_savecheck = builder.get_object("untitled_savecheck")
        self.folder = builder.get_object("folder")

        if (temp_path := SETTINGS.get_string("temp-path")) is None or temp_path == "":
            self.folder.unselect_all()
            self.untitled_savecheck.set_active(False)
            self.folder.set_sensitive(False)
        else:
            self.untitled_savecheck.set_active(True)
            self.folder.set_sensitive(True)
            self.folder.set_current_folder(temp_path)

        # region Signals' binding to the handlers ##############################
        window.connect("destroy", Handler(self).on_window_destroy)
        self.untitled_savecheck.connect(
            "toggled", Handler(self).on_untitled_savecheck_toggled
        )
        self.folder.connect("selection_changed", Handler(self).on_selection_changed)
        # endregion  ###########################################################

        return window


class Handler:
    def __init__(self, main_window):
        self.main_window = main_window

    def on_window_destroy(self, *args):
        if (
            self.main_window.untitled_savecheck.get_active()
            and (folder := self.main_window.folder.get_filename()) is not None
        ):
            SETTINGS.set_string("temp-path", folder)
        else:
            SETTINGS.set_string("temp-path", "")

    def on_selection_changed(self, file_chooser):
        folder = file_chooser.get_filename()
        if folder and self.main_window.untitled_savecheck.get_active():
            SETTINGS.set_string("temp-path", str(Path(folder)))
        else:
            SETTINGS.set_string("temp-path", "")

    def on_untitled_savecheck_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.main_window.folder.set_sensitive(True)
            if (temp_path := SETTINGS.get_string("temp-path")) is None:
                SETTINGS.set_string("temp-path", str(DEFAULT_TEMP_PATH))
                self.main_window.folder.set_current_folder(str(DEFAULT_TEMP_PATH))
        else:
            self.main_window.folder.unselect_all()
            self.main_window.folder.set_sensitive(False)
            SETTINGS.set_string("temp-path", "")
