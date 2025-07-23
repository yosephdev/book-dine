#!/usr/bin/env python
"""
Comprehensive Heroku deployment diagnostic script
"""
import os
import sys
import subprocess
import json

def run_command(cmd, capture_output=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_heroku_config():
    """Check Heroku configuration"""
    print("🔍 Checking Heroku configuration...")
    
    success, stdout, stderr = run_command("heroku config --app book-dine-c8d9fe1355da --json")
    if success:
        config = json.loads(stdout)
        print("✅ Environment variables:")
        for key, value in config.items():
            if 'SECRET' in key or 'PASSWORD' in key:
                print(f"   {key}: [HIDDEN]")
            else:
                print(f"   {key}: {value}")
    else:
        print(f"❌ Failed to get config: {stderr}")

def check_heroku_logs():
    """Get recent Heroku logs"""
    print("\n🔍 Getting recent Heroku logs...")
    
    success, stdout, stderr = run_command("heroku logs --tail --num 50 --app book-dine-c8d9fe1355da")
    if success:
        print("📋 Recent logs:")
        print(stdout)
    else:
        print(f"❌ Failed to get logs: {stderr}")

def check_django_setup():
    """Check if Django can start locally"""
    print("\n🔍 Testing Django setup locally...")
    
    # Set emergency settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BookDine.settings.emergency'
    
    try:
        import django
        django.setup()
        print("✅ Django imports and setup successful")
        
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'check'])
        print("✅ Django check passed")
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")

def check_requirements():
    """Check if all requirements are satisfied"""
    print("\n🔍 Checking requirements...")
    
    success, stdout, stderr = run_command("pip check")
    if success:
        print("✅ All requirements satisfied")
    else:
        print(f"❌ Requirements issues: {stderr}")

def main():
    print("🚀 BookDine Heroku Diagnostic Tool")
    print("=" * 50)
    
    check_heroku_config()
    check_django_setup()
    check_requirements()
    check_heroku_logs()
    
    print("\n🎯 Next steps:")
    print("1. Fix any Django setup issues shown above")
    print("2. Ensure all required environment variables are set")
    print("3. Deploy with: git push heroku main")
    print("4. Monitor with: heroku logs --tail --app book-dine-c8d9fe1355da")

if __name__ == "__main__":
    main()