# XLSX Skill

Guidelines for creating, editing, and analyzing .xlsx files using Python.

## Core Philosophy

- Use **Excel formulas**, not hardcoded calculated values
- Professional formatting with Arial/Times New Roman
- Zero formula errors in deliverables
- Preserve existing template formatting

## Color Coding Standard

Use this color scheme in financial models:

| Color | Meaning | RGB |
|-------|---------|-----|
| Blue | Inputs / Assumptions | #0070C0 |
| Black | Formulas | #000000 |
| Green | Internal links | #00B050 |
| Red | External links | #FF0000 |
| Yellow | Key assumptions | #FFFF00 |

## Number Formatting

- Years: display as text (2024, 2025, etc.)
- Currency: show $ symbol and units (e.g., $1.2M)
- Zeros: display as "-"
- Negatives: use parentheses (e.g., (100))

## Tools

- **pandas**: data analysis, CSV conversion, simple operations
- **openpyxl**: formulas, formatting, Excel-specific features

## Workflow

1. Create formulas (never hardcode calculated values)
2. Run `scripts/recalc.py` to recalculate and verify zero errors
3. Deliver the spreadsheet file (not HTML, not scripts)

## Recalculation

After creating formulas, always run the recalculation script to verify:

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

This uses LibreOffice to recalculate all formulas and checks for:
- #VALUE!
- #DIV/0!
- #REF!
- #NAME?
- #NULL!
- #NUM!
- #N/A

## Office Scripts

The `scripts/office/` directory contains utilities for working with Office files:

- `recalc.py`: Recalculate Excel formulas using LibreOffice
- `pack.py`: Pack directory into DOCX/PPTX/XLSX
- `unpack.py`: Unpack Office files for editing
- `validate.py`: Validate Office document XML

### Prerequisites

These scripts require:
- Python 3.8+
- openpyxl
- pandas
- defusedxml
- lxml
- LibreOffice

Install with:
```bash
pip install openpyxl pandas defusedxml lxml
```
