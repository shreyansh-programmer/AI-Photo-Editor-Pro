import base64
import zlib
import urllib.request
import os

os.chdir(r"c:\Users\Shreyansh\OneDrive\Desktop\Advance Editor")

with open('diagram.mmd', 'r') as f:
    text = f.read()

compressed = zlib.compress(text.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

url = f"https://kroki.io/mermaid/svg/{encoded}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Downloading from {url}")
try:
    with urllib.request.urlopen(req) as response, open('High_Level_Architecture.svg', 'wb') as out_file:
        out_file.write(response.read())
    print("Successfully downloaded High_Level_Architecture.svg")
except Exception as e:
    print(f"Error: {e}")
