from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    """Reads a PDF and returns all its text as one big string."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text: # some pages might return None or empty
            full_text += text + "\n"
    return full_text

def chunk_text(text, chunk_size=400, overlap=80):
    """Splits text into overlapping chunks of roughly chunk_size characters"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap  # move start forward by chunk_size - overlap
    return chunks

if __name__ == "__main__":
    text = extract_text_from_pdf("documents/tennant/tennant-t7-operator-manual.pdf")
    print(f"Total characters extracted: {len(text)}")

    chunks = chunk_text(text)
    print(f"Num of chunks created: {len(chunks)}")

    print("\n--- First chunk ---")
    print(chunks[0])

    print("\n--- Second chunk (notice the overlap with the end of the first) ---")
    print(chunks[1])