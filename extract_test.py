from pypdf import PdfReader

reader = PdfReader("documents/tennant/tennant-t7-operator-manual.pdf")

print(f"num of pages: {len(reader.pages)}")

# Extract text from page 4 (the "Safety Precautions" section, based on the table of contents
# Using index 3 since pages are zero-indexed 
page_text = reader.pages[3].extract_text()
print("--- Page 4 text ---")
print(page_text)