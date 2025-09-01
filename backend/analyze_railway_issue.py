#!/usr/bin/env python3
"""
Analyze why Railway isn't picking up our code changes.
This helps identify the root cause of deployment issues.
"""

import json
import os

def analyze_docker_config():
    """Analyze Docker configuration for issues."""
    print("\n" + "="*60)
    print("DOCKER CONFIGURATION ANALYSIS")
    print("="*60)
    
    # Check Dockerfile.railway
    dockerfile_path = "../Dockerfile.railway"
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        print("\n📋 Dockerfile.railway Analysis:")
        
        # Check for cache bust placement
        lines = content.split('\n')
        pip_line = -1
        copy_line = -1
        cache_line = -1
        
        for i, line in enumerate(lines):
            if 'pip install' in line and 'requirements' in line:
                pip_line = i
            if 'COPY backend/' in line:
                copy_line = i
            if 'CACHEBUST' in line or 'CACHE_BUST' in line:
                cache_line = i
        
        print(f"   • pip install at line: {pip_line + 1}")
        print(f"   • CACHEBUST at line: {cache_line + 1}")
        print(f"   • COPY backend at line: {copy_line + 1}")
        
        if pip_line < cache_line < copy_line:
            print("   ✅ Cache bust is correctly placed between pip and COPY")
        else:
            print("   ❌ Cache bust placement is WRONG!")
            print("   → Must be: pip install → CACHEBUST → COPY backend")
        
        # Check if ARG is used
        if 'ARG CACHEBUST' in content:
            print("   ✅ Using ARG for build-time variable")
        else:
            print("   ❌ Not using ARG - Railway can't pass buildArgs!")
    
    # Check railway.json
    railway_path = "../railway.json"
    if os.path.exists(railway_path):
        with open(railway_path, 'r') as f:
            railway_config = json.load(f)
        
        print("\n📋 railway.json Analysis:")
        
        # Check dockerfile path
        dockerfile = railway_config.get('build', {}).get('dockerfilePath', '')
        print(f"   • Dockerfile: {dockerfile}")
        if dockerfile == "Dockerfile.railway":
            print("   ✅ Using correct Dockerfile.railway")
        else:
            print("   ❌ Wrong Dockerfile specified!")
        
        # Check buildArgs
        build_args = railway_config.get('build', {}).get('buildArgs', {})
        if build_args:
            print(f"   • BuildArgs: {build_args}")
            print("   ✅ BuildArgs configured")
        else:
            print("   ❌ No buildArgs - cache bust won't work!")

def identify_root_cause():
    """Identify the most likely root cause."""
    print("\n" + "="*60)
    print("ROOT CAUSE ANALYSIS")
    print("="*60)
    
    print("\n🔍 HYPOTHESIS 1: Railway Build Cache")
    print("Railway might be caching the entire Docker build, not just layers.")
    print("Evidence: Changes to CACHEBUST don't trigger rebuild")
    print("Solution: Force rebuild in Railway dashboard or change builder")
    
    print("\n🔍 HYPOTHESIS 2: Railway Ignoring BuildArgs")
    print("Railway might not support buildArgs in railway.json")
    print("Evidence: CACHEBUST value doesn't appear in build logs")
    print("Solution: Use ENV directly instead of ARG/buildArgs")
    
    print("\n🔍 HYPOTHESIS 3: Wrong Dockerfile")
    print("Railway might be using a different Dockerfile")
    print("Evidence: Changes don't appear in deployment")
    print("Solution: Verify in Railway dashboard which file is used")
    
    print("\n🔍 HYPOTHESIS 4: Git Sync Issue")
    print("Railway might not have pulled latest changes")
    print("Evidence: Old version still showing")
    print("Solution: Check Railway dashboard for last commit hash")

def suggest_immediate_fix():
    """Suggest an immediate fix that should work."""
    print("\n" + "="*60)
    print("IMMEDIATE FIX RECOMMENDATION")
    print("="*60)
    
    print("\n🚀 NUCLEAR OPTION - Force Complete Rebuild:")
    print("\n1. Create a new Dockerfile.railway.v2 with this content:")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY backend/requirements.prod.txt backend/requirements.prod.txt
RUN pip install --no-cache-dir -r backend/requirements.prod.txt
RUN pip install --no-cache-dir google-ads==24.1.0

# FORCE REBUILD - Change this timestamp for each deployment
ENV REBUILD_TIME="2025-01-09-14:00"
RUN echo "Rebuild triggered at: ${REBUILD_TIME}"

# Copy application code
COPY backend/ backend/

WORKDIR /app/backend
RUN chmod +x start.sh

EXPOSE 8000
CMD ["./start.sh"]'''
    
    print(dockerfile_content)
    
    print("\n2. Update railway.json to use the new file:")
    print('''   "dockerfilePath": "Dockerfile.railway.v2"''')
    
    print("\n3. Commit and push")
    print("\nThis forces Railway to use a completely new Dockerfile,")
    print("bypassing any caching issues.")

def check_alternative_solution():
    """Check if we should use an alternative approach."""
    print("\n" + "="*60)
    print("ALTERNATIVE SOLUTION")
    print("="*60)
    
    print("\n💡 USE NIXPACKS INSTEAD OF DOCKERFILE:")
    print("\nRailway's default builder (Nixpacks) might work better:")
    print("\n1. Delete railway.json temporarily")
    print("2. Let Railway auto-detect and build with Nixpacks")
    print("3. Nixpacks handles Python projects well")
    print("\nOR")
    print("\n💡 USE HEROKU BUILDPACK:")
    print("\n1. Add a Procfile:")
    print("   web: cd backend && ./start.sh")
    print("2. Remove railway.json")
    print("3. Railway will use buildpack")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAILWAY DEPLOYMENT ISSUE ANALYZER")
    print("="*60)
    
    analyze_docker_config()
    identify_root_cause()
    suggest_immediate_fix()
    check_alternative_solution()
    
    print("\n" + "="*60)
    print("RECOMMENDED ACTION:")
    print("="*60)
    print("\n1. First, check Railway dashboard for:")
    print("   • Build logs - look for 'Cache bust' message")
    print("   • Deployment tab - verify commit hash matches")
    print("   • Settings - check if Dockerfile.railway is selected")
    print("\n2. If build isn't triggering, try the NUCLEAR OPTION above")
    print("\n3. As last resort, switch to Nixpacks")
    print("="*60)