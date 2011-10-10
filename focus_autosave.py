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
        #print '\n'.join(dir(doc))
        #self.tab.set_state(Gedit.TabState.SAVING)
        #self.window.do_saving()
        for doc in self.window.get_unsaved_documents():
            #print '\n'.join(dir(doc))
            if doc.is_untouched():
                continue
            if doc.is_untitled():
                continue
                now = datetime.datetime.now();
                filename = now.strftime("/tmp/gedit.unsaved.%Y%m%d-%H%M%S.txt");
                doc.set_location(Gio.file_parse_name(filename))
            tab = Gedit.Tab.get_from_document(doc)
            #doc.emit('save')
            tab.emit('save')
            #doc.save(0)
            #print '\n'.join(dir(Gedit.Tab))
            #autosave = tab.get_auto_save_enabled()
            #autosave_interval = tab.get_auto_save_interval()
            #tab.set_auto_save_enabled(True)
            #tab.set_auto_save_interval(0)
                        

    def reset_auto_save(self):
        pass
            
            
    def do_activate(self):
        self.signal = self.window.connect("focus-out-event", self.on_focus_out_event)

    def do_deactivate(self):
        self.window.disconnect(self.signal)
        del self.signal

    def do_update_state(self):
        pass


