import fitz  # PyMuPDF
import os
import re

# Import the main function from your Round 1A code
from outline_extractor import extract_outline

def process_pdfs_and_chunk_content(pdf_filenames, input_folder_path):
    """
    Reads PDFs, uses the outline_extractor to get headings, and then
    chunks the content based on those headings.
    """
    all_chunks = []
    print("Starting PDF processing with heading extraction...")

    for filename in pdf_filenames:
        pdf_path = os.path.join(input_folder_path, filename)
        
        if not os.path.exists(pdf_path):
            print(f"Warning: PDF file not found at {pdf_path}. Skipping.")
            continue

        print(f"  - Processing: {filename}")
        
        # 1. Get the structured outline from your 1A code
        outline_data = extract_outline(pdf_path)
        headings = outline_data.get("outline", [])
        
        if not headings:
            print(f"    - No headings found for {filename}. Skipping chunking for this file.")
            continue

        # 2. Extract full text from the document
        doc = fitz.open(pdf_path)
        full_text = " ".join(page.get_text() for page in doc)
        doc.close()

        # Clean up the text: remove newlines, multiple spaces, and unicode bullets
        full_text = full_text.replace('\n', ' ').replace('\u2022', '')
        full_text = re.sub(' +', ' ', full_text)

        # 3. Chunk the document using headings as dividers
        # We create a regex pattern that looks for any of the heading texts
        heading_texts = [h['text'] for h in headings]
        # Escape special regex characters in headings
        escaped_headings = [re.escape(text) for text in heading_texts]
        split_pattern = '|'.join(escaped_headings)
        
        if not split_pattern:
            continue

        # Split the full text by the headings, the first element is text before the first heading
        split_content = re.split(f'({split_pattern})', full_text)

        # 4. Re-assemble the chunks with their correct headings
        current_heading_index = -1
        for i, part in enumerate(split_content):
            if not part.strip():
                continue
            
            # If the part is one of our headings, it marks the start of a new section
            if part in heading_texts:
                current_heading_index = heading_texts.index(part)
            # Otherwise, it's the content that follows a heading
            elif current_heading_index != -1:
                heading_info = headings[current_heading_index]
                all_chunks.append({
                    "doc_name": filename,
                    "page_num": heading_info['page'],
                    "section_title": heading_info['text'],
                    "text": part.strip()
                })
                # Reset to avoid assigning same content to multiple headings
                current_heading_index = -1

    print(f"PDF processing complete. Found {len(all_chunks)} structured text chunks.")
    return all_chunks