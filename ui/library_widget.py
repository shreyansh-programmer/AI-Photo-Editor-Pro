"""
Advance Editor - Library & Catalog System
Provides a Lightroom-style grid view of photos in a directory.
"""
import os
import cv2
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QSplitter,
    QTreeView)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QDir, QThread
from PyQt6.QtGui import QIcon, QPixmap, QImage, QFileSystemModel, QColor

class ThumbnailLoader(QThread):
    finished = pyqtSignal(str, QIcon)
    
    def __init__(self, filepath, size=200):
        super().__init__()
        self.filepath = filepath
        self.size = size
        
    def run(self):
        try:
            # Use OpenCV to read image efficiently
            img = cv2.imread(self.filepath, cv2.IMREAD_REDUCED_COLOR_4)
            if img is None:
                img = cv2.imread(self.filepath)
            
            if img is not None:
                # Resize keeping aspect ratio
                h, w = img.shape[:2]
                ratio = self.size / max(h, w)
                small = cv2.resize(img, (int(w * ratio), int(h * ratio)))
                
                rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
                qimg = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.shape[1] * 3, QImage.Format.Format_RGB888).copy()
                icon = QIcon(QPixmap.fromImage(qimg))
                self.finished.emit(self.filepath, icon)
        except Exception as e:
            print(f"Error loading thumbnail for {self.filepath}: {e}")

class LibraryWidget(QWidget):
    """Grid view of images for the catalog."""
    photo_selected = pyqtSignal(str)  # Emits filepath when a photo is double clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("libraryArea")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Splitter for folder tree and grid
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Folders
        folder_widget = QWidget()
        folder_widget.setFixedWidth(250)
        folder_layout = QVBoxLayout(folder_widget)
        folder_layout.setContentsMargins(8, 8, 8, 8)
        
        lbl = QLabel("FOLDERS")
        lbl.setStyleSheet("color: #a1a1aa; font-weight: 600; font-size: 11px; letter-spacing: 1px;")
        folder_layout.addWidget(lbl)
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs)
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)
        self.tree.clicked.connect(self._on_folder_clicked)
        self.tree.setStyleSheet("""
            QTreeView { background: transparent; border: none; color: #d4d4d8; }
            QTreeView::item:hover { background: rgba(255,255,255,0.05); }
            QTreeView::item:selected { background: rgba(124,58,237,0.2); color: #fff; }
        """)
        folder_layout.addWidget(self.tree)
        splitter.addWidget(folder_widget)
        
        # Right side: Grid
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        grid_layout.setContentsMargins(16, 16, 16, 16)
        
        top_bar = QHBoxLayout()
        self.folder_label = QLabel("Select a folder to view photos")
        self.folder_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        top_bar.addWidget(self.folder_label)
        top_bar.addStretch()
        
        self.btn_sync = QPushButton("Sync Active Edits to All")
        self.btn_sync.setToolTip("Applies the current Develop settings to all photos in this folder")
        self.btn_sync.setStyleSheet("background: #7c3aed; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        self.btn_sync.hide()  # Hidden until we have an active edit
        top_bar.addWidget(self.btn_sync)
        
        btn_import = QPushButton("Import Photos")
        btn_import.clicked.connect(self._choose_folder)
        top_bar.addWidget(btn_import)
        grid_layout.addLayout(top_bar)
        
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.setIconSize(QSize(200, 200))
        self.list_widget.setGridSize(QSize(220, 240))
        self.list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list_widget.setSpacing(16)
        self.list_widget.setStyleSheet("""
            QListWidget { background: #0c0c0f; border: none; outline: none; }
            QListWidget::item { color: #d4d4d8; font-size: 12px; border-radius: 8px; padding: 8px; }
            QListWidget::item:hover { background: rgba(255,255,255,0.05); }
            QListWidget::item:selected { background: rgba(124,58,237,0.2); border: 2px solid #7c3aed; }
        """)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        grid_layout.addWidget(self.list_widget)
        
        splitter.addWidget(grid_widget)
        splitter.setSizes([250, 800])
        
        layout.addWidget(splitter)
        
        self._current_folder = ""
        self._loaders = []

    def _choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.tree.setCurrentIndex(self.file_model.index(folder))
            self.load_folder(folder)

    def _on_folder_clicked(self, index):
        path = self.file_model.filePath(index)
        self.load_folder(path)

    def load_folder(self, folder_path):
        self._current_folder = folder_path
        self.folder_label.setText(os.path.basename(folder_path) or folder_path)
        self.list_widget.clear()
        self._loaders.clear()
        
        valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
        try:
            files = [f for f in os.listdir(folder_path) 
                     if os.path.splitext(f.lower())[1] in valid_exts]
        except Exception:
            return
            
        for f in sorted(files):
            filepath = os.path.join(folder_path, f)
            item = QListWidgetItem(f)
            item.setData(Qt.ItemDataRole.UserRole, filepath)
            
            # Placeholder
            pix = QPixmap(200, 200)
            pix.fill(QColor(30, 30, 35))
            item.setIcon(QIcon(pix))
            
            self.list_widget.addItem(item)
            
            loader = ThumbnailLoader(filepath)
            loader.finished.connect(self._on_thumbnail_loaded)
            self._loaders.append(loader)
            loader.start()

    def _on_thumbnail_loaded(self, filepath, icon):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == filepath:
                item.setIcon(icon)
                break

    def _on_item_double_clicked(self, item):
        filepath = item.data(Qt.ItemDataRole.UserRole)
        self.photo_selected.emit(filepath)
