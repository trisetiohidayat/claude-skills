---
name: marp-slides
description: |
  Buat, konversi, dan optimalkan presentasi slide dari Markdown menggunakan Marp CLI.
  WAJIB digunakan ketika:
  - User ingin membuat slide presentasi dari Markdown
  - User menyebutkan "Marp", "slide", "presentasi", "PPT", "PowerPoint" dari markdown
  - User ingin convert file .md ke HTML/PDF/PPTX slide
  - User ingin preview live slide saat mengedit Markdown
  - User ingin custom theme/tema untuk slide
  - User ingin menjalankan "marp" command
  - User menyebut "deck", "keynote-style", "reveal.js"
  - User ingin server mode untuk serve slide via HTTP
  - User ingin bulk convert multiple markdown files ke slide
  - User ingin tambahkan presenter notes ke slide

  SKILL INI UNTUK MARP CLI, BUKAN library Marp lain (marp-core, marp-vscode, dll).
---

# Marp CLI Presentation Skill

## Overview

Marp CLI mengkonversi Markdown ke HTML, PDF, PPTX, dan gambar slide presentasi profesional. Tool ini
memiliki ekosistem lengkap: watch mode, server mode, custom themes, dan configuration file.

## Prerequisite

Pastikan marp-cli sudah terinstall:

```bash
npm install -g @marp-team/marp-cli
# atau
brew install marp-cli
```

Verifikasi installation:

```bash
marp --version
```

---

## Konsep Dasar Marp Markdown

### Struktur Slide

Setiap slide dipisahkan oleh `---` (horizontal rule). Gunakan `<!-- footer: ... -->` untuk footer,
`<!-- page_number: true -->` untuk nomor halaman.

```markdown
---
theme: default
marp: true
---

# Slide 1: Judul Presentasi

Isi slide pertama di sini.

---

# Slide 2: Topik Baru

Isi slide kedua di sini.

<!-- presenter notes di sini, tidak muncul di slide -->
```

### Marp Directive (Frontmatter)

Frontmatter di bagian atas file Markdown:

```markdown
---
marp: true
title: Judul Presentasi
author: Nama Penulis
theme: default
paginate: true
backgroundColor: #f0f0f0
---

# Isi slide...
```

### Layout & Text Direction

```markdown
<!-- _class: lead -->
<!-- _backgroundColor: #1a1a2e -->
<!-- _color: #ffffff -->

# Centered Title (lead layout)

<!-- _class: full -->
<!-- _backgroundImage: url('https://example.com/bg.jpg') -->

# Full Background Image

<!-- _class: two-column -->
<!-- layout: two-col -->

# Kiri          | # Kanan
Konten kiri     | Konten kanan
```

### Built-in Layouts

| Layout      | Deskripsi                          |
|-------------|-------------------------------------|
| `lead`      | Teks centered, title besar          |
| `full`      | Isi penuh, background image         |
| `two-col`   | Dua kolom sama lebar               |
| `cover`     | Cover slide, biasanya untuk title  |

### Warna & Styling Inline

```markdown
<!-- _color: #ff6b6b -->
Teks merah

<!-- _backgroundColor: #0d1b2a -->
Slide dengan background gelap
```

### Header/Footer Global

```markdown
---
marp: true
footer: "Footer Presentasi"
paginate: true
---

<!-- Atau per-slide -->
<!-- footer: "" -->  <!-- kosong, tidak ada footer -->
```

---

## Konversi File

### A. Markdown → HTML

```bash
marp slides.md --html --output ./dist/
```

Output: `slides.html` (single-page HTML dengan semua slide)

### B. Markdown → PDF

Butuh Chrome/Chromium terinstall.

```bash
marp slides.md --pdf --output ./dist/
```

Opsional: Lewati Chrome UI dengan `--chamberlaIn` (screencast):

```bash
marp slides.md --pdf --pptx --chrome binary="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

### C. Markdown → PowerPoint (PPTX)

```bash
marp slides.md --pptx --output ./dist/
```

Editable PPTX (experimental):

```bash
marp slides.md --pptx --pptx-editable --output ./dist/
```

### D. Markdown → Images (PNG/JPEG per slide)

```bash
# Semua slide sebagai gambar
marp slides.md --images png --output ./dist/

# Hanya slide pertama (title slide)
marp slides.md --image png --output ./dist/

# Set resolusi
marp slides.md --images png --image-scale 2 --output ./dist/
```

---

## Live Preview (Watch Mode)

Watch mode sangat powerful — setiap save ke file Markdown, slide otomatis regenerate.

```bash
# Watch single file
marp slides.md --watch

# Watch + server (otomatis buka browser)
marp slides.md --watch --server

# Watch + pdf output (auto-generate PDF on save)
marp slides.md --watch --pdf --output ./dist/
```

Tekan `Ctrl+C` untuk stop watch mode.

---

## Server Mode

Serve slide via HTTP, support multiple files:

```bash
# Serve direktori presentasi
marp ./slides/ --server

# Port khusus
marp ./slides/ --server --port 8080

