import pypdf
import sys

def main(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        with open('extracted_text.txt', 'w', encoding='utf-8') as out_file:
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                out_file.write(f"--- Page {page_num + 1} ---\n")
                out_file.write(text + "\n")

if __name__ == "__main__":
    main(sys.argv[1])

