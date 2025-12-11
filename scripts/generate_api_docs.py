"""
Generate OpenAPI specification from FastAPI app
Run this to export API docs for MkDocs
"""
import json
from pathlib import Path

# Add parent directory to path to import app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backend.endpoints import app

def generate_openapi_json():
    """Generate OpenAPI JSON file"""
    openapi_schema = app.openapi()
    
    # Save to docs folder
    docs_dir = Path(__file__).parent.parent / "docs" / "backend"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = docs_dir / "openapi.json"
    
    with open(output_file, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"✅ OpenAPI specification generated: {output_file}")
    print(f"📊 Endpoints: {len([path for path in openapi_schema.get('paths', {})])}")
    print(f"📦 Schemas: {len(openapi_schema.get('components', {}).get('schemas', {}))}")
    
    return output_file

if __name__ == "__main__":
    generate_openapi_json()
