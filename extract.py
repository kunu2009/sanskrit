# extract_sanskrit_pdfs_to_json.py
# Run with: python extract_sanskrit_pdfs_to_json.py
# Requirements: PyPDF2 (pip install PyPDF2)

import json
from pathlib import Path
from PyPDF2 import PdfReader

def extract_pdf_to_pages(path: Path):
    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            text = f"[EXTRACTION ERROR on page {i+1}: {e}]"
        pages.append({"page_number": i+1, "text": text})
    full_text = "\n\n".join(p["text"] for p in pages)
    return pages, full_text

def build_app_structure(source_name, pages, full_text):
    # Simple heuristic structure for a teaching app.
    # We'll keep raw pages + split full_text into "lessons" by blank-line headings if possible.
    lessons = []
    # naive split on large blank line runs - adapt later for real headings
    blocks = [b.strip() for b in full_text.split("\n\n\n") if b.strip()]
    if not blocks:
        blocks = [full_text] if full_text.strip() else []
    for idx, block in enumerate(blocks, start=1):
        lesson = {
            "lesson_id": f"{source_name}_lesson_{idx}",
            "title": None,                # try to auto-detect titles later (by checking first line)
            "raw_text": block,
            "transliteration": "",        # placeholder for automatic transliteration (add later)
            "translation": "",            # placeholder for translation
            "vocabulary": [],             # list of {word, meaning}
            "grammar_points": [],         # list of grammar notes
            "exercises": []               # list of exercises/qa
        }
        # attempt to detect title as first short line
        first_line = block.splitlines()[0].strip() if block.splitlines() else ""
        if 0 < len(first_line) < 120 and (" " in first_line or len(first_line) < 40):
            lesson["title"] = first_line
        lessons.append(lesson)
    return {
        "source": source_name,
        "num_pages": len(pages),
        "pages": pages,
        "lessons": lessons,
        "full_text": full_text
    }

def main():
    folder = Path(".")
    pdfs = list(folder.glob("*.pdf"))
    if not pdfs:
        print("No PDF files found in current folder. Put your PDFs in the same folder as this script.")
        return
    outputs = []
    out_dir = folder / "extracted_json"
    out_dir.mkdir(exist_ok=True)
    for pdf in pdfs:
        pages, full_text = extract_pdf_to_pages(pdf)
        structured = build_app_structure(pdf.stem, pages, full_text)
        out_path = out_dir / f"{pdf.stem}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)
        outputs.append(str(out_path))
        print(f"Wrote {out_path}")
    combined = out_dir / "combined.json"
    with combined.open("w", encoding="utf-8") as f:
        json.dump([json.load(open(p, encoding="utf-8")) for p in outputs], f, ensure_ascii=False, indent=2)
    print(f"Wrote combined JSON: {combined}")

if __name__ == "__main__":
    main()
