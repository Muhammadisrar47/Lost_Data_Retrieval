"""
Lost Data Retrieval Tool
A utility to scan, locate, and recover lost or deleted files
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict, Tuple

class LostDataRetrieval:
    """Main class for data recovery operations"""
    
    def __init__(self):
        self.recovered_files = []
        self.scanned_locations = []
        self.recovery_log = []
        
    def print_header(self):
        """Print application header"""
        print("\n" + "="*60)
        print("   LOST DATA RETRIEVAL TOOL")
        print("   File Recovery & Data Retrieval Utility")
        print("="*60 + "\n")
    
    def scan_recycle_bin(self) -> List[Dict]:
        """Scan Windows Recycle Bin for deleted files"""
        print("\n[*] Scanning Recycle Bin...")
        recovered = []
        
        try:
            # Windows Recycle Bin paths
            recycle_paths = [
                os.path.expandvars(r'%USERPROFILE%\$Recycle.Bin'),
                os.path.expandvars(r'C:\$Recycle.Bin'),
            ]
            
            for recycle_path in recycle_paths:
                if os.path.exists(recycle_path):
                    for root, dirs, files in os.walk(recycle_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                stat_info = os.stat(file_path)
                                recovered.append({
                                    'name': file,
                                    'path': file_path,
                                    'size': stat_info.st_size,
                                    'modified': datetime.fromtimestamp(stat_info.st_mtime),
                                    'type': 'Recycle Bin'
                                })
                            except Exception as e:
                                pass
            
            print(f"    [+] Found {len(recovered)} items in Recycle Bin")
            return recovered
            
        except Exception as e:
            print(f"    [-] Error scanning Recycle Bin: {e}")
            return []
    
    def scan_temporary_files(self) -> List[Dict]:
        """Scan for temporary and backup files"""
        print("\n[*] Scanning for temporary and backup files...")
        recovered = []
        
        temp_paths = [
            os.path.expandvars(r'%TEMP%'),
            os.path.expandvars(r'%APPDATA%\Local\Temp'),
            os.path.expandvars(r'%USERPROFILE%\AppData\Local\Temp'),
            os.path.expandvars(r'C:\Windows\Temp'),
        ]
        
        # File extensions to search for
        extensions = ['.tmp', '.bak', '.old', '.backup', '.temp', '.~']
        
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for root, dirs, files in os.walk(temp_path):
                        for file in files:
                            if any(file.endswith(ext) for ext in extensions):
                                file_path = os.path.join(root, file)
                                try:
                                    stat_info = os.stat(file_path)
                                    recovered.append({
                                        'name': file,
                                        'path': file_path,
                                        'size': stat_info.st_size,
                                        'modified': datetime.fromtimestamp(stat_info.st_mtime),
                                        'type': 'Temporary File'
                                    })
                                except:
                                    pass
                except PermissionError:
                    print(f"    [!] Permission denied: {temp_path}")
        
        print(f"    [+] Found {len(recovered)} temporary/backup files")
        return recovered
    
    def scan_directory(self, path: str) -> List[Dict]:
        """Scan a specific directory for recoverable files"""
        print(f"\n[*] Scanning directory: {path}")
        recovered = []
        
        if not os.path.exists(path):
            print(f"    [-] Path does not exist: {path}")
            return []
        
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat_info = os.stat(file_path)
                        recovered.append({
                            'name': file,
                            'path': file_path,
                            'size': stat_info.st_size,
                            'modified': datetime.fromtimestamp(stat_info.st_mtime),
                            'type': 'Directory Scan'
                        })
                    except:
                        pass
            
            print(f"    [+] Found {len(recovered)} files")
            self.scanned_locations.append(path)
            return recovered
            
        except Exception as e:
            print(f"    [-] Error scanning directory: {e}")
            return []
    
    def search_by_file_type(self, search_path: str, file_extension: str) -> List[Dict]:
        """Search for specific file types"""
        print(f"\n[*] Searching for .{file_extension} files in {search_path}...")
        recovered = []
        
        if not os.path.exists(search_path):
            print(f"    [-] Path does not exist: {search_path}")
            return []
        
        try:
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith(f'.{file_extension}'):
                        file_path = os.path.join(root, file)
                        try:
                            stat_info = os.stat(file_path)
                            recovered.append({
                                'name': file,
                                'path': file_path,
                                'size': stat_info.st_size,
                                'modified': datetime.fromtimestamp(stat_info.st_mtime),
                                'type': f'{file_extension.upper()} File'
                            })
                        except:
                            pass
            
            print(f"    [+] Found {len(recovered)} .{file_extension} files")
            return recovered
            
        except Exception as e:
            print(f"    [-] Error searching: {e}")
            return []
    
    def display_results(self, files: List[Dict]):
        """Display search results in formatted table"""
        if not files:
            print("\n    No files found.")
            return
        
        print("\n" + "-"*100)
        print(f"{'#':<4} {'File Name':<30} {'Size (KB)':<12} {'Type':<20} {'Modified':<20}")
        print("-"*100)
        
        for i, file in enumerate(files, 1):
            size_kb = file['size'] / 1024
            modified = file['modified'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i:<4} {file['name']:<30} {size_kb:<12.2f} {file['type']:<20} {modified:<20}")
        
        print("-"*100)
        print(f"Total files found: {len(files)}")
    
    def recover_files(self, files: List[Dict], destination: str) -> Tuple[int, int]:
        """Recover selected files to destination"""
        if not files:
            print("\n    No files to recover.")
            return 0, 0
        
        print(f"\n[*] Starting recovery to: {destination}")
        
        if not os.path.exists(destination):
            try:
                os.makedirs(destination)
                print(f"    [+] Created destination directory")
            except Exception as e:
                print(f"    [-] Failed to create destination: {e}")
                return 0, 0
        
        successful = 0
        failed = 0
        
        for i, file in enumerate(files, 1):
            try:
                filename = os.path.basename(file['path'])
                dest_file = os.path.join(destination, filename)
                
                # Handle duplicate filenames
                if os.path.exists(dest_file):
                    name, ext = os.path.splitext(filename)
                    dest_file = os.path.join(destination, f"{name}_recovered{ext}")
                
                shutil.copy2(file['path'], dest_file)
                successful += 1
                print(f"    [{i}] ✓ Recovered: {filename}")
                self.recovery_log.append({
                    'original': file['path'],
                    'destination': dest_file,
                    'status': 'SUCCESS',
                    'timestamp': datetime.now()
                })
            except Exception as e:
                failed += 1
                print(f"    [{i}] ✗ Failed: {os.path.basename(file['path'])} - {e}")
                self.recovery_log.append({
                    'original': file['path'],
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        print(f"\n    [+] Recovery complete: {successful} successful, {failed} failed")
        return successful, failed
    
    def save_recovery_log(self, filename: str = "recovery_log.json"):
        """Save recovery log to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.recovery_log, f, indent=4, default=str)
            print(f"\n[+] Recovery log saved to: {filename}")
        except Exception as e:
            print(f"\n[-] Failed to save recovery log: {e}")
    
    def interactive_menu(self):
        """Interactive menu for recovery operations"""
        while True:
            print("\n" + "="*60)
            print("RECOVERY OPTIONS")
            print("="*60)
            print("1. Scan Recycle Bin")
            print("2. Scan Temporary Files")
            print("3. Scan Custom Directory")
            print("4. Search by File Type")
            print("5. Display Results")
            print("6. Recover Selected Files")
            print("7. Clear Results")
            print("8. Exit")
            print("="*60)
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                files = self.scan_recycle_bin()
                self.recovered_files.extend(files)
            
            elif choice == '2':
                files = self.scan_temporary_files()
                self.recovered_files.extend(files)
            
            elif choice == '3':
                path = input("\nEnter directory path to scan: ").strip().strip('"')
                if path:
                    files = self.scan_directory(path)
                    self.recovered_files.extend(files)
            
            elif choice == '4':
                file_type = input("\nEnter file extension (without dot, e.g., 'txt', 'doc'): ").strip().lower()
                search_path = input("Enter search path (or press Enter for C:\): ").strip().strip('"') or "C:\\"
                if file_type:
                    files = self.search_by_file_type(search_path, file_type)
                    self.recovered_files.extend(files)
            
            elif choice == '5':
                self.display_results(self.recovered_files)
            
            elif choice == '6':
                if not self.recovered_files:
                    print("\n    [-] No files to recover. Please scan first.")
                else:
                    self.display_results(self.recovered_files)
                    dest = input("\nEnter destination folder for recovery: ").strip().strip('"')
                    if dest:
                        self.recover_files(self.recovered_files, dest)
                        self.save_recovery_log()
            
            elif choice == '7':
                self.recovered_files = []
                print("\n    [+] Results cleared")
            
            elif choice == '8':
                print("\n[*] Exiting Lost Data Retrieval Tool")
                print("[*] Thank you for using this tool!\n")
                break
            
            else:
                print("\n    [-] Invalid choice. Please try again.")

def main():
    """Main entry point"""
    tool = LostDataRetrieval()
    tool.print_header()
    
    print("Welcome to Lost Data Retrieval Tool")
    print("\nThis utility helps you scan and recover lost or deleted files.")
    print("You can recover files from:")
    print("  • Recycle Bin")
    print("  • Temporary directories")
    print("  • Custom directories")
    print("  • Specific file types")
    
    try:
        tool.interactive_menu()
    except KeyboardInterrupt:
        print("\n\n[!] Operation interrupted by user")
    except Exception as e:
        print(f"\n[-] Unexpected error: {e}")

if __name__ == "__main__":
    main()