# Server + watch (rekonversi on-the-fly)
marp ./slides/ --server --watch

# Allow local file access (gambar, font lokal)
marp ./slides/ --server --allow-local-files
```

Akses: `http://localhost:8080/slides.md`

---

## Konfigurasi (marp.yaml)

Untuk project besar, buat `marp.yaml` di root project:

```yaml
# marp.yaml
marp: true
title: "Presentasi Judul"
author: "Nama Penulis"
theme: default
paginate: true
---
```

Dan jalankan tanpa argumen:

```bash
marp ./slides/        # process all .md in directory
marp .               # process using marp.yaml
```

### Konfigurasi Lengkap

```yaml
# marp.yaml
marp: true
title: "Laporan Q1 2025"
author: "Tim Engineering"
theme: ./themes/custom-theme.yml
paginate: true
size: 16:9           # atau 4:3
date: 2025-01-15

# Global options
allowLocalFiles: true
charset: utf-8

# Output
html: true
pdf: true
pptx: false
images:
  type: png
  scale: 2

# Server
server:
  port: 8080
  watch: true

# PDF specific
pdfNotes: true       # embed presenter notes
pdfOutlines: true    # add bookmarks
```

---

## Custom Themes

### Menggunakan Theme Bawaan

```yaml
# marp.yaml atau frontmatter
theme: default      # bawaan, clean & professional
theme: uncover       # dramatic, full-bleed images
theme: gaia          # modern, colorful
theme: none          # tanpa style bawaan
```

### Custom Theme (CSS-based)

Buat file tema di `./themes/my-theme.css`:

```css
/* themes/my-theme.css */
@import 'https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap';

section {
  font-family: 'Inter', sans-serif;
  background-color: #0f172a;
  color: #e2e8f0;
}

h1 {
  color: #38bdf8;
  border-bottom: 3px solid #38bdf8;
}

h2 {
  color: #fbbf24;
}

section.title {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

section.title h1 {
  color: #ffffff;
  font-size: 3em;
}

blockquote {
  border-left: 4px solid #38bdf8;
  background-color: rgba(56, 189, 248, 0.1);
  padding: 1em;
  font-style: italic;
}

code {
  background-color: rgba(255,255,255,0.1);
  padding: 0.1em 0.3em;
  border-radius: 4px;
}

pre {
  background-color: #1e293b;
  border: 1px solid #334155;
}

/* Watermark */
section::after {
  content: attr(data-marpit-pagination) / attr(data-marpit-pagination-total);
  position: absolute;
  bottom: 20px;
  right: 30px;
  font-size: 14px;
  color: #64748b;
}
```

Gunakan tema:

```yaml
# marp.yaml
theme: ./themes/my-theme.yml
```

### Custom Theme (YAML-based Color Scheme)

```yaml
# themes/brand-theme.yml
marp-theme:
  colors:
    primary: '#0066cc'
    secondary: '#6c757d'
    background: '#ffffff'
    text: '#212529'
  generic:
    '1': '#0066cc'
    '2': '#6c757d'
  h1:
    color: '#0066cc'
    border-bottom: true
  h2:
    color: '#0052a3'
```

---

## Presenter Notes

Tambahkan notes yang tidak muncul di slide tapi berguna untuk presenter:

```markdown
---

# Slide with Notes

Konten visible di slide.

<!--
Presenter notes di sini.
- Point 1
- Point 2
- Penjelasan tambahan
-->

---

<!-- More notes -->
# Another Slide

<!--
Notes akan muncul di:
- Marp preview
- PDF dengan --pdf-notes flag
- Speaker view (--server)
-->
```

Export notes:

```bash
# PDF dengan notes
marp slides.md --pdf --pdf-notes --output ./dist/

# Export notes only (HTML)
marp slides.md --notes --output ./dist/
```

Speaker view (di browser):

```bash
marp slides.md --server --allow-local-files
# Buka di browser, tekan 'S' untuk speaker view
```

---

## Bulk Conversion

### Semua MD di Directory

```bash
# Konversi semua .md di folder
marp ./slides/ --html --pdf --pptx --output ./dist/

# Dengan konfigurasi
marp ./slides/ -c ./marp.yaml --html --pdf --output ./dist/
```

### Include/Exclude Pattern

```bash
# Hanya file yang match pattern
marp "./**/*-final.md" --pdf --output ./dist/

# Exclude draft files
marp ./slides/ --html --pdf --exclude "**/draft*.md"
```

---

## Advanced Tricks

### Responsive Slide Preview

```bash
# Mobile-friendly preview
marp slides.md --server --allow-local-files --port 8080
```

### Auto-reload Browser (Live Reload)

Buka dua terminal:
1. `marp slides.md --watch --server --allow-local-files`
2. Edit `slides.md` di editor, browser auto-refresh

### Template HTML Kustom

```bash
marp slides.md --html --html-template ./templates/slides.html --output ./dist/
```

### Multiple Themes in One Deck

```markdown
---
theme: default
---

# Slide dengan Default Theme

---

<!-- _theme: ./themes/accent-theme.css -->
# Slide dengan Accent Theme Override
```

