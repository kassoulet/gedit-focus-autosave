install::
	@mkdir -p ~/.local/share/gedit/plugins/gedit-focus-autosave
	@cp gedit-focus-autosave/* ~/.local/share/gedit/plugins/gedit-focus-autosave/ -v

uninstall:
	@rm -rfv ~/.local/share/gedit/plugins/gedit-focus-autosave

.PHONY: install uninstall