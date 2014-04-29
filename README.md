PyPC-NC
=======

by Stefan Siegl

PyPC-NC is a GUI application to controll a CNC mill that has a CNCCON axis
controller by "Burkhard Lewetz - Ingenieurbüro für technische Software-Entwicklung";
hence it is kind of an alternative to his WinPC-NC software for Windows PCs.

Features
----------

 * Python/PySide based GUI application, hence plattform independent
 * displays certain machine status information
 * automatic reference movement + manual movements
 * storing workpiece location (and moving back to its' origin)
 * G-Code import & interpreter
 * CNCCON mock implementation

G-Code interpreter limitations
--------------------------------

The G-Code interpreter is far from being fully-fledged (and error-free).  But
still it supports most of the code popular plugins and free CAM software exports.

Especially the interpreter (currently) lacks support for

 * plane switching (currently solely XY plane is supported)
 * helical arcs (G2 and G3 code with Z axis word)
 * B-splines and nurbs
 * absolute arc distance mode
 * boring canned cycles (G84 to G89)
 * dwells and dwell-requiring canned cycles (G82, G86 et al)
 * tool length & radius compensation
 * path blending
 * coordinate system selection


Gimmicks
----------

 * mockserial, binds the mock implementation to a PTY which can be provided to
   WinPC-NC via Wine (thus allowing mock sessions with WinPC-NC)


Bug in pyside-uic 
-------------------

There is a bug in pyside-uic, caused by use of QButtonGroup and yields
"an unexpected error occured" message during `make`.
See https://bugreports.qt-project.org/browse/PYSIDE-126 for details.

`sudo vim /usr/share/pyshared/pysideuic/uiparser.py +212` and replace
`bg_name = bg_i18n.string` by `bg_name = bg_i18n`.
