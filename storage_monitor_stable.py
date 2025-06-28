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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTableWidget, QTableWidgetItem, QLabel, 
                             QPushButton, QTextEdit, QSplitter, QHeaderView, QTabWidget,
                             QMessageBox, QProgressBar, QCheckBox, QFrame, QGroupBox,
                             QSlider, QComboBox, QSpinBox, QGridLayout, QScrollArea)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt, QMutex, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QBrush, QPen, QPixmap
import json

class StorageChange:
    def __init__(self, path, size_change, change_type, timestamp, process_name=None):
        self.path = path
        self.size_change = size_change
        self.change_type = change_type
        self.timestamp = timestamp
        self.process_name = process_name
        self.file_extension = self._get_extension()
        
    def _get_extension(self):
        try:
            return Path(self.path).suffix.lower()
        except:
            return ""

class GamingSession:
    def __init__(self, start_time):
        self.start_time = start_time
        self.end_time = None
        self.start_snapshot = {}
        self.end_snapshot = {}
        self.changes = []
        self.total_size_change = 0
        
    def add_change(self, change):
        self.changes.append(change)
        self.total_size_change += change.size_change

class SimpleTreemapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.setMinimumSize(400, 300)
        
    def update_data(self, data):
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        if not self.data:
            return
            
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Get widget dimensions
            width = self.width()
            height = self.height()
            
            if width <= 0 or height <= 0:
                return
                
            # Calculate total size for normalization
            total_size = sum(item['size'] for item in self.data)
            if total_size == 0:
                return
                
            # Sort data by size (largest first)
            sorted_data = sorted(self.data, key=lambda x: x['size'], reverse=True)
            
            # Simple grid layout
            self.draw_simple_grid(painter, width, height, sorted_data, total_size)
            
        except Exception as e:
            print(f"Error in treemap paint: {e}")
    
    def draw_simple_grid(self, painter, width, height, data, total_size):
        try:
            # Calculate grid dimensions
            item_count = len(data)
            if item_count == 0:
                return
                
            # Simple grid layout
            cols = int(item_count ** 0.5) + 1
            rows = (item_count + cols - 1) // cols
            
            cell_width = width // cols
            cell_height = height // rows
            
            for i, item in enumerate(data):
                if i >= item_count:
                    break
                    
                row = i // cols
                col = i % cols
                
                x = col * cell_width
                y = row * cell_height
                
                # Ensure minimum size
                draw_width = max(1, cell_width - 2)
                draw_height = max(1, cell_height - 2)
                
                # Calculate color based on size
                ratio = item['size'] / total_size if total_size > 0 else 0
                intensity = int(100 + ratio * 155)
                color = QColor(intensity, intensity // 2, intensity // 3)
                
                # Draw rectangle
                painter.fillRect(x + 1, y + 1, draw_width, draw_height, QBrush(color))
                
                # Draw border
                painter.setPen(QPen(QColor(50, 50, 50), 1))
                painter.drawRect(x + 1, y + 1, draw_width, draw_height)
                
                # Draw text if space allows
                if draw_width > 40 and draw_height > 30:
                    painter.setPen(QColor(255, 255, 255))
                    font = QFont()
                    font.setPointSize(7)
                    painter.setFont(font)
                    
                    # Truncate name if too long
                    name = item['name']
                    if len(name) > 15:
                        name = name[:12] + "..."
                    
                    text = f"{name}\n{self.format_size(item['size'])}"
                    painter.drawText(x + 3, y + 3, draw_width - 6, draw_height - 6, 
                                   Qt.AlignLeft | Qt.AlignTop, text)
                    
        except Exception as e:
            print(f"Error in grid drawing: {e}")
    
    def format_size(self, size):
        if size > 1024**3:
            return f"{size/(1024**3):.1f}GB"
        elif size > 1024**2:
            return f"{size/(1024**2):.1f}MB"
        elif size > 1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size}B"

