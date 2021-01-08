help:
	$(error "Usage: make [start\|stop\|install\|uninstall]")

reinstall: uninstall install

install:
	sudo cp rotel-server.service /lib/systemd/system
	sudo chown root:root /lib/systemd/system/rotel-server.service
	sudo systemctl enable rotel-server.service
##
	sudo cp rotel-worker.service /lib/systemd/system
	sudo chown root:root /lib/systemd/system/rotel-worker.service
	sudo systemctl enable rotel-worker.service

uninstall: stop
	sudo systemctl disable rotel-server.service
	sudo rm /lib/systemd/system/rotel-server.service
##
	sudo systemctl disable rotel-worker.service
	sudo rm /lib/systemd/system/rotel-worker.service

start:
	sudo systemctl start rotel-worker.service
	sudo systemctl start rotel-server.service

stop:
	sudo systemctl stop rotel-server.service
	sudo systemctl stop rotel-worker.service

