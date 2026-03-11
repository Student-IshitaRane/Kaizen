#!/usr/bin/env python3
"""
Update all schema files from Pydantic v2 to v1
"""

import os
import re

def update_schema_file(filepath):
    """Update a single schema file from Pydantic v2 to v1"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace from_attributes with orm_mode
    content = content.replace('from_attributes = True', 'orm_mode = True')
    
    # Replace model_validate with from_orm if needed
    content = content.replace('.model_validate(', '.from_orm(')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {filepath}")

def main():
    schemas_dir = "schemas"
    
    if not os.path.exists(schemas_dir):
        print(f"Schemas directory not found: {schemas_dir}")
        return
    
    for filename in os.listdir(schemas_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(schemas_dir, filename)
            update_schema_file(filepath)
    
    print("\nAll schema files updated for Pydantic v1 compatibility")

if __name__ == "__main__":
    main()