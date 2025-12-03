"""
Update test_generate.py to use headers instead of license_key in body.
"""

import re
from pathlib import Path

test_file = Path("app/tests/test_generate.py")
content = test_file.read_text()

# Pattern 1: Remove license_key from JSON
# Replace: json={"prompt": "...", "license_key": "..."}
# With: headers={"X-License-Key": "lic_test123"}, json={"prompt": "..."}

# Pattern 2: json={...}  -> headers={...}, json={...}
# Step 1: Find all client.post calls with json parameter
def replace_request(match):
    indent = match.group(1)
    json_content = match.group(2)
    
    # Remove license_key from JSON if present
    json_content = re.sub(r',?\s*"license_key":\s*"[^"]*"', '', json_content)
    json_content = json_content.strip().rstrip(',')
    
    # Add headers before json
    return f'{indent}"/v1/generate",\n{indent}headers={{"X-License-Key": "lic_test123"}},\n{indent}json={json_content},'

# Replace all client.post calls
content = re.sub(
    r'(\s+)"/v1/generate",\s+json=({[^}]+}),',
    replace_request,
    content
)

# Write back
test_file.write_text(content)
print("Updated test_generate.py")
