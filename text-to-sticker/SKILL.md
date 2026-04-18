---
name: text-to-sticker
description: >
  Buat stiker WhatsApp dari teks. Trigger ketika user minta bikin stiker, pesan stiker,
  text to sticker, buat teks jadi stiker, atau inginkan gambar .webp dengan teks di dalamnya.
  Tidak untuk kebutuhan lain.
version: 1.0.0
---

# Text to WhatsApp Sticker

## Apa yang Dilakukan

Skill ini menerima teks input dan menghasilkan file gambar `.webp` (format stiker WhatsApp).

## Langkah Kerja

### 1. Kumpulkan Info dari User

Tanya parameter berikut (bisa sekaligus, bisa bertahap):

| Parameter | Default | Keterangan |
|-----------|---------|------------|
| `teks` | **wajib** | Teks yang mau dibuat jadi stiker |
| `warna_latbel` | `#FFFFFF` (putih) | Warna background, pakai hex atau nama CSS |
| `warna_teks` | `#000000` (hitam) | Warna teks, pakai hex atau nama CSS |
| `ukuran_font` | `60` | Ukuran font dalam piksel |
| `lokasi_simpan` | `./stiker.webp` | Path tempat menyimpan file .webp |

Jika user tidak specify warna, pakai default. Jika tidak specify lokasi, simpan di direktori kerja.

### 2. Jalankan Script

Panggil script `scripts/make_sticker.py` dengan parameter yang sudah dikumpulkan:

```bash
python3 <skill-path>/scripts/make_sticker.py \
  --text "Teks stiker di sini" \
  --bg-color "#FF6B6B" \
  --text-color "#FFFFFF" \
  --font-size 60 \
  --output "./stiker.webp"
```

**Pastikan semua argumen ada**: `--text` WAJIB, sisanya optional.

### 3. Laporkan Hasil ke User

Setelah script jalan:
- Beritahu user di mana file `.webp` tersimpan
- Tanyakan apakah mau ada perubahan (warna, font, teks lain)
- Beri tahu user cara pakai: langsung kirim ke WhatsApp

## Catatan Penting

- Teks yang sangat panjang akan di-wrap (dipotong baris) secara otomatis
- Emoji dalam teks akan berusaha dirender, tapi hasil bisa vary — **Jangan promise 100% emoji support**; jika emoji gagal dirender, tetap hasilkan stiker tanpa emoji dan bilang ke user
- Ukuran kanvas default: **512x512 px** — cocok untuk stiker WhatsApp
- Background selalu pakai **rounded corners** (lingkaran di tiap sudut) supaya mirip stiker
- Format output SELALU `.webp` — tidak bisa别的格式
