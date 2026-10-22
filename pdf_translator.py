"""
PDF Translator - English to Indonesian
Translates PDF content while preserving the original layout and formatting
"""

import os
from pathlib import Path
try:
    import fitz  # PyMuPDF
    from deep_translator import GoogleTranslator
    from tqdm import tqdm
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'PyMuPDF', 'deep-translator', 'tqdm', '--break-system-packages'])
    import fitz
    from deep_translator import GoogleTranslator
    from tqdm import tqdm


class PDFTranslator:
    def __init__(self, input_pdf, output_pdf, source_lang='en', target_lang='id'):
        """
        Initialize PDF Translator
        
        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path to output PDF file
            source_lang: Source language code (default: 'en' for English)
            target_lang: Target language code (default: 'id' for Indonesian)
        """
        self.input_pdf = input_pdf
        self.output_pdf = output_pdf
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)
        
    def translate_text(self, text):
        """Translate text using Google Translator"""
        if not text or text.strip() == "":
            return text
        
        try:
            # Google Translator has a limit of 5000 characters
            if len(text) > 4500:
                # Split into chunks
                chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_chunks = [self.translator.translate(chunk) for chunk in chunks]
                return ' '.join(translated_chunks)
            else:
                return self.translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def translate_pdf_method1(self):
        """
        Method 1: Extract text blocks and overlay translated text
        Preserves layout by maintaining text positions
        """
        print(f"Opening PDF: {self.input_pdf}")
        doc = fitz.open(self.input_pdf)
        total_pages = len(doc)
        
        print(f"Total pages: {total_pages}")
        print("Translating PDF (Method 1: Text Overlay)...\n")
        
        for page_num in tqdm(range(total_pages), desc="Processing pages"):
            page = doc[page_num]
            
            # Get text blocks with positions
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Get original text and its properties
                            original_text = span["text"]
                            
                            if original_text.strip():
                                # Get text properties
                                font_size = span["size"]
                                font_name = span["font"]
                                color = span["color"]
                                bbox = span["bbox"]
                                
                                # Translate text
                                translated_text = self.translate_text(original_text)
                                
                                # Cover original text with white rectangle
                                page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
                                
                                # Insert translated text at the same position
                                try:
                                    page.insert_text(
                                        (bbox[0], bbox[3]),  # Position
                                        translated_text,
                                        fontsize=font_size,
                                        color=(0, 0, 0),  # Black color
                                        fontname="helv"  # Use Helvetica as fallback
                                    )
                                except Exception as e:
                                    print(f"Error inserting text on page {page_num + 1}: {e}")
        
        # Save translated PDF
        print(f"\nSaving translated PDF to: {self.output_pdf}")
        doc.save(self.output_pdf)
        doc.close()
        print("✓ Translation complete!")
    
    def translate_pdf_method2(self):
        """
        Method 2: Create new PDF with translated text
        Better for complex layouts
        """
        print(f"Opening PDF: {self.input_pdf}")
        doc = fitz.open(self.input_pdf)
        new_doc = fitz.open()  # New document
        total_pages = len(doc)
        
        print(f"Total pages: {total_pages}")
        print("Translating PDF (Method 2: New PDF Creation)...\n")
        
        for page_num in tqdm(range(total_pages), desc="Processing pages"):
            page = doc[page_num]
            
            # Create new page with same size
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            
            # Copy images and graphics
            new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # Get and translate text
            text_instances = page.get_text("dict")["blocks"]
            
            for block in text_instances:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        bbox = None
                        font_size = 11
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            if bbox is None:
                                bbox = list(span["bbox"])
                                font_size = span["size"]
                            else:
                                bbox[2] = max(bbox[2], span["bbox"][2])
                                bbox[3] = max(bbox[3], span["bbox"][3])
                        
                        if line_text.strip() and bbox:
                            # Translate
                            translated = self.translate_text(line_text)
                            
                            # Cover original area
                            new_page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1))
                            
                            # Add translated text
                            try:
                                new_page.insert_textbox(
                                    bbox,
                                    translated,
                                    fontsize=font_size * 0.9,  # Slightly smaller to fit
                                    color=(0, 0, 0),
                                    fontname="helv",
                                    align=0
                                )
                            except Exception as e:
                                print(f"Error on page {page_num + 1}: {e}")
        
        # Save
        print(f"\nSaving translated PDF to: {self.output_pdf}")
        new_doc.save(self.output_pdf)
        new_doc.close()
        doc.close()
        print("✓ Translation complete!")
    
    def translate_pdf_simple(self):
        """
        Method 3: Simple text extraction and translation
        Creates a new PDF with basic formatting
        """
        print(f"Opening PDF: {self.input_pdf}")
        doc = fitz.open(self.input_pdf)
        new_doc = fitz.open()
        total_pages = len(doc)
        
        print(f"Total pages: {total_pages}")
        print("Translating PDF (Method 3: Simple)...\n")
        
        for page_num in tqdm(range(total_pages), desc="Processing pages"):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            
            # Translate
            if text.strip():
                translated_text = self.translate_text(text)
                
                # Create new page
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # Insert translated text
                new_page.insert_textbox(
                    new_page.rect,
                    translated_text,
                    fontsize=11,
                    fontname="helv",
                    align=0
                )
        
        # Save
        print(f"\nSaving translated PDF to: {self.output_pdf}")
        new_doc.save(self.output_pdf)
        new_doc.close()
        doc.close()
        print("✓ Translation complete!")


def main():
    print("="*60)
    print("PDF TRANSLATOR - English to Indonesian")
    print("="*60)
    print()
    
    # Get input PDF path
    input_pdf = input("Masukkan path file PDF input: ").strip()
    
    if not os.path.exists(input_pdf):
        print(f"Error: File '{input_pdf}' tidak ditemukan!")
        return
    
    # Generate output filename
    input_path = Path(input_pdf)
    output_pdf = str(input_path.parent / f"{input_path.stem}_translated.pdf")
    
    print(f"\nFile output akan disimpan sebagai: {output_pdf}")
    
    # Choose method
    print("\nPilih metode translasi:")
    print("1. Method 1 - Text Overlay (mempertahankan format terbaik)")
    print("2. Method 2 - New PDF Creation (untuk layout kompleks)")
    print("3. Method 3 - Simple (paling cepat, format sederhana)")
    
    choice = input("\nPilih metode (1/2/3) [default: 1]: ").strip() or "1"
    
    # Create translator
    translator = PDFTranslator(input_pdf, output_pdf)
    
    # Execute translation
    print()
    if choice == "1":
        translator.translate_pdf_method1()
    elif choice == "2":
        translator.translate_pdf_method2()
    elif choice == "3":
        translator.translate_pdf_simple()
    else:
        print("Pilihan tidak valid, menggunakan Method 1...")
        translator.translate_pdf_method1()
    
    print(f"\n✓ File terjemahan berhasil disimpan: {output_pdf}")


if __name__ == "__main__":
    main()