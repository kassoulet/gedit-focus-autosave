install::
	@mkdir -p ~/.local/share/gedit/plugins/gedit-focus-autosave
	@cp gedit-focus-autosave/* ~/.local/share/gedit/plugins/gedit-focus-autosave/ -v
	@sudo mkdir -p /usr/share/glib-2.0/schemas
	@sudo cp gedit-focus-autosave/org.gnome.gedit.plugins.focus-autosave.gschema.xml /usr/share/glib-2.0/schemas/
	@sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

uninstall:
	@rm -rfv ~/.local/share/gedit/plugins/gedit-focus-autosave
	@sudo rm -fv /usr/share/glib-2.0/schemas/org.gnome.gedit.plugins.focus-autosave.gschema.xml
	@sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

.PHONY: install uninstall