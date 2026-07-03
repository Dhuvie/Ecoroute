"""Fix the broken Plot data props in frontend pages - take 2."""
from pathlib import Path
import re

pages_dir = Path("/home/z/my-project/ecoroute/frontend/src/pages")

for page in ["Dashboard.tsx", "ModelInsights.tsx", "Analytics.tsx"]:
    p = pages_dir / page
    text = p.read_text()
    # Remove the stray inner { line that appears after data={[{
    # Pattern: "data={[{\n              {\n"  -> "data={[\n              {\n"
    text = text.replace("data={[{\n              {\n", "data={[\n              {\n")
    # Replace "]} as any\n" - need to ensure the closing is right.
    # Currently after fix: "              },\n            ]} as any\n"
    # We want: "              },\n            ]} as any}\n"
    text = text.replace("]} as any\n", "]} as any}\n")
    p.write_text(text)
    print(f"Fixed {page}")

print("Done")
