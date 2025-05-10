import os

def count_pdfs_in_directory(directory_path):
    pdf_count = 0
    for root, _, files in os.walk(directory_path):
        pdf_count += sum(1 for file in files if file.lower().endswith('.pdf'))
    return pdf_count

# Example usage
directory_path = r"D:\Research Paper\Wind Research Paper\Review Reference Papers"  # Replace with your actual path
pdf_count = count_pdfs_in_directory(directory_path)
print(f"Total PDF files found: {pdf_count}")
