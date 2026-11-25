# Cutefish Books

Modern macOS Apple Books style universal e-book and document reader built for **CutefishOS**.

## Features
- **Supported Formats:** PDF, EPUB, XPS, FB2, CBZ, DOCX, TXT, RTF, ODT, DJVU
- **Adaptive System Theme:** Automatically switches between Light and Dark mode following CutefishOS settings (`~/.config/cutefish/services.conf`)
- **Fast Pre-fetching Engine:** In-memory page rendering and background next-page pre-fetching for instant page turns
- **Reader Controls:** Zoom (`+`/`-`), keyboard navigation, Dark Mode page inversion, and automatic reading progress memory

## Installation

### Option 1: Install via `.deb` Package (Recommended)
1. Download `cutefish-books_1.0.0_all.deb` from the [Releases](https://github.com) page.
2. Install it with a single command:
```bash
sudo apt install ./cutefish-books_1.0.0_all.deb
```

### Option 2: Install from Source
```bash
git clone https://github.com
cd cutefish-books
bash install.sh
```
