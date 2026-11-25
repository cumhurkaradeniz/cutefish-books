#!/bin/bash
set -e
mkdir -p pkg/DEBIAN pkg/usr/share/cutefish-books pkg/usr/share/applications pkg/usr/bin
cp app.py worker.py icon.svg pkg/usr/share/cutefish-books/
cat << 'CTRL' > pkg/DEBIAN/control
Package: cutefish-books
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pyqt5, python3-fitz, python3-docx, python3-odf, python3-reportlab, djvulibre-bin
Maintainer: Cumhur Karadeniz <cumhurkaradeniz@github.com>
Description: Modern macOS Apple Books style E-Book and Document Reader for CutefishOS
CTRL
printf '#!/bin/bash\nexec python3 /usr/share/cutefish-books/app.py "$@"\n' > pkg/usr/bin/cutefish-books && chmod +x pkg/usr/bin/cutefish-books
cat << 'DSK' > pkg/usr/share/applications/cutefish-books.desktop
[Desktop Entry]
Name=Cutefish Books
Comment=Modern macOS Apple Books style E-Book and Document Reader
Exec=cutefish-books
Icon=/usr/share/cutefish-books/icon.svg
Terminal=false
Type=Application
Categories=Office;Viewer;
DSK
dpkg-deb --root-owner-group --build pkg cutefish-books_1.0.0_all.deb && rm -rf pkg
