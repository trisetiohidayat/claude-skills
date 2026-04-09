---
name: mermaid-diagram
description: |
  Membuat dan menghasilkan diagram Mermaid untuk visualisasi. Gunakan skill ini ketika:
  - User ingin menggambarkan sesuatu dalam bentuk diagram/flowchart
  - User meminta "buat flowchart", "bikin diagram", "gambarkan proses X"
  - User ingin visualisasi alur (flow), sequence, class diagram, ER diagram
  - User menyebut "mermaid", "diagram Mermaid", atau ".mmd"
  - User ingin convert deskripsi teks ke diagram Mermaid
  - User ingin membuat flowchart dari JSON/YAML config
  - User ingin dokumentasi dengan embedded diagram

  Skill ini mendukung: flowchart, sequence diagram, class diagram, ER diagram, state diagram, gantt chart, pie chart, journey, dan lain-lain.
---

# Mermaid Diagram Skill

## Overview

Skill ini digunakan untuk membuat diagram Mermaid dari:
1. **Deskripsi natural language** - Teks yang menjelaskan alur/proses
2. **File JSON/YAML** - Konfigurasi struktur data
3. **Konsep/logika** - Ide yang perlu divisualisasikan

Output yang dihasilkan:
- Kode Mermaid (`.mmd` file)
- Markdown dengan embedded diagram (` ```mermaid `)

---

## Step 1: Identifikasi Tipe Diagram

Pilih tipe diagram yang sesuai berdasarkan konteks:

| Konteks | Tipe Diagram |
|---------|--------------|
| Proses bisnis, workflow, alur keputusan | `flowchart` atau `flowchart TD` |
| Interaksi antar objek/aktor | `sequenceDiagram` |
| Struktur class dan relasi OOP | `classDiagram` |
| Schema database | `erDiagram` |
| Finite state machine | `stateDiagram-v2` |
| Timeline project | `gantt` |
| Distribusi data | `pie` |
| User journey | `journey` |
| C4 diagrams | `C4Context` |

---

## Step 2: Parse Input

### A. Natural Language → Mermaid

Jika input adalah deskripsi teks:

1. **Identifikasi node/aktor** - Siapa/s apa saja yang terlibat
2. **Identifikasi hubungan** - Bagaimana node terhubung
3. **Identifikasi arah alur** - Arah panah/arah proses
4. **Konversi ke syntax Mermaid** - Ikuti format yang benar

### B. JSON/YAML → Mermaid

Jika input dari file config:

```json
{
  "diagram": "flowchart",
  "nodes": [
    {"id": "A", "label": "Start"},
    {"id": "B", "label": "Process"},
    {"id": "C", "label": "End"}
  ],
  "edges": [
    {"from": "A", "to": "B"},
    {"from": "B", "to": "C"}
  ]
}
```

Konversi ke:

```mermaid
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]
```

---

## Step 3: Generate Mermaid Code

### Flowchart Syntax

```mermaid
flowchart TD
    %% Arah: TD (top-down), LR (left-right), BT, RL

    Start([Mulai]) --> Process{Decision?}
    Process -->|Yes| Action1[Action Yes]
    Process -->|No| Action2[Action No]
    Action1 --> End1([Selesai])
    Action2 --> End2([Selesai])

    %% Styling (opsional)
    classDef primary fill:#f96,stroke:#333,stroke-width:2px;
    class Start,End1,End2 primary
```

### Sequence Diagram Syntax

```mermaid
sequenceDiagram
    participant A as Actor 1
    participant B as Actor 2
    participant S as System

    A->>S: Request
    alt success case
        S-->>A: Response OK
    else error case
        S--xA: Error Message
    end
```

### Class Diagram Syntax

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    Animal <|-- Dog : inherits
```

### ER Diagram Syntax

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : "is in"
```

### State Diagram Syntax

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted: submit
    Submitted --> Approved: approve
    Submitted --> Rejected: reject
    Approved --> [*]
    Rejected --> Draft: revise
```

### Gantt Chart Syntax

```mermaid
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Task 1: 2024-01-01, 7d
    Task 2: 7d
    section Phase 2
    Task 3: after Task 2, 5d
```

---

## Step 4: Output Generation

### A. Output ke File .mmd

Simpan kode Mermaid ke file:

```bash
# Example filename: workflow.mmd
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]
```

### B. Output ke Markdown

Tambahkan ke dokumentasi dengan code block:

```markdown
## Workflow Diagram

```mermaid
flowchart LR
    A[Start] --> B[Process]
    B --> C[End]
```
```

---

## Best Practices

1. **Gunakan label yang jelas** - Nama node harus deskriptif
2. **Arah yang konsisten** - Pilih TD, LR, BT, atau RL dan konsisten
3. **Warna untuk kategori** - Gunakan classDef untuk grouping
4. **Komentar untuk kompleksitas** - Tambahkan komentar untuk alur yang rumit
5. **Subgraph untuk grouping** - Kelompokkan node terkait

```mermaid
flowchart TB
    subgraph Backend
        A[API] --> B[Service]
        B --> C[Database]
    end

    subgraph Frontend
        D[UI] --> A
    end
```

---

## Contoh转换

### Input: "User login process"
```
User enters credentials → System validates →
If valid → Grant access → Dashboard
If invalid → Show error → Return to login
```

### Output:
```mermaid
flowchart LR
    A[User enters credentials] --> B{System validates}
    B -->|Valid| C[Grant access]
    B -->|Invalid| D[Show error]
    C --> E[Dashboard]
    D --> A
```

---

## Catatan Penting

- Untuk preview: Bisa gunakan https://mermaid.live/ atau VS Code extension
- Untuk dokumentasi: Selalu gunakan fenced code block dengan ```mermaid
- Untuk file: Simpan dengan ekstensi .mmd
- State diagram: Gunakan `stateDiagram-v2` untuk fitur lengkap
- Gantt: Gunakan format `YYYY-MM-DD` untuk tanggal
