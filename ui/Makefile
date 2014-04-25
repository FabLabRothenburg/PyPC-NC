PYFILES := MainWindow.py

all: $(PYFILES)

clean:
	rm -f $(PYFILES)

%.py: %.ui
	pyside-uic -o $@ $<
