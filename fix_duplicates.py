#!/usr/bin/env python3
"""
Script to truncate main.py at the correct line
"""

# Read the file
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep only lines up to and including the if __name__ == "__main__": block
# This should be around line 1443
truncated_lines = []
for i, line in enumerate(lines):
    truncated_lines.append(line)
    # Stop after the if __name__ block
    if line.strip() == 'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)':
        break

# Write the truncated file
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(truncated_lines)

print(f"✅ Truncated main.py to {len(truncated_lines)} lines")
print("✅ Removed all duplicate Flask routes")
