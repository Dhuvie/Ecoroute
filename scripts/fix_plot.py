"""Fix the broken Plot data props in frontend pages."""
import re
from pathlib import Path

pages_dir = Path("/home/z/my-project/ecoroute/frontend/src/pages")

for page in ["Dashboard.tsx", "ModelInsights.tsx", "Analytics.tsx"]:
    p = pages_dir / page
    text = p.read_text()
    # Fix pattern: data={[{\n              {\n -> data={[{\n
    text = re.sub(r"data=\[\{\{\s*\n\s*\{\s*\n", "data={[\n              {\n", text)
    # Fix closing: ] as any}  -> ]} as any  (proper format)
    text = re.sub(r"\] as any\}", "]} as any", text)
    p.write_text(text)
    print(f"Fixed {page}")

print("Done")
