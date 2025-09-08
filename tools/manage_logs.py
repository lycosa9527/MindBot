#!/usr/bin/env python3
"""
MindBot Log Management Script
Provides utilities for managing log files
"""

import os
import glob
import argparse
import gzip
from datetime import datetime, timedelta
from pathlib import Path

def list_logs():
    """List all log files in the logs directory"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("Logs directory does not exist")
        return
    
    log_files = list(logs_dir.glob("*.log*"))
    if not log_files:
        print("No log files found")
        return
    
    print("Log files:")
    for log_file in sorted(log_files):
        size = log_file.stat().st_size
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"  {log_file.name:<20} {size:>10} bytes  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")

def clean_old_logs(keep_days=30):
    """Clean up log files older than specified days"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("Logs directory does not exist")
        return
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    removed_count = 0
    
    for log_file in logs_dir.glob("*.log*"):
        if log_file.name == "README.md":
            continue
            
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime < cutoff_date:
            print(f"Removing old log file: {log_file.name}")
            log_file.unlink()
            removed_count += 1
    
    print(f"Removed {removed_count} old log files")

def compress_logs():
    """Compress log files to save space"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("Logs directory does not exist")
        return
    
    compressed_count = 0
    
    for log_file in logs_dir.glob("*.log.*"):
        if log_file.suffix == ".gz":
            continue
            
        compressed_file = log_file.with_suffix(log_file.suffix + ".gz")
        if compressed_file.exists():
            continue
        
        print(f"Compressing {log_file.name}")
        
        with open(log_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file after successful compression
        log_file.unlink()
        compressed_count += 1
    
    print(f"Compressed {compressed_count} log files")

def show_log_stats():
    """Show log file statistics"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("Logs directory does not exist")
        return
    
    log_files = list(logs_dir.glob("*.log*"))
    if not log_files:
        print("No log files found")
        return
    
    total_size = sum(f.stat().st_size for f in log_files)
    total_files = len(log_files)
    
    print(f"Log Statistics:")
    print(f"  Total files: {total_files}")
    print(f"  Total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
    
    # Show size by file type
    regular_logs = [f for f in log_files if f.suffix == ".log"]
    rotated_logs = [f for f in log_files if f.suffix != ".log" and not f.name.endswith(".gz")]
    compressed_logs = [f for f in log_files if f.name.endswith(".gz")]
    
    if regular_logs:
        size = sum(f.stat().st_size for f in regular_logs)
        print(f"  Regular logs: {len(regular_logs)} files, {size:,} bytes")
    
    if rotated_logs:
        size = sum(f.stat().st_size for f in rotated_logs)
        print(f"  Rotated logs: {len(rotated_logs)} files, {size:,} bytes")
    
    if compressed_logs:
        size = sum(f.stat().st_size for f in compressed_logs)
        print(f"  Compressed logs: {len(compressed_logs)} files, {size:,} bytes")

def tail_log(lines=50):
    """Show the last N lines of the main log file"""
    main_log = Path("logs/mindbot.log")
    if not main_log.exists():
        print("Main log file does not exist")
        return
    
    try:
        with open(main_log, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            print("".join(last_lines))
    except Exception as e:
        print(f"Error reading log file: {e}")

def main():
    parser = argparse.ArgumentParser(description="MindBot Log Management")
    parser.add_argument("command", choices=["list", "clean", "compress", "stats", "tail"], 
                       help="Command to execute")
    parser.add_argument("--days", type=int, default=30, 
                       help="Days to keep when cleaning (default: 30)")
    parser.add_argument("--lines", type=int, default=50, 
                       help="Number of lines to show when tailing (default: 50)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_logs()
    elif args.command == "clean":
        clean_old_logs(args.days)
    elif args.command == "compress":
        compress_logs()
    elif args.command == "stats":
        show_log_stats()
    elif args.command == "tail":
        tail_log(args.lines)

if __name__ == "__main__":
    main()
