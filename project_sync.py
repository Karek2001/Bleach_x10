# project_sync.py - Auto-sync project files to remote PCs
import os
import sys
import time
import json
import hashlib
import socket
import threading
from pathlib import Path
from datetime import datetime
import paramiko
from scp import SCPClient

class ProjectSync:
    def __init__(self):
        # Remote PC configurations
        self.remote_pcs = [
            {
                "name": "RDP#1",
                "server_number": 1,
                "host": "37.27.127.250",  # Replace with actual IP
                "port": 22,
                "username": "fadi",  # Replace with actual username
                "password": "Aa@54109999",  # Replace with actual password
                "project_path": "C:/Users/Administrator/Desktop/Bleach_10x"
            },
            {
                "name": "RDP#2",
                "server_number": 2,
                "host": "37.27.226.185",  # Replace with actual IP
                "port": 22,
                "username": "anas",  # Replace with actual username
                "password": "Aa@5410932",  # Replace with actual password
                "project_path": "C:/Users/Administrator/Desktop/Bleach_10x"
            },
            {
                "name": "RDP#3",
                "server_number": 3,
                "host": "37.27.226.186",  # Replace with actual IP
                "port": 22,
                "username": "karek",  # Replace with actual username
                "password": "AXel21IOWgLaz*)KM_[Yq5-_",  # Replace with actual password
                "project_path": "C:/Users/karek/Desktop/Bleach_10x"
            }
        ]
        
        # Files to exclude from sync
        self.exclude_files = [
            "__pycache__",
            ".pyc",
            ".git",
            ".gitignore",
            ".env",            # Don't sync local credentials
            ".env1",           # Server-specific env (synced separately)
            ".env2",           # Server-specific env (synced separately)
            ".env3",           # Server-specific env (synced separately)
            "device_states",   # Don't sync device states
            "stock_images",    # Don't sync stock images
            "testing"          # Don't sync testing folder
        ]
        
        # Local project path
        self.local_path = Path.cwd()
        
        # File hashes for change detection
        self.file_hashes = {}
        self.load_hashes()
    
    def load_hashes(self):
        """Load stored file hashes"""
        hash_file = self.local_path / ".sync_hashes.json"
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                self.file_hashes = json.load(f)
    
    def save_hashes(self):
        """Save file hashes"""
        hash_file = self.local_path / ".sync_hashes.json"
        with open(hash_file, 'w') as f:
            json.dump(self.file_hashes, f, indent=2)
    
    def get_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def should_exclude(self, filepath):
        """Check if file should be excluded from sync"""
        filepath_str = str(filepath)
        for exclude in self.exclude_files:
            if exclude in filepath_str:
                return True
        return False
    
    def get_all_local_files(self):
        """Get list of all local files (for tracking deletions)"""
        local_files = set()
        
        for root, dirs, files in os.walk(self.local_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if not self.should_exclude(d)]
            
            for file in files:
                filepath = Path(root) / file
                
                # Skip excluded files
                if self.should_exclude(filepath):
                    continue
                
                # Skip non-project files
                if not (filepath.suffix in ['.py', '.json', '.png', '.txt', '.md', '.sh'] or 
                       'templates' in str(filepath)):
                    continue
                
                # Get relative path
                rel_path = filepath.relative_to(self.local_path)
                rel_path_str = str(rel_path).replace('\\', '/')
                local_files.add(rel_path_str)
        
        return local_files
    
    def get_changed_files(self, force=False):
        """Get list of files that have changed"""
        changed_files = []
        
        for root, dirs, files in os.walk(self.local_path):
            # Remove excluded directories from traversal
            dirs[:] = [d for d in dirs if not self.should_exclude(d)]
            
            for file in files:
                filepath = Path(root) / file
                
                # Skip excluded files
                if self.should_exclude(filepath):
                    continue
                
                # Skip non-project files
                if not (filepath.suffix in ['.py', '.json', '.png', '.txt', '.md', '.sh'] or 
                       'templates' in str(filepath)):
                    continue
                
                # Get relative path
                rel_path = filepath.relative_to(self.local_path)
                rel_path_str = str(rel_path).replace('\\', '/')
                
                # Calculate hash
                current_hash = self.get_file_hash(filepath)
                
                # Check if file is new or changed (or force sync all)
                if force or rel_path_str not in self.file_hashes or \
                   self.file_hashes[rel_path_str] != current_hash:
                    changed_files.append((filepath, rel_path_str))
                    self.file_hashes[rel_path_str] = current_hash
        
        return changed_files
    
    def get_deleted_files(self, local_files):
        """Get list of files that exist in hash but not locally (deleted files)"""
        deleted_files = []
        for file_path in self.file_hashes.keys():
            if file_path not in local_files:
                deleted_files.append(file_path)
        return deleted_files
    
    def sync_to_pc(self, pc_config, changed_files, deleted_files=None):
        """Sync changed files and delete removed files on a specific PC"""
        name = pc_config["name"]
        server_number = pc_config.get("server_number")
        print(f"{name}: Connecting...")
        
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect
            ssh.connect(
                hostname=pc_config["host"],
                port=pc_config["port"],
                username=pc_config["username"],
                password=pc_config["password"],
                timeout=10
            )
            
            print(f"{name}: Updating...")
            
            # First, delete removed files on remote
            if deleted_files:
                for rel_path in deleted_files:
                    remote_path = f"{pc_config['project_path']}/{rel_path}"
                    remote_path_win = remote_path.replace('/', '\\')
                    print(f"{name}: Deleting {rel_path}")
                    stdin, stdout, stderr = ssh.exec_command(f'if exist "{remote_path_win}" del /F /Q "{remote_path_win}"')
                    stdout.read()  # Wait for command to complete
            
            # Second, sync changed/new files
            with SCPClient(ssh.get_transport()) as scp:
                for local_file, rel_path in changed_files:
                    remote_path = f"{pc_config['project_path']}/{rel_path}"
                    
                    # Create remote directory if needed (Windows compatible)
                    remote_dir = os.path.dirname(remote_path).replace('/', '\\')
                    stdin, stdout, stderr = ssh.exec_command(f'if not exist "{remote_dir}" mkdir "{remote_dir}"')
                    stdout.read()  # Wait for command to complete
                    
                    # Copy file
                    print(f"{name}: Copying {rel_path}")
                    scp.put(str(local_file), remote_path)
                
                # Third, sync server-specific .env file if it exists
                if server_number:
                    env_file = self.local_path / f".env{server_number}"
                    if env_file.exists():
                        remote_env_path = f"{pc_config['project_path']}/.env"
                        print(f"{name}: Copying .env{server_number} as .env")
                        scp.put(str(env_file), remote_env_path)
            
            ssh.close()
            print(f"{name}: Updated! ✅")
            return True
            
        except socket.timeout:
            print(f"{name}: Connection timeout ❌")
            return False
        except paramiko.AuthenticationException:
            print(f"{name}: Authentication failed ❌")
            return False
        except Exception as e:
            print(f"{name}: Error - {e} ❌")
            return False
    
    def sync_all(self, force=False, mirror=True):
        """Sync to all PCs with mirror mode (includes deletions)"""
        print("=" * 50)
        print(f"Project Sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if force:
            print("🔄 FORCE SYNC - All files will be synced")
        if mirror:
            print("🪞 MIRROR MODE - Deletions will be synced")
        print("=" * 50)
        
        # Get all local files for deletion tracking
        local_files = self.get_all_local_files()
        
        # Get changed files
        changed_files = self.get_changed_files(force=force)
        
        # Get deleted files (exist in hash but not locally)
        deleted_files = self.get_deleted_files(local_files) if mirror else []
        
        # Remove deleted files from hash
        for deleted_file in deleted_files:
            if deleted_file in self.file_hashes:
                del self.file_hashes[deleted_file]
        
        if not changed_files and not deleted_files:
            print("No changes detected")
            return
        
        if changed_files:
            print(f"Found {len(changed_files)} changed file(s):")
            for _, rel_path in changed_files[:10]:  # Show first 10
                print(f"  ➕ {rel_path}")
            if len(changed_files) > 10:
                print(f"  ... and {len(changed_files) - 10} more")
        
        if deleted_files:
            print(f"\nFound {len(deleted_files)} deleted file(s):")
            for rel_path in deleted_files[:10]:  # Show first 10
                print(f"  ❌ {rel_path}")
            if len(deleted_files) > 10:
                print(f"  ... and {len(deleted_files) - 10} more")
        
        print()
        
        # Sync to each PC in parallel
        threads = []
        for pc_config in self.remote_pcs:
            thread = threading.Thread(
                target=self.sync_to_pc,
                args=(pc_config, changed_files, deleted_files)
            )
            thread.start()
            threads.append(thread)
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Save updated hashes
        self.save_hashes()
        print("\nSync complete!")
    
    def watch_and_sync(self, interval=60, mirror=True):
        """Watch for changes and sync periodically"""
        print("Starting auto-sync service...")
        print(f"Watching for changes every {interval} seconds")
        if mirror:
            print("Mirror mode enabled - deletions will be synced")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.sync_all(mirror=mirror)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping auto-sync service...")

def main():
    syncer = ProjectSync()
    
    # Parse arguments
    force = "--force" in sys.argv
    mirror = "--no-mirror" not in sys.argv  # Mirror mode ON by default
    
    # Check if running in watch mode or single sync
    if "--watch" in sys.argv:
        # Auto-sync mode
        interval = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 60
        syncer.watch_and_sync(interval, mirror=mirror)
    else:
        # Single sync
        syncer.sync_all(force=force, mirror=mirror)

if __name__ == "__main__":
    main()