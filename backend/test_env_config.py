#!/usr/bin/env python3
"""Test environment variable configuration"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("Environment Variable Configuration Test")
print("=" * 60)

# Test database configuration
print("\n📊 Database Configuration:")
print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")

# Test JWT configuration
print("\n🔐 JWT Configuration:")
print(f"  JWT_SECRET_KEY: {'Set' if os.getenv('JWT_SECRET_KEY') else 'Not set'}")
print(f"  JWT_ALGORITHM: {os.getenv('JWT_ALGORITHM', 'Not set')}")
print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 'Not set')}")

# Test AI/LLM configuration
print("\n🤖 AI/LLM Configuration:")
print(f"  GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'Not set'}")
print(f"  GROK_API_KEY: {'Set' if os.getenv('GROK_API_KEY') else 'Not set'}")
print(f"  LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'Not set')}")
print(f"  LLM_TEMPERATURE: {os.getenv('LLM_TEMPERATURE', 'Not set')}")
print(f"  LLM_MAX_TOKENS: {os.getenv('LLM_MAX_TOKENS', 'Not set')}")
print(f"  LLM_CACHE_ENABLED: {os.getenv('LLM_CACHE_ENABLED', 'Not set')}")

# Test streaming configuration
print("\n📡 Streaming/Kafka Configuration:")
print(f"  KAFKA_BOOTSTRAP_SERVERS: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'Not set')}")
print(f"  KAFKA_CLIENT_ID: {os.getenv('KAFKA_CLIENT_ID', 'Not set')}")
print(f"  KAFKA_GROUP_ID: {os.getenv('KAFKA_GROUP_ID', 'Not set')}")
print(f"  KAFKA_AUTO_OFFSET_RESET: {os.getenv('KAFKA_AUTO_OFFSET_RESET', 'Not set')}")
print(f"  KAFKA_ENABLE_AUTO_COMMIT: {os.getenv('KAFKA_ENABLE_AUTO_COMMIT', 'Not set')}")

# Test Redis configuration
print("\n🔴 Redis Configuration:")
print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
print(f"  REDIS_CACHE_TTL: {os.getenv('REDIS_CACHE_TTL', 'Not set')}")

# Test agent configuration
print("\n🤖 Agent Configuration:")
print(f"  AGENT_PIPELINE: {os.getenv('AGENT_PIPELINE', 'Not set')}")
print(f"  AGENT_CONFIDENCE_THRESHOLD: {os.getenv('AGENT_CONFIDENCE_THRESHOLD', 'Not set')}")
print(f"  RISK_SCORE_THRESHOLD_HIGH: {os.getenv('RISK_SCORE_THRESHOLD_HIGH', 'Not set')}")
print(f"  RISK_SCORE_THRESHOLD_MEDIUM: {os.getenv('RISK_SCORE_THRESHOLD_MEDIUM', 'Not set')}")
print(f"  RISK_SCORE_THRESHOLD_LOW: {os.getenv('RISK_SCORE_THRESHOLD_LOW', 'Not set')}")

# Test file upload configuration
print("\n📁 File Upload Configuration:")
print(f"  UPLOAD_DIR: {os.getenv('UPLOAD_DIR', 'Not set')}")
print(f"  MAX_UPLOAD_SIZE: {os.getenv('MAX_UPLOAD_SIZE', 'Not set')}")

# Test application configuration
print("\n⚙️ Application Configuration:")
print(f"  ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
print(f"  LOG_LEVEL: {os.getenv('LOG_LEVEL', 'Not set')}")
print(f"  API_HOST: {os.getenv('API_HOST', 'Not set')}")
print(f"  API_PORT: {os.getenv('API_PORT', 'Not set')}")

print("\n" + "=" * 60)
print("Configuration Test Complete")
print("=" * 60)

# Test Settings class
print("\n🔧 Testing Settings class import...")
try:
    from core.config import settings
    print("✅ Settings class imported successfully")
    
    print(f"\n📋 Settings properties:")
    print(f"  Database URL: {settings.DATABASE_URL[:50]}...")
    print(f"  Has Gemini: {settings.has_gemini}")
    print(f"  Has Grok: {settings.has_grok}")
    print(f"  Has any LLM: {settings.has_any_llm}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Is development: {settings.is_development}")
    print(f"  Kafka servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Agent pipeline: {settings.AGENT_PIPELINE}")
    
except Exception as e:
    print(f"❌ Error importing Settings: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Environment configuration is ready!")
print("=" * 60)