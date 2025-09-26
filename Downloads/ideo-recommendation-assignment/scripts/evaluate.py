#!/usr/bin/env python3
"""
Evaluation script for Video Recommendation Engine.
Checks the evaluation checklist and validates all components.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import httpx
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

class EvaluationChecker:
    """Comprehensive evaluation checker for the Video Recommendation Engine."""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.results = {}
        self.total_checks = 0
        self.passed_checks = 0
        
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{title.center(60)}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def print_check(self, check_name: str, status: bool, details: str = ""):
        """Print check result with color coding."""
        self.total_checks += 1
        if status:
            self.passed_checks += 1
            status_text = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}"
        else:
            status_text = f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
        
        print(f"{status_text} {check_name}")
        if details:
            print(f"    {Fore.YELLOW}{details}{Style.RESET_ALL}")
        
        self.results[check_name] = {"status": status, "details": details}
    
    def check_file_exists(self, file_path: str, description: str) -> bool:
        """Check if a file exists."""
        exists = Path(file_path).exists()
        self.print_check(
            f"File exists: {description}",
            exists,
            f"Path: {file_path}" if not exists else ""
        )
        return exists
    
    def check_directory_exists(self, dir_path: str, description: str) -> bool:
        """Check if a directory exists."""
        exists = Path(dir_path).is_dir()
        self.print_check(
            f"Directory exists: {description}",
            exists,
            f"Path: {dir_path}" if not exists else ""
        )
        return exists
    
    def check_api_endpoint(self, endpoint: str, expected_status: int = 200) -> bool:
        """Check if an API endpoint is accessible."""
        try:
            response = httpx.get(f"{self.base_url}{endpoint}", timeout=10.0)
            status_ok = response.status_code == expected_status
            self.print_check(
                f"API endpoint: {endpoint}",
                status_ok,
                f"Status: {response.status_code} (expected: {expected_status})"
            )
            return status_ok
        except httpx.RequestError as e:
            self.print_check(
                f"API endpoint: {endpoint}",
                False,
                f"Connection error: {str(e)}"
            )
            return False
    
    def check_postman_collection(self) -> bool:
        """Check Postman collection file."""
        collection_path = "video-recommendation.postman_collection.json"
        if not self.check_file_exists(collection_path, "Postman collection"):
            return False
        
        try:
            with open(collection_path, 'r') as f:
                collection = json.load(f)
            
            # Check required endpoints
            required_endpoints = [
                "Get Personalized Feed",
                "Get Category Feed", 
                "Health Check",
                "External API - Get Viewed Posts"
            ]
            
            endpoints_found = []
            for item in collection.get("item", []):
                endpoints_found.append(item.get("name", ""))
            
            missing_endpoints = set(required_endpoints) - set(endpoints_found)
            
            self.print_check(
                "Postman collection endpoints",
                len(missing_endpoints) == 0,
                f"Missing: {list(missing_endpoints)}" if missing_endpoints else "All required endpoints present"
            )
            
            return len(missing_endpoints) == 0
            
        except json.JSONDecodeError:
            self.print_check(
                "Postman collection JSON",
                False,
                "Invalid JSON format"
            )
            return False
    
    def check_database_migrations(self) -> bool:
        """Check if database migrations can run."""
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            migration_success = result.returncode == 0
            self.print_check(
                "Database migrations",
                migration_success,
                result.stderr if not migration_success else "Migrations completed successfully"
            )
            return migration_success
            
        except subprocess.TimeoutExpired:
            self.print_check(
                "Database migrations",
                False,
                "Migration timeout"
            )
            return False
        except FileNotFoundError:
            self.print_check(
                "Database migrations",
                False,
                "Alembic not found. Install dependencies first."
            )
            return False
    
    def check_documentation(self) -> bool:
        """Check documentation completeness."""
        docs_path = "docs/recommendation_system.md"
        if not self.check_file_exists(docs_path, "Main documentation"):
            return False
        
        try:
            with open(docs_path, 'r') as f:
                content = f.read()
            
            required_sections = [
                "Project Overview",
                "System Architecture", 
                "API Endpoints",
                "Setup and Running Instructions",
                "Edge Cases and Error Handling",
                "Future Neural Network Implementation"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            self.print_check(
                "Documentation completeness",
                len(missing_sections) == 0,
                f"Missing sections: {missing_sections}" if missing_sections else "All required sections present"
            )
            
            return len(missing_sections) == 0
            
        except Exception as e:
            self.print_check(
                "Documentation readability",
                False,
                f"Error reading documentation: {str(e)}"
            )
            return False
    
    def check_code_quality(self) -> bool:
        """Check code quality and documentation."""
        python_files = [
            "app/main.py",
            "app/services/recommendation.py",
            "app/services/data_collection.py",
            "app/routes/recommendations.py"
        ]
        
        all_files_ok = True
        for file_path in python_files:
            if not self.check_file_exists(file_path, f"Python file: {file_path}"):
                all_files_ok = False
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for docstrings and comments
                has_docstrings = '"""' in content or "'''" in content
                has_comments = '#' in content
                
                self.print_check(
                    f"Code documentation: {file_path}",
                    has_docstrings and has_comments,
                    "Missing docstrings or comments" if not (has_docstrings and has_comments) else "Well documented"
                )
                
            except Exception as e:
                self.print_check(
                    f"Code readability: {file_path}",
                    False,
                    f"Error reading file: {str(e)}"
                )
                all_files_ok = False
        
        return all_files_ok
    
    def check_video_scripts(self) -> bool:
        """Check video submission scripts."""
        scripts = [
            "docs/intro_video_script.txt",
            "docs/technical_demo_script.txt"
        ]
        
        all_scripts_ok = True
        for script_path in scripts:
            if not self.check_file_exists(script_path, f"Video script: {script_path}"):
                all_scripts_ok = False
                continue
            
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Check for required elements
                has_timing = any(word in content.lower() for word in ['duration', 'seconds', 'minutes'])
                has_structure = any(word in content.lower() for word in ['scene', 'step', 'section'])
                
                self.print_check(
                    f"Video script quality: {script_path}",
                    has_timing and has_structure,
                    "Missing timing or structure information" if not (has_timing and has_structure) else "Well structured"
                )
                
            except Exception as e:
                self.print_check(
                    f"Video script readability: {script_path}",
                    False,
                    f"Error reading script: {str(e)}"
                )
                all_scripts_ok = False
        
        return all_scripts_ok
    
    async def check_api_functionality(self) -> bool:
        """Check API functionality with actual requests."""
        endpoints_to_test = [
            ("/health", 200),
            ("/api/v1/health", 200),
            ("/api/v1/feed?username=testuser", 200),
            ("/api/v1/feed/category?username=testuser&project_code=fitness", 200),
            ("/api/v1/neural-network-suggestions", 200)
        ]
        
        all_endpoints_ok = True
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, expected_status in endpoints_to_test:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    status_ok = response.status_code == expected_status
                    
                    self.print_check(
                        f"API functionality: {endpoint}",
                        status_ok,
                        f"Status: {response.status_code} (expected: {expected_status})"
                    )
                    
                    if not status_ok:
                        all_endpoints_ok = False
                        
                except httpx.RequestError as e:
                    self.print_check(
                        f"API functionality: {endpoint}",
                        False,
                        f"Connection error: {str(e)}"
                    )
                    all_endpoints_ok = False
        
        return all_endpoints_ok
    
    def check_error_handling(self) -> bool:
        """Check error handling scenarios."""
        error_scenarios = [
            ("/api/v1/feed?username=", 400),  # Empty username
            ("/api/v1/feed/category?username=test&project_code=", 400),  # Empty project_code
            ("/api/v1/feed?username=test&limit=100", 400),  # Invalid limit
        ]
        
        all_errors_handled = True
        for endpoint, expected_status in error_scenarios:
            try:
                response = httpx.get(f"{self.base_url}{endpoint}", timeout=10.0)
                status_ok = response.status_code == expected_status
                
                self.print_check(
                    f"Error handling: {endpoint}",
                    status_ok,
                    f"Status: {response.status_code} (expected: {expected_status})"
                )
                
                if not status_ok:
                    all_errors_handled = False
                    
            except httpx.RequestError as e:
                self.print_check(
                    f"Error handling: {endpoint}",
                    False,
                    f"Connection error: {str(e)}"
                )
                all_errors_handled = False
        
        return all_errors_handled
    
    def print_summary(self):
        """Print evaluation summary."""
        self.print_header("EVALUATION SUMMARY")
        
        success_rate = (self.passed_checks / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"{Fore.CYAN}Total Checks: {self.total_checks}")
        print(f"{Fore.GREEN}Passed: {self.passed_checks}")
        print(f"{Fore.RED}Failed: {self.total_checks - self.passed_checks}")
        print(f"{Fore.YELLOW}Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")
        
        if success_rate >= 90:
            print(f"\n{Fore.GREEN}🎉 EXCELLENT! Project meets all requirements.{Style.RESET_ALL}")
        elif success_rate >= 80:
            print(f"\n{Fore.YELLOW}⚠️  GOOD! Minor issues to address.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ NEEDS WORK! Significant issues found.{Style.RESET_ALL}")
        
        # Print failed checks
        failed_checks = [name for name, result in self.results.items() if not result["status"]]
        if failed_checks:
            print(f"\n{Fore.RED}Failed Checks:{Style.RESET_ALL}")
            for check in failed_checks:
                print(f"  - {check}")
                if self.results[check]["details"]:
                    print(f"    {Fore.YELLOW}{self.results[check]['details']}{Style.RESET_ALL}")
    
    async def run_evaluation(self):
        """Run complete evaluation."""
        self.print_header("VIDEO RECOMMENDATION ENGINE EVALUATION")
        
        # File structure checks
        self.print_header("FILE STRUCTURE CHECKS")
        self.check_directory_exists("app", "Main application directory")
        self.check_directory_exists("app/services", "Services directory")
        self.check_directory_exists("app/routes", "Routes directory")
        self.check_directory_exists("app/models", "Models directory")
        self.check_directory_exists("docs", "Documentation directory")
        self.check_directory_exists("scripts", "Scripts directory")
        self.check_directory_exists("alembic", "Database migrations directory")
        
        # Core files
        self.print_header("CORE FILES CHECKS")
        self.check_file_exists("app/main.py", "FastAPI main application")
        self.check_file_exists("app/config.py", "Configuration module")
        self.check_file_exists("requirements.txt", "Python dependencies")
        self.check_file_exists("alembic.ini", "Alembic configuration")
        
        # API functionality
        self.print_header("API FUNCTIONALITY CHECKS")
        await self.check_api_functionality()
        
        # Error handling
        self.print_header("ERROR HANDLING CHECKS")
        self.check_error_handling()
        
        # Database migrations
        self.print_header("DATABASE CHECKS")
        self.check_database_migrations()
        
        # Documentation
        self.print_header("DOCUMENTATION CHECKS")
        self.check_documentation()
        self.check_video_scripts()
        
        # Code quality
        self.print_header("CODE QUALITY CHECKS")
        self.check_code_quality()
        
        # Postman collection
        self.print_header("POSTMAN COLLECTION CHECKS")
        self.check_postman_collection()
        
        # Print summary
        self.print_summary()


async def main():
    """Main evaluation function."""
    print(f"{Fore.CYAN}Video Recommendation Engine - Evaluation Script{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Checking project against evaluation checklist...{Style.RESET_ALL}")
    
    checker = EvaluationChecker()
    await checker.run_evaluation()
    
    # Exit with appropriate code
    success_rate = (checker.passed_checks / checker.total_checks) * 100 if checker.total_checks > 0 else 0
    sys.exit(0 if success_rate >= 80 else 1)


if __name__ == "__main__":
    asyncio.run(main())
