import os
import sys
import time
import psutil
import win32api
import win32process
import win32gui
import win32con
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue
import collections

class StorageChange:
    def __init__(self, path, size_change, change_type, timestamp, process_name=None):
        self.path = path
        self.size_change = size_change
        self.change_type = change_type  # 'created', 'modified', 'deleted'
        self.timestamp = timestamp
        self.process_name = process_name
        self.file_extension = self._get_extension()
        
    def _get_extension(self):
        try:
            return Path(self.path).suffix.lower()
        except:
            return ""

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, change_queue):
        super().__init__()
        self.change_queue = change_queue
        self.last_sizes = {}
        self.process_cache = {}
        self.cache_timeout = 5
        
    def on_created(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'created')
    
    def on_modified(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'modified')
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._handle_file_change(event.src_path, 'deleted')
    
    def _handle_file_change(self, file_path, change_type):
        try:
            current_size = 0
            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
            
            size_change = current_size - self.last_sizes.get(file_path, 0)
            self.last_sizes[file_path] = current_size
            
            if size_change != 0:
                process_name = self._get_process_using_file(file_path)
                change = StorageChange(
                    file_path, 
                    size_change, 
                    change_type, 
                    datetime.now(),
                    process_name
                )
                self.change_queue.put(change)
        except Exception as e:
            print(f"Error handling file change: {e}")
    
    def _get_process_using_file(self, file_path):
        try:
            current_time = time.time()
            if file_path in self.process_cache:
                cached_time, cached_process = self.process_cache[file_path]
                if current_time - cached_time < self.cache_timeout:
                    return cached_process
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_obj = psutil.Process(proc.info['pid'])
                    open_files = proc_obj.open_files()
                    
                    for file in open_files:
                        if file.path == file_path:
                            self.process_cache[file_path] = (current_time, proc.info['name'])
                            return proc.info['name']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception:
                    continue
        except Exception:
            pass
        
        self._clean_cache()
        return "Unknown"
    
    def _clean_cache(self):
        current_time = time.time()
        self.process_cache = {k: v for k, v in self.process_cache.items() 
                            if current_time - v[0] < self.cache_timeout}

