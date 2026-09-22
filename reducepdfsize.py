from pymupdf import PyUnicode_DecodeRawUnicodeEscape
import os
import pymupdf  # Also known as fitz

# --- CONFIGURATION ---
# Change this to your target directory path
script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)
FOLDER_PATH = script_dir 
# ---------------------

def compress_pdf_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Error: The folder '{folder_path}' does not exist.")
        return

    # Create a destination folder for compressed files so originals are safe
    output_folder = os.path.join(folder_path, "Compressed_PDFs")
    os.makedirs(output_folder, exist_ok=True)

    # Gather all PDF files in the directory
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return

    print(f"Found {len(pdf_files)} PDF(s). Starting compression...\n")

    for file_name in pdf_files:
        input_path = os.path.join(folder_path, file_name)
        output_path = os.path.join(output_folder, file_name)
        
        try:
            # Open the PDF document
            doc = pymupdf.open(input_path)
            
            # 1. Compress & downsample images (DPI 150 is ideal for reading on screens)
            doc.rewrite_images(
                dpi_threshold=150,  # Only change images larger than 150 DPI
                dpi_target=75,     # Downsample to 150 DPI
                quality=50,         # Compress JPEG quality to 70%
                lossy=True
            )
            
            # 2. Subset embedded fonts (Removes unused text glyphs from the file)
            if hasattr(doc, "subset_fonts"):
                doc.subset_fonts()

            # 3. Save with strict garbage collection to wipe out deleted data/duplicates
            doc.save(
                output_path, 
                garbage=4,          # Deep cleaning of duplicate streams and unreferenced objects
                deflate=True,       # Compresses uncompressed content streams
                use_objstms=True    # Packs object definitions into tight streams
            )
            doc.close()

            # Calculate and display the size difference
            orig_size = os.path.getsize(input_path) / (1024 * 1024)
            new_size = os.path.getsize(output_path) / (1024 * 1024)
            reduction = ((orig_size - new_size) / orig_size) * 100
            
            print(f"✓ {file_name}: {orig_size:.2f}MB → {new_size:.2f}MB (-{reduction:.1f}%)")

        except Exception as e:
            print(f"✗ Failed to compress {file_name}. Error: {e}")

    print(f"\nDone! Processed PDFs are saved in: {output_folder}")

if __name__ == "__main__":
    compress_pdf_folder(FOLDER_PATH)
