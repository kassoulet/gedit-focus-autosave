
install::
	@mkdir -p ~/.local/share/gedit/plugins
	@cp focus_autosave{.py,_config.glade} focus-autosave.plugin ~/.local/share/gedit/plugins -v

uninstall:
	@rm -fv  ~/.local/share/gedit/plugins/focus{-,_}autosave{_config,}.{plugin,py,glade}