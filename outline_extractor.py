# outline_extractor.py (Definitive Hybrid Version)
import fitz  # PyMuPDF

def get_document_title(doc):
    """
    Extracts the document title using metadata as a priority,
    falling back to the largest text on the first page.
    """
    if doc.metadata and doc.metadata.get("title"):
        title = doc.metadata.get("title").strip()
        # A basic filter to avoid garbage metadata titles
        if len(title) > 3 and len(title.split()) < 20:
            return title

    if doc.page_count > 0:
        # Fallback to finding the largest font size on the first page
        page = doc[0]
        max_size = 0
        potential_title = ""
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if line["spans"]:
                        line_text = "".join(s["text"] for s in line["spans"]).strip()
                        # A title should not be excessively long
                        if len(line_text.split()) < 15:
                            span = line["spans"][0]
                            if span["size"] > max_size:
                                max_size = span["size"]
                                potential_title = line_text
        if potential_title:
             return potential_title

    return "Untitled Document"

# In outline_extractor.py

def analyze_document_with_font_analysis(doc):
    """
    Performs a single-pass analysis that checks for font size AND font weight (bold)
    to identify headings. Highly accurate and filters common noise.
    """
    font_data = {}
    # --- Single-pass data collection ---
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        header_margin, footer_margin = page_height * 0.07, page_height * 0.93

        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    if not line["spans"]: continue
                    
                    y0 = line["bbox"][1]
                    if y0 < header_margin or y0 > footer_margin: continue

                    for span in line["spans"]:
                        line_text = span["text"].strip()
                        if not line_text or len(line_text) < 3 or line_text.isnumeric(): continue

                        size = round(span["size"], 1)
                        font_name = span["font"]
                        is_bold = "bold" in font_name.lower() or "black" in font_name.lower()

                        if size not in font_data:
                            font_data[size] = {"count": 0, "lines": []}
                        
                        font_data[size]["count"] += 1
                        font_data[size]["lines"].append({
                            "text": line_text, 
                            "page": page_num + 1, 
                            "bold": is_bold
                        })

    if not font_data: return []

    # --- Heuristic-based heading detection ---
    primary_body_size = max(font_data, key=lambda s: font_data[s]['count'])

    outline = []
    # Identify headings: text that is BOLD and at least body size, OR text that is significantly larger.
    for size, data in font_data.items():
        is_potential_heading_size = (size > primary_body_size * 1.15)
        
        for line_info in data["lines"]:
            # A line is a heading if it's bold (and not tiny) OR if its font size is larger than body text
            is_bold_heading = (line_info["bold"] and size >= primary_body_size)
            
            if is_bold_heading or is_potential_heading_size:
                # Basic filter for list items or other noise
                if not line_info["text"].startswith(('•', 'o', '-', '*')):
                    outline.append({
                        # We can't know the H1/H2 level easily here, so we'll assign a generic level
                        "level": "H2", 
                        "text": line_info["text"], 
                        "page": line_info["page"]
                    })

    # Remove duplicate headings that might be picked up
    unique_outline = [dict(t) for t in {tuple(d.items()) for d in outline}]
    return sorted(unique_outline, key=lambda x: (x['page'], x['text']))


def extract_outline(pdf_path):
    """
    Definitive extraction function that uses a hybrid strategy. It tries
    the fast TOC method first and falls back to a high-accuracy font analysis.
    """
    try:
        doc = fitz.open(pdf_path)
        title = get_document_title(doc)

        # --- Strategy 1: The Instant Method (Built-in TOC) ---
        toc = doc.get_toc()
        if toc:
            # If a TOC exists, use it directly as it's the most reliable source
            outline = [{"level": f"H{min(lvl, 3)}", "text": text, "page": page} for lvl, text, page in toc]
            doc.close()
            return {"title": title, "outline": outline}

        # --- Strategy 2: The Accurate Fallback (Deep Font Analysis) ---
        outline = analyze_document_with_font_analysis(doc)

        doc.close()
        return {"title": title, "outline": outline}

    except Exception as e:
        print(f"An unexpected error occurred while processing {pdf_path}: {e}")
        return {"title": "Error Processing Document", "outline": []}