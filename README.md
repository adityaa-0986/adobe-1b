# Adobe Hackathon 2025: Persona-Driven Document Intelligence

This project is a solution for Round 1B of the "Connecting the Dots" Hackathon. It functions as an intelligent document analyst that extracts and prioritizes the most relevant sections from a collection of PDFs based on a specific user persona and their job-to-be-done.

## Our Approach

The solution employs a multi-stage pipeline to process, understand, and rank document content, ensuring both high relevance and content diversity in the final output.

### 1. Hybrid Heading Extraction
The process begins with a robust heading extraction module (`outline_extractor.py`) that analyzes each PDF. To ensure accuracy across different document formats, it uses a hybrid strategy:
* It first attempts to use the PDF's built-in Table of Contents (TOC) if one exists.
* If no TOC is found, it performs a deep analysis of the document's text, identifying headings based on font characteristics like **font size** and **font weight (bolding)**. This allows it to find headings even in documents that don't use larger fonts for titles.

### 2. Intelligent Content Chunking
Once the headings are identified, the `pdf_processor.py` script intelligently splits the document's text into meaningful chunks. Each chunk consists of a heading and the complete text content that follows it, preserving the document's original structure.

### 3. Context-Aware Semantic Ranking
This is the core of the intelligence. We use a pre-trained Sentence Transformer model (`all-MiniLM-L6-v2`) to perform semantic analysis.
* The user's `persona` and `job_to_be_done` are combined into a single, focused query.
* Crucially, to provide the model with maximum context, we create embeddings from the combined **`section_title + chunk_text`**. This is more effective than analyzing the text alone.
* The relevance of each chunk is calculated using Cosine Similarity between its embedding and the user query's embedding.

### 4. Diversity-Enforced Selection
To ensure the final output is a comprehensive overview rather than a list of results from a single document, a diversity rule is applied. The final selection logic in `main.py` prioritizes pulling the top-ranked sections from a **variety of different source documents**, ensuring a well-rounded and highly useful summary for the user.

### 5. Granular Subsection Analysis
Finally, for the top-ranked sections, the system performs a deeper analysis. It breaks down the section text into individual sentences and uses a similarity threshold to pull out the most relevant granular snippets, which are presented in the `subsection_analysis` portion of the final output.

## Models and Libraries Used

* **Model**: `all-MiniLM-L6-v2` (from the Sentence-Transformers library). This model was chosen for its excellent balance of performance and size (~80MB), easily fitting within the 1GB constraint.
* **Core Libraries**:
    * `PyMuPDF`: For fast and efficient PDF text and metadata extraction.
    * `sentence-transformers` & `torch`: For generating text embeddings and performing semantic analysis.
    * `scikit-learn` & `numpy`: For performing the high-speed Cosine Similarity calculations.

## How to Build and Run

The project is designed to be run within a Docker container as per the hackathon requirements.

### Prerequisites
* Docker must be installed and running.

