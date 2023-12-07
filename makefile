
install::
	@mkdir -p ~/.local/share/gedit/plugins
	@cp focus-autosave.plugin focus_autosave.py ~/.local/share/gedit/plugins -v

uninstall:
	@rm -fv  ~/.local/share/gedit/plugins/focus{-,_}autosave.{plugin,py}
