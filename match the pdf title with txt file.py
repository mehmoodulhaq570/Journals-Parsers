# This script matches PDF filenames in a specified folder with titles from a text file.
# It uses fuzzy string matching to find similar titles and saves unmatched titles back to the text file.

import os
import re
import shutil
from fuzzywuzzy import fuzz

def load_titles_from_txt(txt_file):
    with open(txt_file, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def save_titles_to_txt(txt_file, titles):
    with open(txt_file, "w", encoding="utf-8") as file:
        for title in titles:
            file.write(title + "\n")

def normalize(text):
    return re.findall(r'\b\w+\b', text.lower())

def main():
    pdf_folder = r"C:\Users\mehmo\Downloads\rpdownloader2\downloads"
    txt_file = r"titles.txt"
    match_folder = os.path.join(pdf_folder, "match")
    matched_titles_file = os.path.join(pdf_folder, "matched_titles.txt")

    # Create match folder if it doesn't exist
    os.makedirs(match_folder, exist_ok=True)

    txt_titles = load_titles_from_txt(txt_file)
    print(f"Loaded {len(txt_titles)} titles.")

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    normalized_filenames = [(f, normalize(os.path.splitext(f)[0])) for f in pdf_files]

    remaining_titles = []
    matched_titles = []

    for title in txt_titles:
        matched = False

        for filename, _ in normalized_filenames:
            similarity_score = fuzz.token_set_ratio(title.lower(), filename.lower())

            if similarity_score >= 75:
                print(f'MATCHED: "{title}" <==> "{filename}"')
                matched = True
                matched_titles.append(title)

                # Copy matched PDF to match folder
                source_path = os.path.join(pdf_folder, filename)
                destination_path = os.path.join(match_folder, filename)
                shutil.copy2(source_path, destination_path)
                break

        if not matched:
            remaining_titles.append(title)

    save_titles_to_txt(txt_file, remaining_titles)
    save_titles_to_txt(matched_titles_file, matched_titles)

    print(f"\n✅ Done!")
    print(f"Matched PDFs copied to: {match_folder}")
    print(f"Matched titles saved to: {matched_titles_file}")
    print(f"Remaining unmatched titles saved to: {txt_file}")

# Run the script
main()
