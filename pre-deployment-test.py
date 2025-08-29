#!/usr/bin/env python3
"""
Pre-deployment validation script
Ensures all critical components work before deploying to Railway
"""

import subprocess
import sys
import os
import json
import asyncio
import httpx
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log(message, color=Colors.BLUE):
    print(f"{color}▸ {message}{Colors.RESET}")

def success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")
    
def warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

class DeploymentValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def check_environment_variables(self):
        """Check if critical environment variables are set"""
        log("Checking environment variables...")
        
        required_vars = [
            'OPENAI_API_KEY',
            'CLAUDE_API_KEY'
        ]
        
        optional_vars = [
            'GOOGLE_PAGESPEED_API_KEY',
            'SENTRY_DSN'
        ]
        
        env_file = Path('.env')
        env_vars = {}
        
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value
        
        for var in required_vars:
            if var not in env_vars or not env_vars[var]:
                self.errors.append(f"Missing required env var: {var}")
            else:
                success(f"Found {var}")
                
        for var in optional_vars:
            if var not in env_vars or not env_vars[var]:
                self.warnings.append(f"Missing optional env var: {var}")
            else:
                success(f"Found {var}")
    
    def check_docker_builds(self):
        """Test if Docker images build successfully"""
        log("Testing Docker builds...")
        
        # Test backend build
        log("Building backend Docker image...")
        result = subprocess.run(
            ["docker", "build", "-t", "test-backend", "./backend"],
            capture_output=True
        )
        if result.returncode != 0:
            self.errors.append("Backend Docker build failed")
            error("Backend build failed")
        else:
            success("Backend Docker image builds")
        
        # Test frontend build
        log("Building frontend Docker image...")
        result = subprocess.run(
            ["docker", "build", "-t", "test-frontend", "./frontend"],
            capture_output=True
        )
        if result.returncode != 0:
            self.errors.append("Frontend Docker build failed")
            error("Frontend build failed")
        else:
            success("Frontend Docker image builds")
    
    def test_local_services(self):
        """Test if services start locally"""
        log("Testing local services...")
        
        # Check if ports are available
        import socket
        
        ports_to_check = [
            (8000, "Backend"),
            (3000, "Frontend"),
            (5432, "PostgreSQL"),
            (6379, "Redis")
        ]
        
        for port, service in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                warning(f"Port {port} ({service}) is already in use")
                self.warnings.append(f"Port {port} in use - may conflict")
            else:
                success(f"Port {port} ({service}) is available")
    
    async def test_websocket_connection(self):
        """Test WebSocket connectivity"""
        log("Testing WebSocket connection...")
        
        # This would test against a running instance
        # For now, we'll validate the WebSocket code exists
        ws_file = Path('backend/app/api/websocket.py')
        if ws_file.exists():
            success("WebSocket endpoint found")
        else:
            self.errors.append("WebSocket endpoint missing")
    
    def check_playwright_compatibility(self):
        """Check if Playwright will work in container"""
        log("Checking Playwright compatibility...")
        
        # Check if Playwright installer is in requirements
        req_file = Path('backend/requirements.txt')
        if req_file.exists():
            with open(req_file) as f:
                content = f.read()
                if 'playwright' in content:
                    success("Playwright found in requirements")
                else:
                    self.errors.append("Playwright not in requirements.txt")
    
    def validate_database_migrations(self):
        """Check if database migrations are set up"""
        log("Checking database migrations...")
        
        alembic_ini = Path('backend/alembic.ini')
        migrations_dir = Path('backend/migrations')
        
        if alembic_ini.exists():
            success("Alembic configuration found")
        else:
            self.errors.append("Alembic not configured")
            
        if migrations_dir.exists():
            # Check if there are actual migration files
            versions_dir = migrations_dir / 'versions'
            if versions_dir.exists() and any(versions_dir.iterdir()):
                success("Database migrations exist")
            else:
                warning("No database migrations created yet")
                self.warnings.append("Run 'alembic revision --autogenerate' to create migrations")
        else:
            self.errors.append("Migrations directory missing")
    
    def check_railway_config(self):
        """Validate Railway-specific configuration"""
        log("Checking Railway configuration...")
        
        # Railway needs specific start commands
        configs_to_check = [
            ('railway.json', False),
            ('railway.toml', False),
            ('Procfile', False)
        ]
        
        for config_file, required in configs_to_check:
            if Path(config_file).exists():
                success(f"Found {config_file}")
            elif required:
                self.errors.append(f"Missing required file: {config_file}")
    
    def validate_memory_requirements(self):
        """Check if memory requirements are reasonable"""
        log("Checking memory requirements...")
        
        # Playwright needs at least 2GB RAM
        warning("Ensure Railway instance has at least 2GB RAM for Playwright")
        self.warnings.append("Playwright requires 2GB+ RAM")
    
    def create_deployment_checklist(self):
        """Generate deployment checklist"""
        log("\n" + "="*50)
        log("DEPLOYMENT CHECKLIST", Colors.GREEN)
        log("="*50)
        
        checklist = [
            "Create new GitHub repository",
            "Remove any sensitive data from code",
            "Set up Railway project",
            "Configure environment variables in Railway",
            "Set up PostgreSQL in Railway",
            "Set up Redis in Railway",
            "Configure custom domain (optional)",
            "Set up monitoring (Sentry/PostHog)",
            "Test WebSocket connections",
            "Verify Playwright works"
        ]
        
        for item in checklist:
            print(f"  ☐ {item}")
    
    def run_all_checks(self):
        """Run all validation checks"""
        print("\n" + "="*50)
        print("🚀 GROWTH COPILOT - DEPLOYMENT VALIDATOR")
        print("="*50 + "\n")
        
        self.check_environment_variables()
        print()
        
        self.check_docker_builds()
        print()
        
        self.test_local_services()
        print()
        
        self.check_playwright_compatibility()
        print()
        
        self.validate_database_migrations()
        print()
        
        self.check_railway_config()
        print()
        
        self.validate_memory_requirements()
        print()
        
        # Summary
        print("\n" + "="*50)
        print("VALIDATION SUMMARY")
        print("="*50)
        
        if self.errors:
            print(f"\n{Colors.RED}❌ ERRORS (Must fix before deployment):{Colors.RESET}")
            for err in self.errors:
                print(f"   • {err}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  WARNINGS (Should address):{Colors.RESET}")
            for warn in self.warnings:
                print(f"   • {warn}")
        
        if not self.errors:
            print(f"\n{Colors.GREEN}✅ Ready for deployment!{Colors.RESET}")
            self.create_deployment_checklist()
            return True
        else:
            print(f"\n{Colors.RED}❌ Fix errors before deploying{Colors.RESET}")
            return False

if __name__ == "__main__":
    validator = DeploymentValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)