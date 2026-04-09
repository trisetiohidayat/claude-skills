---
name: docx
description: "Use this skill any time a .docx file is involved in any way — as input, output, or both. This includes: creating Word documents, reading or extracting text from any .docx file, editing or modifying existing Word documents, working with templates, tables, styles, comments, or track changes. Trigger when the user mentions 'Word', '.docx', or asks to create/edit/produce a Word document."
license: Proprietary. LICENSE.txt has complete terms
---

# DOCX Skill

This document is technical documentation for a DOCX skill describing how to create, edit, and analyze Word documents. Key features include:

**Creation:** Use docx-js npm library with JavaScript to generate documents, setting explicit page sizes (US Letter is 12240×15840 DXA), using LevelFormat.BULLET for lists (never unicode), and dual-width tables.

**Editing:** Unpack DOCX → edit XML → repack using provided Python scripts. Track changes with `<w:ins>` and `<w:del>` elements.

**Critical rules:** No `\n` in paragraphs, PageBreak must wrap in Paragraph, ImageRun requires type parameter, use WidthType.DXA (never percentage) for tables.
