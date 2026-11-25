#!/bin/bash
set -e
echo "Cutefish Books kuruluyor..."
sudo apt update && sudo apt install -y python3-pyqt5 python3-fitz python3-docx python3-odf python3-reportlab djvulibre-bin
APP_DIR="$HOME/.local/share/cutefish-books"
mkdir -p "$APP_DIR" "$HOME/.local/share/applications"
cp app.py worker.py icon.svg "$APP_DIR/"
sed -i "s|~/CutefishBooks|$APP_DIR|g" "$APP_DIR/app.py"
cat << DESKTOP > "$HOME/.local/share/applications/cutefish-books.desktop"
[Desktop Entry]
Name=Cutefish Books
Comment=Modern macOS Apple Books style E-Book and Document Reader
Exec=python3 $APP_DIR/app.py
Icon=$APP_DIR/icon.svg
Terminal=false
Type=Application
Categories=Office;Viewer;
DESKTOP
echo "Kurulum tamamlandi! Cutefish Launcher uzerinden acabilirsiniz."
