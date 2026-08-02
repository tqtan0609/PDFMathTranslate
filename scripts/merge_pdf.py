import sys
import glob
import pymupdf

def merge_pdfs(pattern: str, output_path: str):
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"Không tìm thấy file nào khớp: {pattern}")
        sys.exit(1)

    out = pymupdf.open()
    for f in files:
        print(f"ghép {f}")
        with pymupdf.open(f) as doc:
            out.insert_pdf(doc)
    out.save(output_path)
    out.close()
    print(f"Xong: {len(files)} file -> {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python merge_pdf.py "translated/*/*-mono.pdf" output.pdf')
        sys.exit(1)
    merge_pdfs(sys.argv[1], sys.argv[2])