class ConsoleStorageMonitor:
    def __init__(self, drive_path="C:\\"):
        self.drive_path = drive_path
        self.running = False
        self.observer = None
        self.handler = None
        self.change_queue = queue.Queue()
        self.changes = []
        self.stats = {
            'total_changes': 0,
            'total_size_change': 0,
            'processes': collections.defaultdict(int),
            'file_types': collections.defaultdict(int),
            'directories': collections.defaultdict(int)
        }
        
    def start_monitoring(self):
        print(f"Starting storage monitoring for {self.drive_path}")
        print("Press Ctrl+C to stop monitoring")
        print("Press 's' + Enter to show statistics")
        print("Press 'a' + Enter to show analysis")
        print("Press 'c' + Enter to clear history")
        print("-" * 80)
        
        self.handler = FileChangeHandler(self.change_queue)
        self.observer = Observer()
        
        # Monitor important directories
        important_dirs = [
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Windows\\Temp",
            "C:\\Users\\Public\\Downloads",
            "C:\\Users\\Public\\Desktop"
        ]
        
        for directory in important_dirs:
            if os.path.exists(directory):
                try:
                    self.observer.schedule(self.handler, directory, recursive=True)
                    print(f"Monitoring: {directory}")
                except Exception as e:
                    print(f"Could not monitor {directory}: {e}")
        
        self.observer.start()
        
        self.running = True
        
        # Start display thread
        display_thread = threading.Thread(target=self.display_changes)
        display_thread.daemon = True
        display_thread.start()
        
        # Start input thread
        input_thread = threading.Thread(target=self.handle_input)
        input_thread.daemon = True
        input_thread.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            self.stop()
    
    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def handle_input(self):
        while self.running:
            try:
                user_input = input().strip().lower()
                if user_input == 's':
                    self.show_statistics()
                elif user_input == 'a':
                    self.show_analysis()
                elif user_input == 'c':
                    self.clear_history()
                elif user_input == 'q':
                    self.running = False
                    break
            except EOFError:
                break
            except Exception:
                pass
    
    def display_changes(self):
        while self.running:
            try:
                change = self.change_queue.get(timeout=1)
                self.changes.append(change)
                
                # Keep only last 200 changes
                if len(self.changes) > 200:
                    self.changes = self.changes[-200:]
                
                self.update_stats(change)
                self.print_change(change)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in display thread: {e}")
    
    def update_stats(self, change):
        self.stats['total_changes'] += 1
        self.stats['total_size_change'] += change.size_change
        self.stats['processes'][change.process_name] += 1
        self.stats['file_types'][change.file_extension] += 1
        
        # Track directory
        try:
            directory = os.path.dirname(change.path)
            self.stats['directories'][directory] += 1
        except:
            pass
    
    def print_change(self, change):
        timestamp = change.timestamp.strftime("%H:%M:%S")
        
        # Format size change
        size_str = f"{change.size_change:+,} bytes"
        if abs(change.size_change) > 1024*1024:
            size_str = f"{change.size_change/(1024*1024):+,.1f} MB"
        elif abs(change.size_change) > 1024:
            size_str = f"{change.size_change/1024:+,.1f} KB"
        
        # Truncate long paths
        path = change.path
        if len(path) > 70:
            path = "..." + path[-67:]
        
        # Color coding based on change type
        change_symbol = {
            'created': '+',
            'modified': '~',
            'deleted': '-'
        }.get(change.change_type, '?')
        
        print(f"[{timestamp}] {change_symbol} {size_str:>12} | {change.process_name:>15} | {change.file_extension:>6} | {path}")
    
    def show_statistics(self):
        if not self.changes:
            print("\nNo changes detected yet.")
            return
        
        print(f"\n{'='*60}")
        print("STORAGE MONITOR STATISTICS")
        print(f"{'='*60}")
        
        # Overall stats
        print(f"Total Changes: {self.stats['total_changes']}")
        print(f"Total Size Change: {self.stats['total_size_change']:+,} bytes")
        if abs(self.stats['total_size_change']) > 1024*1024:
            print(f"                ({self.stats['total_size_change']/(1024*1024):+,.1f} MB)")
        
        # Top processes
        print(f"\nTop Processes ({len(self.stats['processes'])} total):")
        for process, count in sorted(self.stats['processes'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {process:>20}: {count:>4} changes")
        
        # Top file types
        print(f"\nTop File Types ({len(self.stats['file_types'])} total):")
        for ext, count in sorted(self.stats['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            if ext:
                print(f"  {ext:>10}: {count:>4} changes")
            else:
                print(f"  {'(no ext)':>10}: {count:>4} changes")
        
        # Top directories
        print(f"\nTop Directories ({len(self.stats['directories'])} total):")
        for directory, count in sorted(self.stats['directories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            dir_name = os.path.basename(directory) if directory != directory else directory
            print(f"  {dir_name:>20}: {count:>4} changes")
        
        print(f"{'='*60}")
    
    def show_analysis(self):
        if not self.changes:
            print("\nNo changes detected yet.")
            return
        
        print(f"\n{'='*60}")
        print("DETAILED ANALYSIS")
        print(f"{'='*60}")
        
        # Recent changes by process
        recent_changes = [c for c in self.changes if (datetime.now() - c.timestamp).seconds < 300]  # Last 5 minutes
        
        if recent_changes:
            print(f"Recent Changes (Last 5 minutes): {len(recent_changes)}")
            
            # Group by process
            process_changes = collections.defaultdict(list)
            for change in recent_changes:
                process_changes[change.process_name].append(change)
            
            for process, changes in process_changes.items():
                process_total = sum(c.size_change for c in changes)
                size_str = f"{process_total:+,} bytes"
                if abs(process_total) > 1024*1024:
                    size_str = f"{process_total/(1024*1024):+,.1f} MB"
                elif abs(process_total) > 1024:
                    size_str = f"{process_total/1024:+,.1f} KB"
                
                print(f"\n{process}:")
                print(f"  Total change: {size_str}")
                print(f"  Files affected: {len(changes)}")
                
                # Show file types used by this process
                file_types = collections.defaultdict(int)
                for change in changes:
                    file_types[change.file_extension] += 1
                
                print(f"  File types: {', '.join([f'{ext}({count})' for ext, count in file_types.items() if ext])}")
                
                # Show recent files
                for change in changes[-3:]:  # Last 3 files
                    size_str = f"{change.size_change:+,} bytes"
                    if abs(change.size_change) > 1024*1024:
                        size_str = f"{change.size_change/(1024*1024):+,.1f} MB"
                    elif abs(change.size_change) > 1024:
                        size_str = f"{change.size_change/1024:+,.1f} KB"
                    
                    print(f"    {change.path} ({size_str})")
        
        # Largest changes
        print(f"\nLargest Changes:")
        largest = sorted(self.changes, key=lambda x: abs(x.size_change), reverse=True)[:10]
        for i, change in enumerate(largest, 1):
            size_str = f"{change.size_change:+,} bytes"
            if abs(change.size_change) > 1024*1024:
                size_str = f"{change.size_change/(1024*1024):+,.1f} MB"
            elif abs(change.size_change) > 1024:
                size_str = f"{change.size_change/1024:+,.1f} KB"
            
            path = change.path
            if len(path) > 50:
                path = "..." + path[-47:]
            
            print(f"{i:2}. {size_str:>12} | {change.process_name:>15} | {change.file_extension:>6} | {path}")
        
        print(f"{'='*60}")
    
    def clear_history(self):
        self.changes.clear()
        self.stats = {
            'total_changes': 0,
            'total_size_change': 0,
            'processes': collections.defaultdict(int),
            'file_types': collections.defaultdict(int),
            'directories': collections.defaultdict(int)
        }
        print("\nHistory cleared!")

def show_disk_usage():
    try:
        disk_usage = psutil.disk_usage("C:\\")
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        usage_percent = (used_gb / total_gb) * 100
        
        print("CURRENT DISK USAGE:")
        print(f"Total Space: {total_gb:.1f} GB")
        print(f"Used Space:  {used_gb:.1f} GB ({usage_percent:.1f}%)")
        print(f"Free Space:  {free_gb:.1f} GB")
        print()
        
    except Exception as e:
        print(f"Error getting disk usage: {e}")

def main():
    print("Real-Time Storage Monitor (Enhanced Console Version)")
    print("=" * 60)
    
    show_disk_usage()
    
    monitor = ConsoleStorageMonitor("C:\\")
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        pass
    finally:
        monitor.show_statistics()
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main() 