PYFILES := MainWindow.py GraphicsView.py

all: $(PYFILES)

clean:
	rm -f $(PYFILES)

%.py: %.ui
	pyside-uic -o $@ $<
