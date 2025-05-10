# import os
# from rapidfuzz import fuzz

# # Check if the new title is similar to any in the unique list
# def is_similar(title, unique_titles, threshold=90):
#     for existing in unique_titles:
#         if fuzz.ratio(title.lower(), existing.lower()) >= threshold:
#             return True
#     return False

# # Root directory to start from
# root_folder = r"D:\Research Paper\Wind Research Paper\Review Reference Papers"

# all_titles = []

# # Walk through all folders and subfolders to find paper_titles.txt
# for dirpath, dirnames, filenames in os.walk(root_folder):
#     for filename in filenames:
#         if filename == 'paper_titles.txt':
#             file_path = os.path.join(dirpath, filename)
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as file:
#                     titles = [line.strip() for line in file if line.strip()]
#                     all_titles.extend(titles)
#                     print(f"✔ Read {len(titles)} titles from: {file_path}")
#             except Exception as e:
#                 print(f"❌ Error reading {file_path}: {e}")

# # Apply fuzzy matching to remove near-duplicates across all files
# fuzzy_unique_titles = []
# for title in all_titles:
#     if not is_similar(title, fuzzy_unique_titles):
#         fuzzy_unique_titles.append(title)

# # Print summary
# print("\n--- Summary ---")
# print(f"📄 Total titles (raw count across files): {len(all_titles)}")
# print(f"✨ Total fuzzy-unique titles: {len(fuzzy_unique_titles)}")

# # Optional: Save fuzzy-unique titles to a new file
# output_file = 'fuzzy_unique_titles.txt'
# with open(output_file, 'w', encoding='utf-8') as f:
#     for title in fuzzy_unique_titles:
#         f.write(title + '\n')

# print(f"\n💾 Fuzzy-unique titles saved to: {output_file}")


import os
from rapidfuzz import fuzz
from openpyxl import Workbook

def find_match(title, unique_titles, threshold=90):
    """
    Returns matched title and score if similar title exists, else (None, 0)
    """
    for existing in unique_titles:
        score = fuzz.ratio(title.lower(), existing.lower())
        if score >= threshold:
            return existing, score
    return None, 0

root_folder = r"D:\Research Paper\Wind Research Paper\Review Reference Papers"

all_titles = []

# Step 1: Traverse folders and collect all titles
for dirpath, dirnames, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename == 'paper_titles.txt':
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    titles = [line.strip() for line in file if line.strip()]
                    all_titles.extend(titles)
                    print(f"✔ Read {len(titles)} titles from: {file_path}")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")

# Step 2: Identify unique and duplicate titles using fuzzy matching
fuzzy_unique_titles = []
duplicates = []  # (duplicate_title, matched_unique_title, score)

for title in all_titles:
    matched_title, score = find_match(title, fuzzy_unique_titles)
    if matched_title:
        duplicates.append((title, matched_title, score))
    else:
        fuzzy_unique_titles.append(title)

# Step 3: Save results to Excel
output_excel = 'fuzzy_matched_titles.xlsx'
wb = Workbook()

# Sheet 1: Unique Titles
ws_unique = wb.active
ws_unique.title = "Unique Titles"
ws_unique.append(["Index", "Unique Paper Title"])
for idx, title in enumerate(fuzzy_unique_titles, start=1):
    ws_unique.append([idx, title])

# Sheet 2: Duplicates
ws_dup = wb.create_sheet(title="Duplicates")
ws_dup.append(["Duplicate Title", "Matched Unique Title", "Similarity Score (%)"])
for dup_title, matched, score in duplicates:
    ws_dup.append([dup_title, matched, score])

wb.save(output_excel)

# Summary
print("\n--- Summary ---")
print(f"📄 Total titles (raw count): {len(all_titles)}")
print(f"✅ Unique titles (fuzzy matched): {len(fuzzy_unique_titles)}")
print(f"♻ Duplicate titles found: {len(duplicates)}")
print(f"\n💾 Excel saved as: {output_excel}")
