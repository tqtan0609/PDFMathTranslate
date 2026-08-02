import sys
import pymupdf
from pathlib import Path

def split_pdf(input_path: str, chunk_size: int, out_dir: str):
    src = pymupdf.open(input_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    total = src.page_count
    n_chunks = (total + chunk_size - 1) // chunk_size

    for i in range(n_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, total) - 1
        dst = pymupdf.open()
        dst.insert_pdf(src, from_page=start, to_page=end)
        out_path = out_dir / f"chunk_{i+1:03d}_p{start+1}-{end+1}.pdf"
        dst.save(out_path)
        dst.close()
        print(f"saved {out_path} (trang {start+1}-{end+1})")

    src.close()
    print(f"Xong: {n_chunks} chunk, tổng {total} trang.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python split_pdf.py <input.pdf> <chunk_size> <out_dir>")
        sys.exit(1)
    split_pdf(sys.argv[1], int(sys.argv[2]), sys.argv[3])
