#!/usr/bin/env python3
#this belongs in apps/gui/load_core_dialog.py - Version: 1
# X-Seti - November23 2025 - Multi-Emulator Launcher - Load Core Dialog

"""
Load Core Dialog
Quick browser for loading cores from cores directory
Shows installed cores with details and allows manual selection
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem, QTextEdit,
                            QFileDialog, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

##Methods list -
# __init__
# _browse_core
# _create_ui
# _load_core_details
# _on_core_selected
# _scan_cores

##class LoadCoreDialog -

class LoadCoreDialog(QDialog): #vers 1
    """Dialog for loading cores"""
    
    core_selected = pyqtSignal(str, str)  # core_name, core_path
    
    def __init__(self, cores_dir: Path, parent=None): #vers 1
        """Initialize load core dialog
        
        Args:
            cores_dir: Directory containing cores
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.cores_dir = Path(cores_dir)
        self.cores_list = []
        self.selected_core = None
        
        self.setWindowTitle("Load Core")
        self.resize(700, 500)
        
        self._scan_cores()
        self._create_ui()
        
        # Select first core if available
        if self.core_listwidget.count() > 0:
            self.core_listwidget.setCurrentRow(0)
    
    def _scan_cores(self): #vers 2
        """Scan for available cores (system + local)"""
        from apps.methods.system_core_scanner import SystemCoreScanner

        # Initialize scanner
        scanner = SystemCoreScanner(self.cores_dir)

        # Get all cores with source info
        cores_with_source = scanner.get_all_cores()

        # Build list with source tags
        self.cores_list = []
        self.cores_sources = {}  # core_path -> source

        for core_name, core_path, source in cores_with_source:
            self.cores_list.append(core_path)
            self.cores_sources[core_path] = source

        print(f"Found {len(self.cores_list)} core(s)")
    
    def _create_ui(self): #vers 1
        """Create dialog UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"<b>Available Cores</b> ({len(self.cores_list)} cores)")
        header.setFont(QFont("Sans", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Info
        info = QLabel(f"Cores directory: {self.cores_dir}")
        info.setStyleSheet("color: gray; font-style: italic;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Search/filter
        search_layout = QHBoxLayout()
        search_label = QLabel("Filter:")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to filter cores...")
        self.search_box.textChanged.connect(self._filter_cores)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # Core list
        list_label = QLabel("Installed Cores:")
        layout.addWidget(list_label)
        
        self.core_listwidget = QListWidget()
        self.core_listwidget.currentRowChanged.connect(self._on_core_selected)
        
        # Populate list with source tags
        for core_path in self.cores_list:
            core_name = core_path.stem.replace("_libretro", "")
            size_kb = core_path.stat().st_size / 1024
            source = self.cores_sources.get(core_path, 'unknown')

            # Add source tag - TODO - SVG icons needed for local, system and flatpak
            source_tag = {
                'local': '',
                'system': '',
                'flatpak': ''
            }.get(source, '')

            item_text = f"{source_tag} {core_name} ({size_kb:.1f} KB) [{source}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, core_path)
            self.core_listwidget.addItem(item)
        
        layout.addWidget(self.core_listwidget)
        
        # Core details
        details_label = QLabel("Core Details:")
        layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(self.details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_core)
        button_layout.addWidget(browse_btn)
        
        button_layout.addStretch()
        
        self.load_btn = QPushButton("Load Core")
        self.load_btn.clicked.connect(self._load_selected_core)
        self.load_btn.setEnabled(False)
        self.load_btn.setDefault(True)
        button_layout.addWidget(self.load_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _filter_cores(self, text): #vers 1
        """Filter core list by search text"""
        for i in range(self.core_listwidget.count()):
            item = self.core_listwidget.item(i)
            core_path = item.data(Qt.ItemDataRole.UserRole)
            core_name = core_path.stem
            
            # Show item if text matches
            visible = text.lower() in core_name.lower()
            item.setHidden(not visible)
    
    def _on_core_selected(self, index): #vers 1
        """Handle core selection"""
        if index < 0:
            self.load_btn.setEnabled(False)
            return
        
        item = self.core_listwidget.item(index)
        core_path = item.data(Qt.ItemDataRole.UserRole)
        
        self.selected_core = core_path
        self.load_btn.setEnabled(True)
        
        # Load details
        self._load_core_details(core_path)
    
    def _load_core_details(self, core_path: Path): #vers 1
        """Load and display core details"""
        core_name = core_path.stem.replace("_libretro", "")
        size_bytes = core_path.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_bytes / (1024 * 1024)
        
        # Get file info
        from datetime import datetime
        modified = datetime.fromtimestamp(core_path.stat().st_mtime)
        
        details = f"""
<b>Core Name:</b> {core_name}<br>
<b>File Name:</b> {core_path.name}<br>
<b>Size:</b> {size_mb:.2f} MB ({size_kb:.1f} KB)<br>
<b>Modified:</b> {modified.strftime('%Y-%m-%d %H:%M:%S')}<br>
<b>Path:</b> {core_path}<br>
        """
        
        self.details_text.setHtml(details.strip())
    
    def _browse_core(self): #vers 1
        """Browse for core file outside cores directory"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            filter_str = "Core Files (*.dll);;All Files (*)"
        elif system == "Darwin":
            filter_str = "Core Files (*.dylib);;All Files (*)"
        else:
            filter_str = "Core Files (*.so);;All Files (*)"
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Core File",
            str(self.cores_dir),
            filter_str
        )
        
        if not filename:
            return
        
        core_path = Path(filename)
        
        if not core_path.exists():
            QMessageBox.warning(self, "Invalid File", "File does not exist.")
            return
        
        # Update selection
        self.selected_core = core_path
        self._load_core_details(core_path)
        self.load_btn.setEnabled(True)
        
        # Show in list if it's in cores directory
        for i in range(self.core_listwidget.count()):
            item = self.core_listwidget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == core_path:
                self.core_listwidget.setCurrentRow(i)
                return
        
        # Add to list if not there
        core_name = core_path.stem.replace("_libretro", "")
        size_kb = core_path.stat().st_size / 1024
        item_text = f"{core_name} ({size_kb:.1f} KB) [external]"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, core_path)
        self.core_listwidget.addItem(item)
        self.core_listwidget.setCurrentItem(item)
    
    def _load_selected_core(self): #vers 1
        """Load selected core"""
        if not self.selected_core:
            return
        
        core_name = self.selected_core.stem.replace("_libretro", "")
        
        # Emit signal
        self.core_selected.emit(core_name, str(self.selected_core))
        
        self.accept()
    
    def get_selected_core(self) -> Optional[tuple]: #vers 1
        """Get selected core info
        
        Returns:
            Tuple of (core_name, core_path) or None
        """
        if not self.selected_core:
            return None
        
        core_name = self.selected_core.stem.replace("_libretro", "")
        return (core_name, str(self.selected_core))


# Standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    cores_dir = Path("./cores")
    
    dialog = LoadCoreDialog(cores_dir)
    
    if dialog.exec():
        result = dialog.get_selected_core()
        if result:
            print(f"Selected: {result[0]}")
            print(f"Path: {result[1]}")
