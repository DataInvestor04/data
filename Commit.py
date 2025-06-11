import os
import git
from datetime import datetime

def commit_to_github(file_path):
    try:
        # Detailed path configuration
        repo_path = os.path.expanduser("~/OneDrive/Desktop/52WH-final/data")
        
        # Print debugging information
        print(f"Repository Path: {repo_path}")
        print(f"File to Commit: {file_path}")
        
        # Check if the repository path exists
        if not os.path.exists(repo_path):
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        # Initialize the repo
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            print("Not a git repository. Initializing...")
            repo = git.Repo.init(repo_path)
        
        # Change working directory to repo path
        os.chdir(repo_path)
        
        # Configure git user (if not already configured)
        try:
            repo.git.config('user.name', 'DataInvestor04')
            repo.git.config('user.email', 'thegeniusof.info@gmail.com')
        except Exception as config_error:
            print(f"Failed to set git config: {config_error}")
         
        # Add the file
        try:
            repo.git.add(file_path)
        except Exception as add_error:
            print(f"Failed to add file: {add_error}")
            raise
        
        # Commit
        try:
            commit_message = f"Update financial metrics: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            repo.git.commit('-m', commit_message)
        except git.exc.GitCommandError as commit_error:
            print(f"Commit failed: {commit_error}")
            # Check if there are any changes to commit
            if "nothing to commit" in str(commit_error):
                print("No changes to commit.")
                return
            raise
        
        # Push to remote
        try:
            # Try to get the origin remote, create if not exists
            try:
                origin = repo.remote('origin')
            except ValueError:
                origin = repo.create_remote('origin', 'https://github.com/DataInvestor04/52WH-final.git')
            
            # Ensure we're pushing the correct branch
            repo.git.branch('-M', 'main')
            
            # Push with verbose output
            origin.push(refspec='main:main', verbose=True)
            print("Successfully pushed to GitHub")
        
        except Exception as push_error:
            print(f"Push failed: {push_error}")
            # Additional diagnostics
            print("Checking remote configuration...")
            for remote in repo.remotes:
                print(f"Remote: {remote.name}")
                print(f"URL: {remote.url}")
            raise
    
    except Exception as e:
        print(f"Comprehensive GitHub commit failed: {e}")
        # Print system and git diagnostics
        print("\nDiagnostic Information:")
        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Repository Path: {repo_path}")
        print(f"File Path: {file_path}")
        
        # Additional system checks
        import sys
        print(f"Python Version: {sys.version}")
        
        # Git version check
        import subprocess
        try:
            git_version = subprocess.check_output(['git', '--version']).decode('utf-8').strip()
            print(f"Git Version: {git_version}")
        except Exception as version_error:
            print(f"Could not retrieve Git version: {version_error}")

# file_to_commit = "financial_metrics.csv"
# commit_to_github(file_to_commit)