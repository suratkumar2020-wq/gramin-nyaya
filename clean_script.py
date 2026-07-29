import re

input_file = "legal_docs/registrationActEnglish.txt"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# The first 147 lines are the Table of Contents, which we skip.
if len(lines) > 150:
    if "THE REGISTRATION ACT, 1908" in lines[147]:
        lines = lines[147:]
    else:
        # Just in case the file was already cleaned
        pass

cleaned_lines = []
for line in lines:
    # 1. Remove isolated page numbers (lines with just numbers)
    if re.match(r'^\s*\d+\s*$', line):
        continue
        
    # 2. Remove common footnote indicators (e.g., "1. Subs. by...")
    if re.match(r'^\d+\.\s*(Subs\.|Ins\.|The word|The proviso|Clause|Sub-section)', line):
        continue
    
    # 3. Remove lines that are just asterisks (footnote dividers)
    if re.match(r'^\s*\*\s*$', line) or re.match(r'^\s*\*\s*\*\s*\*\s*$', line):
        continue
        
    cleaned_lines.append(line)

with open(input_file, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)

print(f"✅ Successfully cleaned the document! Reduced from {len(lines)} to {len(cleaned_lines)} lines.")
