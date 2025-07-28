# main.py (Corrected with Absolute Paths)
import json
import os
import time

# Import the functions from our other scripts
from pdf_processor import process_pdfs_and_chunk_content
from semantic_analyzer import rank_chunks, get_refined_subsections

def run():
    """
    Executes the entire persona-driven document intelligence pipeline.
    """
    start_time = time.time()

    # --- 1. Load Inputs using absolute paths for Docker ---
    input_json_path = '/app/input/input.json'
    pdf_folder_path = '/app/input/PDFs/'
    
    with open(input_json_path, 'r') as f:
        input_data = json.load(f)

    pdf_filenames = [doc['filename'] for doc in input_data['documents']]
    
    persona = input_data['persona']['role']
    job_to_be_done = input_data['job_to_be_done']['task']
    user_query = f"{persona}: {job_to_be_done}"

    print("--- Starting Analysis ---")
    print(f"Persona: {persona}")
    print(f"Job: {job_to_be_done}")

    # --- 2. Process PDFs to get text chunks ---
    all_chunks = process_pdfs_and_chunk_content(pdf_filenames, pdf_folder_path)
    if not all_chunks:
        print("\nNo content could be extracted from the PDFs. Exiting.")
        return

    # --- 3. Rank the chunks to find top sections ---
    ranked_chunks = rank_chunks(user_query, all_chunks)
    
    # --- 4. Select top sections with diversity ---
    top_5_sections = []
    seen_documents = set()
    for chunk in ranked_chunks:
        if len(top_5_sections) >= 5:
            break
        if chunk['doc_name'] not in seen_documents:
            top_5_sections.append(chunk)
            seen_documents.add(chunk['doc_name'])

    if len(top_5_sections) < 5:
        remaining_needed = 5 - len(top_5_sections)
        remaining_chunks = [c for c in ranked_chunks if c not in top_5_sections]
        top_5_sections.extend(remaining_chunks[:remaining_needed])

    # --- 5. Get refined subsections from the top sections ---
    refined_subsections = get_refined_subsections(user_query, top_5_sections)

    # --- 6. Assemble the final JSON output ---
    print("Assembling final output JSON...")
    output_data = {
        "metadata": {
            "input_documents": pdf_filenames,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": [],
        "subsection_analysis": refined_subsections
    }

    for i, section in enumerate(top_5_sections):
        output_data["extracted_sections"].append({
            "document": section["doc_name"],
            "section_title": section["section_title"],
            "importance_rank": i + 1,
            "page_number": section["page_num"]
        })

    # --- 7. Write the output to a file ---
    output_folder = '/app/output/'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_file_path = os.path.join(output_folder, 'output.json')
    with open(output_file_path, 'w') as f:
        json.dump(output_data, f, indent=4)
    
    end_time = time.time()
    print(f"\n--- Analysis Complete ---")
    print(f"Final output saved to: {output_file_path}")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    run()