### Image Handling

```markdown
<!-- _backgroundImage: url('./assets/hero.jpg') -->
<!-- _class: full -->

# Full-Bleed Background

<!-- _backgroundImage: linear-gradient(45deg, #667eea 0%, #764ba2 100%) -->
```

### Global Theme Directory

```yaml
# ~/.marp/config.yaml (global config)
marp:
  theme: .
  globalThemeDir: /path/to/themes
```

---

## Workflow yang Direkomendasikan

### 1. New Presentation (Start Here)

```bash
# Buat struktur folder
mkdir -p presentation/{assets,themes}

# Buat marp.yaml
cat > presentation/marp.yaml << 'EOF'
marp: true
title: "Judul Presentasi"
author: "Nama"
paginate: true
size: 16:9
EOF

# Buat slide pertama
cat > presentation/slides.md << 'EOF'
---
marp: true
---

# Welcome

Ini slide pertama.

---

# Topik 1

Konten topik 1.

---

# Q&A

Terima kasih!
EOF

# Preview
cd presentation && marp slides.md --server --watch
```

### 2. Export Final (Production)

```bash
cd presentation

# HTML + PDF + PPTX
marp slides.md \
  --html \
  --pdf \
  --pptx \
  --pdf-outlines \
  --pdf-notes \
  --output ./dist/

# PNG images (title slide only)
marp slides.md --image png --image-scale 2 --output ./dist/
```

### 3. Batch dari Multiple Files

```bash
# Setiap .md jadi satu deck terpisah
for f in ./decks/*.md; do
  name=$(basename "$f" .md)
  marp "$f" --html --pdf --pptx --output "./dist/$name/"
done
```

---

## Troubleshooting

### "Chrome not found" / PDF tidak bisa di-generate

```bash
# Install Chrome
brew install --cask google-chrome

# Atau specify path
marp slides.md --pdf --chrome "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

### Theme tidak ditemukan

```bash
# Gunakan absolute path atau relative dari cwd
marp slides.md --theme ./themes/my-theme.yml
```

### Karakter non-ASCII bermasalah

```yaml
# Tambahkan di marp.yaml
charset: utf-8
```

### Local images tidak muncul

```bash
# Gunakan --allow-local-files
marp slides.md --html --allow-local-files
```

### Server port sudah dipakai

```bash
# Port berbeda
marp slides.md --server --port 9000
```

### marp command not found

```bash
npm install -g @marp-team/marp-cli
# atau
brew install marp-cli
# Verify
which marp && marp --version
```

---

## Command Reference Cheatsheet

| Command | Fungsi |
|---------|--------|
| `marp file.md` | Preview default (HTML di stdout) |
| `marp file.md --html` | Export HTML |
| `marp file.md --pdf` | Export PDF |
| `marp file.md --pptx` | Export PPTX |
| `marp file.md --images png` | Export semua slide sebagai PNG |
| `marp file.md --image png` | Export title slide saja |
| `marp file.md --watch` | Watch mode (auto-rebuild) |
| `marp file.md --server` | HTTP server mode |
| `marp file.md --pptx-editable` | Editable PPTX (experimental) |
| `marp file.md --pdf-notes` | Embed presenter notes di PDF |
| `marp file.md --pdf-outlines` | Add PDF bookmarks |
| `marp file.md --image-scale 2` | Resolusi gambar 2x |
| `marp file.md --allow-local-files` | Allow local asset access |
| `marp file.md --theme THEME` | Override theme |
| `marp file.md --notes` | Export presenter notes HTML |
| `marp dir/ -c config.yaml` | Bulk convert dengan konfigurasi |
| `marp --version` | Cek versi |
| `marp --help` | Help lengkap |

---

## Tips & Best Practices

1. **Selalu gunakan frontmatter** dengan `marp: true` dan `theme` agar consistent.
2. **Gunakan watch mode** saat membuat slide — feedback loop instan.
3. **Gunakan YAML config** untuk project besar, jangan rely pada CLI flags.
4. **Custom theme** lebih maintainable dibanding inline CSS per-slide.
5. **Presenter notes** adalah investment besar — tulis notes saat buat slide.
6. **Batch conversion** dengan loop script saat punya banyak decks.
7. **16:9 vs 4:3** — default sekarang 16:9, set explicit di frontmatter.
8. **Local images** — simpan di `./assets/` dan gunakan relative path.
9. **Export PPTX** untuk audiens non-technical yang butuh PowerPoint editable.
10. **PDF outlines** (`--pdf-outlines`) sangat berguna untuk deck panjang.

---

## Example Prompts

Prompt yang harus ditangani skill ini:

- "convert file.md ke PDF slide"
- "buatkan slide tentang Python dari file notes.md"
- "tambahkan presenter notes ke slide saya"
- "custom theme dengan warna brand perusahaan"
- "preview live slide saat edit markdown"
- "serve slides via server mode"
- "bulk convert semua md di folder decks/"
- "export sebagai PPTX editable"
- "marp-cli watch mode tidak jalan"
- "custom font untuk slide presentation"
