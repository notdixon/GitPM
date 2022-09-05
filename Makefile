install:
	mkdir -pv /usr/share/gitpm
	touch /usr/share/gitpm/installed
	cp src/gitpm.1 /usr/local/share/man/man1/gitpm.1
	cp src/gitpm.conf /etc/gitpm.conf
	cp src/gitpm.py /usr/local/bin/gitpm
	chmod +x /usr/local/bin/gitpm

uninstall:
	rm -rfv /usr/share/gitpm
	rm -f /usr/local/share/man/man1/gitpm.1
	rm -f /etc/gitpm.conf
	rm -f /usr/local/bin/gitpm
