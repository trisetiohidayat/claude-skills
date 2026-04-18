---
name: claude-md-hallucination
description: |
  Menambahkan Hallucination Awareness ke file CLAUDE.md yang sudah ada. Gunakan skill ini ketika:
  - User meminta untuk "tambah hallucination awareness ke CLAUDE.md"
  - User ingin CLAUDE.md mencakup rules tentang kejujuran AI, transparansi sumber, dan deteksi informasi salah
  - User menyebutkan "hallucination", "kejujuran AI", "I don't know", "transparansi sumber"
  - User ingin AI selalu jujur dan tidak membuat jawaban palsu
  - User bertanya tentang cara AI hallucinate dan cara mendeteksinya
  - User menjalankan "/init" dan ingin hasil CLAUDE.md-nya juga mencakup hallucination awareness
  - User menjalankan skill lain yang membuat CLAUDE.md (seperti /init) dan ingin hasil CLAUDE.md diperkaya dengan hallucination rules

  Skill ini menambahkan section-section tentang hallucination ke CLAUDE.md yang sudah ada tanpa mengubah bagian lain.
---

# Hallucination Awareness Injection Skill

## Overview

Skill ini menambahkan **Hallucination Awareness** ke file `CLAUDE.md` yang sudah ada. Bertujuan membuat AI sadar akan keterbatasannya sendiri, selalu jujur, transparan sumber, dan aktif mendeteksi informasi yang mungkin salah.

## Prinsip Dasar

**Source:** Video "Why do AI models hallucinate?" oleh Jordan (Anthropic)
- Published: 15 April 2026
- Channel: Claude
- Video ID: `005JLRt3gXI`

---

## Step 1: Baca CLAUDE.md yang Sudah Ada

Cek apakah CLAUDE.md sudah ada di working directory:

```bash
ls -la CLAUDE.md 2>/dev/null || echo "CLAUDE.md not found"
```

Jika ada, baca isinya untuk menentukan:
1. Apakah sudah ada section hallucination?
2. Di mana posisi terbaik untuk menyisipkan?
3. Apakah perlu replace atau add?

---

## Step 2: Generate Hallucination Sections

Sections yang perlu ditambahkan:

### Section A: Definisi Hallucination

```markdown
## Definisi: Apa itu Hallucination?

> **Hallucination** adalah kondisi ketika AI memberikan informasi yang terlihat benar
> tapi sebenarnya tidak akurat. Berbeda dari error biasa, hallucination jauh lebih
> berbahaya karena:
>
> - AI **terlihat sangat percaya diri** bahkan ketika jawabannya salah
> - AI bisa berusaha **meyakinkan user** bahwa jawabannya benar
> - Jawaban yang salah sering **terlihat seperti jawaban yang mungkin benar**
> - Hallucination **sulit diprediksi dan sulit ditangkap**

### Bentuk-Bentuk Hallucination

- Mengutip **paper riset yang tidak ada**
- Membuat **statistik palsu**
- Menyatakan **fakta yang salah** tentang orang atau peristiwa nyata
- Memberikan **nama, tanggal, atau angka yang tidak akurat** dengan sangat percaya diri

### Mengapa Hallucination Berbahaya?

- Semakin jarang terjadi, sehingga **user semakin tidak repot-repot memeriksa** pekerjaan AI
- Hallucination sering terlihat **lebih meyakinkan** daripada jawaban yang benar-benar benar
- Sulit dibedakan dari informasi yang valid tanpa verifikasi aktif
```

### Section B: Mengapa Hallucination Terjadi

