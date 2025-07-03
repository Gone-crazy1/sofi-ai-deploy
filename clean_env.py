#!/usr/bin/env python3
"""Clean .env file from null characters"""

# Read the .env file and clean null characters
with open('.env', 'rb') as f:
    content = f.read()

# Remove null characters
cleaned = content.replace(b'\x00', b'')

print(f"Removed {len(content) - len(cleaned)} null bytes")

# Write the cleaned content back
with open('.env', 'wb') as f:
    f.write(cleaned)

print("✅ .env file cleaned")
