#!/usr/bin/env python3
"""
Update all route files from Pydantic v2 to v1
"""

import os
import re

def update_route_file(filepath):
    """Update a single route file from Pydantic v2 to v1"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace model_validate with from_orm
    content = content.replace('.model_validate(', '.from_orm(')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {filepath}")

def main():
    routes_dir = "routes"
    
    if not os.path.exists(routes_dir):
        print(f"Routes directory not found: {routes_dir}")
        return
    
    for filename in os.listdir(routes_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(routes_dir, filename)
            update_route_file(filepath)
    
    print("\nAll route files updated for Pydantic v1 compatibility")

if __name__ == "__main__":
    main()