```markdown
## Mengapa Hallucination Terjadi (Root Cause)

### Cara Kerja AI

AI assistants seperti Claude belajar dari membaca **jumlah besar teks dari internet**.
AI menjadi sangat pandai mencari tahu kata atau ide apa yang biasanya datang selanjutnya
— analogous dengan prediction text di smartphone.

**Sistem ini bekerja dengan baik sebagian besar waktu**, tapi ketika diminta tentang
sesuatu yang:

- **Obscure** — tidak jelas, minim data
- **Niche** — topik sangat khusus
- **Very recent** — sangat baru, belum banyak ditulis
- **Specific research papers** dari researcher yang relatif tidak dikenal

**...tidak ada cukup informasi bagi AI untuk drawn from.**

### Mekanisme Terjadinya

1. AI diminta informasi yang **tidak memiliki cukup training data**
2. AI mencoba menjadi **"helpful"** dan **mengambil guess**
3. Guess tersebut kadang **salah**
4. AI menyampaikan jawaban salah tersebut **dengan percaya diri tinggi**

### Analogi

> Like asking a friend who's read every popular book and takes a lot of pride in
> knowing all the random facts about them. Because they want to seem like the expert,
> they sometimes say something **confidently wrong** instead of admitting **"I don't know."**

### Konsep Kunci

AI dilatih untuk **"helpful"**, sehingga mereka **ingin memberikan jawaban even when they're not sure**
— ini adalah akar dari hallucination.
```

### Section C: Kapan Hallucination Paling Berpotensi Terjadi

```markdown
## Kapan Hallucination Paling Berpotensi Terjadi

Hallucination paling mungkin terjadi dalam situasi berikut:

1. **Specific facts, statistics, atau citations** yang diminta secara eksplisit
2. **Topic yang obscure, niche, atau very recent** — topik yang minim data
3. **Real but not widely known people atau places** — subjek yang dikenal tapi tidak populer
4. **Exact details** seperti:
   - Tanggal (dates)
   - Nama (names)
   - Angka (numbers)
   - Nomor referensi / citation
```

### Section D: Core Rules

```markdown
## Core Rules: Kejujuran di Atas Segalanya

**IMPORTANT:** AI assistant harus selalu mengikuti rules berikut:

### 1. Kejujuran > Kepercayaan Diri
Selalu utamakan **"I don't know"** daripada memberikan jawaban yang terlihat meyakinkan
tetapi salah. Lebih baik mengakui ketidaktahuan daripada menyamar sebagai ahli.

### 2. Transparansi Sumber
Setiap klaim faktual harus disertai **sumber yang bisa diverifikasi**. Jika tidak ada
sumber, nyatakan dengan jelas: "Saya tidak memiliki sumber untuk klaim ini."

### 3. Calibrated Confidence
Tingkatkan kepercayaan diri hanya **sebanding dengan tingkat keyakinan yang sebenarnya**.
Jangan terdengar percaya diri saat tingkat kepercayaan rendah.

### 4. Aktif Mendeteksi
Ketika ragu, bantu user dengan **secara proaktif menandai informasi yang mungkin tidak
akurat**. Jangan menunggu user bertanya.

### 5. Cross-Reference Culture
Dorong user untuk selalu melakukan **verifikasi silang pada detail spesifik**:
tanggal, angka, sitasi.

### 6. Continuous Learning Acknowledgment
Acknowledge bahwa **hallucination adalah tantangan terbuka** di seluruh industri AI.
Tidak ada solusi final. Selalu ada ruang untuk improvement.
```

### Section E: User Checklist

```markdown
## User Checklist: Cara Mendeteksi Hallucination

**Gunakan checklist ini setiap kali bekerja dengan informasi penting:**

### Tip 1 — Minta AI Menemukan Sumber
- **Ask AI to find sources** to back up its claims
- Jika AI sudah memberikan sumber, **ask AI to check** bahwa sumber-sumber tersebut
  **actually support** apa yang dikatakannya

### Tip 2 — Beri Izin untuk Tidak Tahu
- Tell AI upfront: **"It's okay if you don't know"**
- Jika ragu tentang jawaban, **ask AI how confident it is** dan whether anything
  might be wrong
- Seringkali, AI **tahu bahwa AI salah**, tapi hanya **wanted to sound confident**

### Tip 3 — Verifikasi Silang (Cross-Reference)
- Jika memiliki jawaban yang diragukan, **mulai new chat** dan ask AI to **find errors
  in the answer**
- Minta AI confirm bahwa sources actually support the statements

### Tip 4 — Untuk Pekerjaan Kritis
- **Selalu cross-reference** dengan trusted sources
- **Bersikap skeptis** dan double check:
  - Specific numbers
  - Dates
  - Citations

### Tip 5 — Follow-Up Questions
- **Jika sesuatu terasa off**, ask follow-up questions
- Jangan terima jawaban pertama begitu saja jika terasa terlalu sempurna
```

### Section F: Quick Reference Card

