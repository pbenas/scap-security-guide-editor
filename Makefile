NAME = ssge
DESTDIR = 
INSTALL_PATH = /usr/share

build: 
	echo "Nothing to do here. Maybe you want to try make install or make uninstall."

install:
	mkdir -p $(DESTDIR)$(INSTALL_PATH)
	cp -r $(NAME) $(DESTDIR)$(INSTALL_PATH)
	mkdir -p $(DESTDIR)/usr/bin
	ln -s $(INSTALL_PATH)/$(NAME)/$(NAME).py $(DESTDIR)/usr/bin/$(NAME)

uninstall: 
	rm -rf $(DESTDIR)$(INSTALL_PATH)/$(NAME)
	rm -f $(DESTDIR)/usr/bin/$(NAME)

clean: uninstall

