import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI
from document_loader import extract_text_from_pdf, chunk_text

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def build_index_for_folder(folder_path):
    pdf_paths = glob.glob(os.path.join(folder_path, "*.pdf"))
    print(f"Found {len(pdf_paths)} PDF(s) in {folder_path}: {[os.path.basename(p) for p in pdf_paths]}")

    all_indexed_chunks = []
    for pdf_path in pdf_paths:
        print(f"Reading {pdf_path}...")
        text = extract_text_from_pdf(pdf_path)
        chunks = chunk_text(text, chunk_size=400, overlap=80)
        print(f"  Split into {len(chunks)} chunks. Generating embeddings...")

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            all_indexed_chunks.append({
                "text": chunk,
                "embedding": embedding,
                "source": os.path.basename(pdf_path)  # track which PDF this came from
            })
            print(f"    Embedded chunk {i + 1}/{len(chunks)} from {os.path.basename(pdf_path)}")

    output_path = os.path.join(folder_path, "index.json")
    with open(output_path, "w") as f:
        json.dump(all_indexed_chunks, f)

    print(f"Saved combined index to {output_path} ({len(all_indexed_chunks)} total chunks)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 build_index.py <folder_path>")
        sys.exit(1)
    build_index_for_folder(sys.argv[1])