class LightweightStorageMonitor(QThread):
    change_detected = pyqtSignal(object)
    status_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.file_sizes = {}
        self.process_cache = {}
        self.cache_timeout = 10
        self.monitored_dirs = [
            os.path.expanduser("~\\AppData\\Local\\Temp"),
            os.path.expanduser("~\\AppData\\Roaming"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            "C:\\Windows\\Temp",
            "C:\\Users\\Public\\Downloads"
        ]
        
    def run(self):
        self.running = True
        self.status_update.emit("Initializing file monitoring...")
        
        # Initialize file sizes
        self.scan_files()
        self.status_update.emit("Monitoring active - scanning for changes...")
        
        while self.running:
            try:
                self.check_for_changes()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                self.status_update.emit(f"Error: {str(e)}")
                time.sleep(5)
    
    def scan_files(self):
        """Initial scan of files to establish baseline"""
        self.file_sizes.clear()
        for directory in self.monitored_dirs:
            if os.path.exists(directory):
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    size = os.path.getsize(file_path)
                                    self.file_sizes[file_path] = size
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue
    
    def check_for_changes(self):
        """Check for file changes using polling"""
        current_files = {}
        
        # Get current file sizes
        for directory in self.monitored_dirs:
            if os.path.exists(directory):
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    size = os.path.getsize(file_path)
                                    current_files[file_path] = size
                            except (OSError, PermissionError):
                                continue
                except (OSError, PermissionError):
                    continue
        
        # Check for changes
        for file_path, current_size in current_files.items():
            old_size = self.file_sizes.get(file_path, 0)
            
            if current_size != old_size:
                size_change = current_size - old_size
                if size_change != 0:
                    change_type = 'modified' if old_size > 0 else 'created'
                    process_name = self._get_process_using_file(file_path)
                    
                    change = StorageChange(
                        file_path,
                        size_change,
                        change_type,
                        datetime.now(),
                        process_name
                    )
                    
                    self.change_detected.emit(change)
                
                self.file_sizes[file_path] = current_size
        
        # Check for deleted files
        deleted_files = set(self.file_sizes.keys()) - set(current_files.keys())
        for file_path in deleted_files:
            old_size = self.file_sizes[file_path]
            if old_size > 0:
                change = StorageChange(
                    file_path,
                    -old_size,
                    'deleted',
                    datetime.now(),
                    "Unknown"
                )
                self.change_detected.emit(change)
            
            del self.file_sizes[file_path]
    
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
    
    def stop(self):
        self.running = False

class StorageAnalyzer:
    def __init__(self):
        self.changes = []
        self.mutex = QMutex()
        self.gaming_sessions = []
        self.current_gaming_session = None
        
    def add_change(self, change):
        self.mutex.lock()
        try:
            self.changes.append(change)
            if len(self.changes) > 500:
                self.changes = self.changes[-500:]
            
            # Add to current gaming session if active
            if self.current_gaming_session:
                self.current_gaming_session.add_change(change)
        finally:
            self.mutex.unlock()
    
    def start_gaming_session(self):
        self.current_gaming_session = GamingSession(datetime.now())
        # Take snapshot of current state
        self.current_gaming_session.start_snapshot = self.get_current_storage_state()
    
    def end_gaming_session(self):
        if self.current_gaming_session:
            self.current_gaming_session.end_time = datetime.now()
            self.current_gaming_session.end_snapshot = self.get_current_storage_state()
            self.gaming_sessions.append(self.current_gaming_session)
            return self.current_gaming_session
        return None
    
    def get_current_storage_state(self):
        state = {}
        for directory in [
            os.path.expanduser("~\\AppData\\Local\\Temp"),
            os.path.expanduser("~\\AppData\\Roaming"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Desktop"),
            "C:\\Windows\\Temp"
        ]:
            if os.path.exists(directory):
                try:
                    total_size = 0
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                if os.path.exists(file_path):
                                    total_size += os.path.getsize(file_path)
                            except (OSError, PermissionError):
                                continue
                    state[directory] = total_size
                except (OSError, PermissionError):
                    continue
        return state
    
    def get_recent_changes(self, minutes=10):
        self.mutex.lock()
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            return [change for change in self.changes if change.timestamp > cutoff_time]
        finally:
            self.mutex.unlock()
    
    def get_largest_changes(self, count=10):
        self.mutex.lock()
        try:
            return sorted(self.changes, key=lambda x: abs(x.size_change), reverse=True)[:count]
        finally:
            self.mutex.unlock()
    
    def clear_changes(self):
        self.mutex.lock()
        try:
            self.changes.clear()
        finally:
            self.mutex.unlock()

class DarkModeStyle:
    @staticmethod
    def get_dark_stylesheet():
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2b2b2b;
        }
        
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #4a4a4a;
            border-bottom: 2px solid #0078d4;
        }
        
        QTabBar::tab:hover {
            background-color: #404040;
        }
        
        QTableWidget {
            background-color: #1e1e1e;
            alternate-background-color: #2d2d2d;
            gridline-color: #555555;
            color: #ffffff;
            border: 1px solid #555555;
        }
        
        QTableWidget::item {
            padding: 4px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
        }
        
        QHeaderView::section {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #555555;
            font-weight: bold;
        }
        
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QTextEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QLabel {
            color: #ffffff;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 4px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QCheckBox {
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #555555;
            background-color: #2b2b2b;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #0078d4;
            background-color: #0078d4;
        }
        
        QComboBox {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            background-color: #2b2b2b;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        """

class StableStorageMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = StorageAnalyzer()
        self.monitor = None
        self.dark_mode = True
        self.init_ui()
        self.apply_dark_mode()
        self.start_monitoring()
        
    def init_ui(self):
        self.setWindowTitle("Stable Storage Monitor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top control bar
        control_layout = QHBoxLayout()
        
        # Status and controls
        self.status_label = QLabel("Starting...")
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        # Gaming mode controls
        gaming_group = QGroupBox("Gaming Mode")
        gaming_layout = QHBoxLayout(gaming_group)
        
        self.gaming_btn = QPushButton("Start Gaming Session")
        self.gaming_btn.clicked.connect(self.start_gaming_session)
        gaming_layout.addWidget(self.gaming_btn)
        
        self.end_gaming_btn = QPushButton("End Gaming Session")
        self.end_gaming_btn.clicked.connect(self.end_gaming_session)
        self.end_gaming_btn.setEnabled(False)
        gaming_layout.addWidget(self.end_gaming_btn)
        
        control_layout.addWidget(gaming_group)
        
        # Theme toggle
        self.theme_btn = QPushButton("Toggle Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        control_layout.addWidget(self.theme_btn)
        
        layout.addLayout(control_layout)
        
        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Real-time changes tab
        realtime_tab = QWidget()
        realtime_layout = QVBoxLayout(realtime_tab)
        
        # Changes table
        self.changes_table = QTableWidget()
        self.changes_table.setColumnCount(5)
        self.changes_table.setHorizontalHeaderLabels([
            "Time", "Path", "Size Change", "Type", "Process"
        ])
        header = self.changes_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        realtime_layout.addWidget(self.changes_table)
        
        tabs.addTab(realtime_tab, "📊 Real-time Changes")
        
        # Treemap tab
        treemap_tab = QWidget()
        treemap_layout = QVBoxLayout(treemap_tab)
        
        treemap_controls = QHBoxLayout()
        self.treemap_refresh_btn = QPushButton("Refresh Treemap")
        self.treemap_refresh_btn.clicked.connect(self.update_treemap)
        treemap_controls.addWidget(self.treemap_refresh_btn)
        
        self.treemap_type_combo = QComboBox()
        self.treemap_type_combo.addItems(["Largest Files", "Recent Changes", "By Process"])
        self.treemap_type_combo.currentTextChanged.connect(self.update_treemap)
        treemap_controls.addWidget(QLabel("View:"))
        treemap_controls.addWidget(self.treemap_type_combo)
        
        treemap_layout.addLayout(treemap_controls)
        
        self.treemap_widget = SimpleTreemapWidget()
        treemap_layout.addWidget(self.treemap_widget)
        
        tabs.addTab(treemap_tab, "🗺️ Storage Treemap")
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Analysis controls
        analysis_controls = QHBoxLayout()
        self.analyze_btn = QPushButton("Analyze Recent Changes")
        self.analyze_btn.clicked.connect(self.analyze_recent_changes)
        analysis_controls.addWidget(self.analyze_btn)
        
        self.largest_btn = QPushButton("Show Largest Changes")
        self.largest_btn.clicked.connect(self.show_largest_changes)
        analysis_controls.addWidget(self.largest_btn)
        
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)
        analysis_controls.addWidget(self.clear_btn)
        
        analysis_layout.addLayout(analysis_controls)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_text)
        
        tabs.addTab(analysis_tab, "📈 Analysis")
        
        # Gaming sessions tab
        gaming_tab = QWidget()
        gaming_tab_layout = QVBoxLayout(gaming_tab)
        
        self.gaming_sessions_text = QTextEdit()
        self.gaming_sessions_text.setReadOnly(True)
        gaming_tab_layout.addWidget(self.gaming_sessions_text)
        
        tabs.addTab(gaming_tab, "🎮 Gaming Sessions")
        
        # Storage overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        overview_layout.addWidget(self.overview_text)
        
        tabs.addTab(overview_tab, "💾 Storage Overview")
        
        # Set up timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_overview)
        self.update_timer.start(15000)  # Update every 15 seconds
        
        # Set up timer for table updates
        self.table_timer = QTimer()
        self.table_timer.timeout.connect(self.update_changes_table)
        self.table_timer.start(3000)  # Update table every 3 seconds
        
    def apply_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet(DarkModeStyle.get_dark_stylesheet())
        else:
            self.setStyleSheet("")
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_dark_mode()
        
    def start_monitoring(self):
        self.monitor = LightweightStorageMonitor()
        self.monitor.change_detected.connect(self.on_storage_change)
        self.monitor.status_update.connect(self.on_status_update)
        self.monitor.start()
        
    def on_storage_change(self, change):
        self.analyzer.add_change(change)
        
    def on_status_update(self, status):
        self.status_label.setText(status)
        
    def start_gaming_session(self):
        self.analyzer.start_gaming_session()
        self.gaming_btn.setEnabled(False)
        self.end_gaming_btn.setEnabled(True)
        self.status_label.setText("🎮 Gaming session started - monitoring paused")
        
        # Stop intensive monitoring
        if self.monitor:
            self.monitor.stop()
            self.monitor.wait(1000)
        
        QMessageBox.information(self, "Gaming Mode", 
                              "Gaming session started!\n\n"
                              "Storage monitoring has been paused to reduce performance impact.\n"
                              "Click 'End Gaming Session' when you're done to see what changed.")
        
    def end_gaming_session(self):
        session = self.analyzer.end_gaming_session()
        self.gaming_btn.setEnabled(True)
        self.end_gaming_btn.setEnabled(False)
        
        if session:
            self.show_gaming_analysis(session)
            self.update_gaming_sessions()
        
        # Restart monitoring
        self.start_monitoring()
        self.status_label.setText("Monitoring resumed")
        
    def show_gaming_analysis(self, session):
        duration = session.end_time - session.start_time
        hours = duration.total_seconds() / 3600
        
        analysis = f"🎮 GAMING SESSION ANALYSIS\n"
        analysis += f"{'='*50}\n\n"
        analysis += f"Session Duration: {hours:.1f} hours\n"
        analysis += f"Start Time: {session.start_time.strftime('%H:%M:%S')}\n"
        analysis += f"End Time: {session.end_time.strftime('%H:%M:%S')}\n\n"
        
        if session.changes:
            analysis += f"Total Changes: {len(session.changes)}\n"
            analysis += f"Total Size Change: {session.total_size_change:+,} bytes\n"
            
            if abs(session.total_size_change) > 1024*1024:
                analysis += f"                ({session.total_size_change/(1024*1024):+,.1f} MB)\n"
            
            # Group by process
            process_changes = {}
            for change in session.changes:
                if change.process_name not in process_changes:
                    process_changes[change.process_name] = []
                process_changes[change.process_name].append(change)
            
            analysis += f"\n=== Changes by Process ===\n"
            for process, changes in process_changes.items():
                process_total = sum(c.size_change for c in changes)
                analysis += f"\n{process}:\n"
                analysis += f"  Total change: {process_total:+,} bytes\n"
                analysis += f"  Files affected: {len(changes)}\n"
                
                for change in changes[:5]:  # Show first 5 files per process
                    analysis += f"    {change.path} ({change.size_change:+,} bytes)\n"
        else:
            analysis += "No storage changes detected during gaming session.\n"
        
        QMessageBox.information(self, "Gaming Session Complete", analysis)
        
    def update_gaming_sessions(self):
        if not self.analyzer.gaming_sessions:
            self.gaming_sessions_text.setText("No gaming sessions recorded yet.")
            return
        
        text = "🎮 GAMING SESSIONS HISTORY\n"
        text += f"{'='*50}\n\n"
        
        for i, session in enumerate(reversed(self.analyzer.gaming_sessions), 1):
            duration = session.end_time - session.start_time
            hours = duration.total_seconds() / 3600
            
            text += f"Session {i}:\n"
            text += f"  Duration: {hours:.1f} hours\n"
            text += f"  Start: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"  End: {session.end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            text += f"  Changes: {len(session.changes)}\n"
            text += f"  Size Change: {session.total_size_change:+,} bytes\n"
            
            if abs(session.total_size_change) > 1024*1024:
                text += f"            ({session.total_size_change/(1024*1024):+,.1f} MB)\n"
            
            text += "\n"
        
        self.gaming_sessions_text.setText(text)
        
    def update_treemap(self):
        try:
            view_type = self.treemap_type_combo.currentText()
            
            if view_type == "Largest Files":
                self.update_treemap_largest_files()
            elif view_type == "Recent Changes":
                self.update_treemap_recent_changes()
            elif view_type == "By Process":
                self.update_treemap_by_process()
        except Exception as e:
            print(f"Error updating treemap: {e}")
    
    def update_treemap_largest_files(self):
        try:
            # Get largest files in monitored directories
            large_files = []
            for directory in [
                os.path.expanduser("~\\Downloads"),
                os.path.expanduser("~\\Desktop"),
                os.path.expanduser("~\\Documents"),
                os.path.expanduser("~\\AppData\\Local"),
                "C:\\Windows\\Temp"
            ]:
                if os.path.exists(directory):
                    try:
                        for root, dirs, files in os.walk(directory):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    if os.path.exists(file_path):
                                        size = os.path.getsize(file_path)
                                        if size > 1024*1024:  # Files larger than 1MB
                                            large_files.append({
                                                'name': os.path.basename(file_path),
                                                'size': size,
                                                'path': file_path
                                            })
                                except (OSError, PermissionError):
                                    continue
                    except (OSError, PermissionError):
                        continue
            
            # Sort by size and take top 20
            large_files.sort(key=lambda x: x['size'], reverse=True)
            self.treemap_widget.update_data(large_files[:20])
        except Exception as e:
            print(f"Error updating largest files treemap: {e}")
    
    def update_treemap_recent_changes(self):
        try:
            recent_changes = self.analyzer.get_recent_changes(30)  # Last 30 minutes
            
            # Group by directory
            dir_sizes = {}
            for change in recent_changes:
                try:
                    directory = os.path.dirname(change.path)
                    if directory not in dir_sizes:
                        dir_sizes[directory] = 0
                    dir_sizes[directory] += abs(change.size_change)
                except:
                    continue
            
            # Convert to treemap data
            treemap_data = []
            for directory, total_size in dir_sizes.items():
                if total_size > 0:
                    treemap_data.append({
                        'name': os.path.basename(directory) or directory,
                        'size': total_size,
                        'path': directory
                    })
            
            self.treemap_widget.update_data(treemap_data[:20])
        except Exception as e:
            print(f"Error updating recent changes treemap: {e}")
    
    def update_treemap_by_process(self):
        try:
            recent_changes = self.analyzer.get_recent_changes(30)  # Last 30 minutes
            
            # Group by process
            process_sizes = {}
            for change in recent_changes:
                if change.process_name not in process_sizes:
                    process_sizes[change.process_name] = 0
                process_sizes[change.process_name] += abs(change.size_change)
            
            # Convert to treemap data
            treemap_data = []
            for process, total_size in process_sizes.items():
                if total_size > 0:
                    treemap_data.append({
                        'name': process,
                        'size': total_size,
                        'path': process
                    })
            
            self.treemap_widget.update_data(treemap_data[:20])
        except Exception as e:
            print(f"Error updating process treemap: {e}")
        
    def update_changes_table(self):
        try:
            recent_changes = self.analyzer.get_recent_changes(30)  # Last 30 minutes
            self.changes_table.setRowCount(len(recent_changes))
            
            for i, change in enumerate(reversed(recent_changes)):
                self.changes_table.setItem(i, 0, QTableWidgetItem(
                    change.timestamp.strftime("%H:%M:%S")
                ))
                
                # Truncate long paths
                path = change.path
                if len(path) > 80:
                    path = "..." + path[-77:]
                self.changes_table.setItem(i, 1, QTableWidgetItem(path))
                
                size_str = f"{change.size_change:+,} bytes"
                if abs(change.size_change) > 1024:
                    size_str = f"{change.size_change/1024:+,.1f} KB"
                if abs(change.size_change) > 1024*1024:
                    size_str = f"{change.size_change/(1024*1024):+,.1f} MB"
                    
                self.changes_table.setItem(i, 2, QTableWidgetItem(size_str))
                self.changes_table.setItem(i, 3, QTableWidgetItem(change.change_type))
                self.changes_table.setItem(i, 4, QTableWidgetItem(change.process_name))
        except Exception as e:
            print(f"Error updating table: {e}")
    
    def clear_history(self):
        self.analyzer.clear_changes()
        self.update_changes_table()
        self.analysis_text.clear()
        
    def refresh_data(self):
        self.update_changes_table()
        self.update_overview()
        self.update_treemap()
        
    def analyze_recent_changes(self):
        try:
            recent_changes = self.analyzer.get_recent_changes(10)  # Last 10 minutes
            analysis = "=== Recent Storage Changes (Last 10 minutes) ===\n\n"
            
            if not recent_changes:
                analysis += "No changes detected in the last 10 minutes.\n"
            else:
                total_size_change = sum(change.size_change for change in recent_changes)
                analysis += f"Total size change: {total_size_change:+,} bytes\n"
                
                # Group by process
                process_changes = {}
                for change in recent_changes:
                    if change.process_name not in process_changes:
                        process_changes[change.process_name] = []
                    process_changes[change.process_name].append(change)
                
                analysis += "\n=== Changes by Process ===\n"
                for process, changes in process_changes.items():
                    process_total = sum(c.size_change for c in changes)
                    analysis += f"\n{process}:\n"
                    analysis += f"  Total change: {process_total:+,} bytes\n"
                    analysis += f"  Files affected: {len(changes)}\n"
                    
                    for change in changes[:5]:  # Show first 5 files per process
                        analysis += f"    {change.path} ({change.size_change:+,} bytes)\n"
            
            self.analysis_text.setText(analysis)
        except Exception as e:
            self.analysis_text.setText(f"Error in analysis: {e}")
        
    def show_largest_changes(self):
        try:
            largest_changes = self.analyzer.get_largest_changes(20)
            analysis = "=== Largest Storage Changes ===\n\n"
            
            if not largest_changes:
                analysis += "No changes detected yet.\n"
            else:
                for i, change in enumerate(largest_changes, 1):
                    size_str = f"{change.size_change:+,} bytes"
                    if abs(change.size_change) > 1024*1024:
                        size_str = f"{change.size_change/(1024*1024):+,.1f} MB"
                    elif abs(change.size_change) > 1024:
                        size_str = f"{change.size_change/1024:+,.1f} KB"
                        
                    analysis += f"{i}. {change.path}\n"
                    analysis += f"   Size: {size_str}\n"
                    analysis += f"   Process: {change.process_name}\n"
                    analysis += f"   Time: {change.timestamp.strftime('%H:%M:%S')}\n\n"
            
            self.analysis_text.setText(analysis)
        except Exception as e:
            self.analysis_text.setText(f"Error showing largest changes: {e}")
        
    def update_overview(self):
        try:
            # Get disk usage
            disk_usage = psutil.disk_usage("C:\\")
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (used_gb / total_gb) * 100
            
            overview = f"=== Storage Overview ===\n\n"
            overview += f"Total Space: {total_gb:.1f} GB\n"
            overview += f"Used Space: {used_gb:.1f} GB ({usage_percent:.1f}%)\n"
            overview += f"Free Space: {free_gb:.1f} GB\n\n"
            
            # Monitored directories
            overview += "=== Monitored Directories ===\n"
            monitored_dirs = [
                os.path.expanduser("~\\AppData\\Local\\Temp"),
                os.path.expanduser("~\\AppData\\Roaming"),
                os.path.expanduser("~\\Downloads"),
                os.path.expanduser("~\\Desktop"),
                "C:\\Windows\\Temp",
                "C:\\Users\\Public\\Downloads"
            ]
            
            for directory in monitored_dirs:
                if os.path.exists(directory):
                    try:
                        file_count = sum(len(files) for _, _, files in os.walk(directory))
                        overview += f"{directory}: {file_count} files\n"
                    except Exception:
                        overview += f"{directory}: Access denied\n"
            
            self.overview_text.setText(overview)
            
        except Exception as e:
            self.overview_text.setText(f"Error updating overview: {e}")
    
    def closeEvent(self, event):
        if self.monitor:
            self.monitor.stop()
            self.monitor.wait(3000)  # Wait up to 3 seconds
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Stable Storage Monitor")
    
    window = StableStorageMonitor()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 