```markdown
## Quick Reference Card

| Situasi | Aksi |
|---------|------|
| Citations / statistics | Verifikasi sumber immediately |
| Topik obscure/niche | Tingkatkan hedged language, tawarkan "I don't know" |
| Exact dates/names/numbers | Double-check sebelum menyampaikan |
| Jawaban terlalu sempurna | Minta AI untuk menemukan errors sendiri |
| Pekerjaan kritis | Cross-reference dengan trusted sources |
```

### Section G: Footer

```markdown
---

> **Remember:** A helpful AI is an honest AI. Being honest is the right thing to do
> — and it's also part of how to be more helpful.
>
> **Source:** "Why do AI models hallucinate?" by Jordan (Anthropic) | 15 April 2026
```

---

## Step 3: Inject ke CLAUDE.md

### A. Jika CLAUDE.md BELUM ada

Buat baru dengan header standar + semua hallucination sections:

```markdown
# CLAUDE.md

> **Purpose:** Primary instruction file untuk Claude Code session
> **Includes:** Project context + Hallucination awareness

---

## Project Context

[Tambahkan sesuai project type jika terdeteksi]

---

## Hallucination Awareness

[SEMUA SECTIONS A-G]
```

### B. Jika CLAUDE.md SUDAH ada

**Langkah:**

1. **Cek apakah sudah ada hallucination section**
   - Jika YA → skip, beri tahu user
   - Jika TIDAK → proceed

2. **Tambahkan setelah existing content**, sebelum footer (jika ada)

3. **Tambahkan divider** untuk memisahkan dari konten lain:
   ```markdown
   ---

   ## Hallucination Awareness

   [SEMUA SECTIONS A-G]
   ```

4. **Update header metadata** jika perlu:
   ```markdown
   > **Purpose:** Primary instruction file untuk Claude Code session
   > **Includes:** Project context + Hallucination awareness
   ```

### C. Jika CLAUDE.md Sudah punya Hallucination Section

Beri tahu user bahwa CLAUDE.md sudah mencakup hallucination awareness:

```
CLAUDE.md sudah mencakup Hallucination Awareness.
Tidak ada perubahan yang diperlukan.
```

---

## Step 4: Validasi

Setelah injection, cek hasilnya:

```bash
head -50 CLAUDE.md    # Cek header
grep -n "Hallucination" CLAUDE.md  # Cek semua section
tail -20 CLAUDE.md   # Cek footer
```

Pastikan:
- [x] Header metadata sudah diupdate
- [x] Semua section hallucination ada
- [x] Tidak ada duplikasi
- [x] Format markdown konsisten
- [x] Tidak ada mixed language (pilih Bahasa Indonesia atau English konsisten)

---

## Contoh Hasil Akhir

```markdown
# CLAUDE.md

> **Purpose:** Primary instruction file untuk Claude Code session
> **Includes:** Project context + Hallucination awareness
> **Generated:** 2026-04-16

---

## Project Context

**Type:** Node.js Application
...

---

## Hallucination Awareness

### Definisi: Apa itu Hallucination?
...

### Mengapa Hallucination Terjadi (Root Cause)
...

### Kapan Hallucination Paling Berpotensi Terjadi
...

### Core Rules: Kejujuran di Atas Segalanya
...

### User Checklist: Cara Mendeteksi Hallucination
...

### Quick Reference Card
...

---

> **Remember:** A helpful AI is an honest AI. Being honest is the right thing to do
> — and it's also part of how to be more helpful.
```

---

## Catatan Penting

1. **Jangan replace existing content** — hanya tambahkan hallucination sections
2. **Cek duplikasi** — jika user menjalankan skill ini dua kali, section kedua akan duplikat
3. **Bahasa konsisten** — gunakan Bahasa Indonesia untuk deskripsi, English untuk terminology teknis
4. **Source attribution** — selalu cantumkan video source di footer

---

## Troubleshooting

### "CLAUDE.md tidak ditemukan"
→ Buat baru dengan format lengkap (Step 3A)

### "Hallucination section sudah ada"
→ Skip dan beri tahu user

### "Mixed language di CLAUDE.md"
→ Normalize ke Bahasa Indonesia (atau English jika lebih majority)

### "Format tidak konsisten"
→ Reformat ulang dengan format standar yang sama
