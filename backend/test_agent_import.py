#!/usr/bin/env python3
"""Test agent imports"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agents.agent_orchestrator import agent_orchestrator
    print('✅ Agent orchestrator imported successfully')
    
    agents = agent_orchestrator.get_available_agents()
    print(f'✅ Found {len(agents)} agents')
    
    for agent in agents:
        print(f'  - {agent.get("name")}: {agent.get("description", "No description")}')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()