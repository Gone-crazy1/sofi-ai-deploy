"""
Git Deployment Helper
===================
This helps commit and push the WhatsApp integration updates
"""

import subprocess
import os

def run_command(command, description):
    """Run a command and show the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_git_status():
    """Check git status"""
    print("📋 Checking Git Status")
    print("=" * 30)
    
    # Check if we're in a git repo
    if not os.path.exists('.git'):
        print("❌ Not a git repository")
        return False
    
    # Show status
    run_command("git status --porcelain", "Checking for changes")
    return True

def commit_and_push():
    """Commit and push changes"""
    print("\n🚀 Deploying WhatsApp Integration")
    print("=" * 40)
    
    # Add all changes
    if not run_command("git add .", "Adding changes"):
        return False
    
    # Commit with descriptive message
    commit_message = "Fix WhatsApp integration API endpoints and SSL issues"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("ℹ️  No changes to commit (already up to date)")
    
    # Push to main branch
    if not run_command("git push origin main", "Pushing to GitHub"):
        return False
    
    print("\n✅ Deployment pushed successfully!")
    return True

def main():
    """Main deployment process"""
    print("🔧 WhatsApp Integration Deployment")
    print("📅 2025-08-02")
    print()
    
    if not check_git_status():
        print("💡 Initialize git first: git init")
        return
    
    print("\n📋 Files being deployed:")
    files = [
        "main.py (WhatsApp routes)",
        "templates/whatsapp_onboarding.html (Better error handling)",
        "utils/whatsapp_account_manager_simple.py (Database integration)",
        "paystack/paystack_dva_api.py (SSL fixes)",
        "utils/whatsapp_gpt_integration.py (GPT integration)"
    ]
    
    for file in files:
        print(f"  ✅ {file}")
    
    print("\n🎯 This deployment will:")
    print("  1. Fix SSL connection issues with Paystack")
    print("  2. Add missing API routes for account creation")
    print("  3. Update database schema compatibility")
    print("  4. Improve error handling in web form")
    
    # Ask for confirmation
    confirm = input("\n🤔 Deploy these changes? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        if commit_and_push():
            print("\n🎉 DEPLOYMENT COMPLETE!")
            print("⏰ Wait 2-3 minutes for auto-deployment")
            print("🧪 Then test:")
            print("   https://pipinstallsofi.com/whatsapp-onboard")
            print("   https://pipinstallsofi.com/api/whatsapp_create_account")
        else:
            print("\n❌ Deployment failed")
    else:
        print("\n⏸️  Deployment cancelled")

if __name__ == "__main__":
    main()
