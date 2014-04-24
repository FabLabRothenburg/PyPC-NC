LRELEASE := lrelease-qt4

all:
	$(MAKE) -C ui/ $@
	$(LRELEASE) PyPC-NC.pro

clean:
	$(MAKE) -C ui/ $@
	rm -f i18n/*.qm
