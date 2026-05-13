"""
Advance Editor - Main Application Window
Professional photo editor with AI tools, layers, and non-destructive editing.
"""
import os, sys, cv2, logging, numpy as np
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFileDialog, QApplication, QMessageBox,
    QFrame, QSplitter, QProgressBar, QStatusBar, QStackedWidget, QDockWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont

from ui.canvas_widget import CanvasWidget
from ui.panels import AdjustmentPanel, AIToolsPanel, LayerPanel
from ui.curves_widget import CurvesPanel
from ui.filters_panel import FiltersPanel, FilterProcessor
from ui.styles import DARK_THEME
from ui.library_widget import LibraryWidget
from engine.image_processor import ImageProcessor
from engine.ai_engine import AIEngine
from engine.ai_advanced import HDRMergeAI, LensAI, StyleTransferAI, WhiteBalanceAI
from engine.layer_system import LayerSystem
from engine.history import HistoryManager
from engine.batch_processor import Recipe, BatchProcessor
from ui.copilot_panel import CopilotPanel


class AIWorker(QThread):
    """Background thread for AI processing."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advance Editor — AI-Powered Photo Editor")
        self.setMinimumSize(1200, 700)
        self.resize(1500, 900)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(DARK_THEME)

        # Core systems
        self.ai = AIEngine()
        self.layers = LayerSystem()
        self.history = HistoryManager()
        self.processor = ImageProcessor()
        self._current_file = None
        self._worker = None
        self._adjust_timer = QTimer()
        self._adjust_timer.setSingleShot(True)
        self._adjust_timer.setInterval(150)
        self._adjust_timer.timeout.connect(self._apply_adjustments_now)
        self._curve_timer = QTimer()
        self._curve_timer.setSingleShot(True)
        self._curve_timer.setInterval(100)
        self._curve_timer.timeout.connect(self._apply_curves_now)
        self._active_filter = None

        self._build_ui()
        self._build_menu()
        self._connect_signals()
        self._show_welcome()

    # ─── UI Construction ──────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Custom Title Bar (40px height, 8pt grid)
        self._title_bar = QWidget()
        self._title_bar.setObjectName("titleBar")
        self._title_bar.setFixedHeight(40)
        tb_layout = QHBoxLayout(self._title_bar)
        tb_layout.setContentsMargins(12, 0, 0, 0)
        tb_layout.setSpacing(0)

        icon_label = QLabel("◆")
        icon_label.setObjectName("appIcon")
        tb_layout.addWidget(icon_label)

        self._title_label = QLabel("Advance Editor")
        self._title_label.setObjectName("titleLabel")
        tb_layout.addWidget(self._title_label)
        
        # Module Switcher
        tb_layout.addStretch()
        self.btn_library = QPushButton("LIBRARY")
        self.btn_library.setCheckable(True)
        self.btn_library.setChecked(True)
        self.btn_library.clicked.connect(lambda: self._switch_module(0))
        self.btn_library.setStyleSheet("QPushButton { font-weight: bold; border: none; padding: 0 16px; color: #71717a; } QPushButton:checked { color: #a78bfa; }")
        tb_layout.addWidget(self.btn_library)

        self.btn_develop = QPushButton("DEVELOP")
        self.btn_develop.setCheckable(True)
        self.btn_develop.clicked.connect(lambda: self._switch_module(1))
        self.btn_develop.setStyleSheet("QPushButton { font-weight: bold; border: none; padding: 0 16px; color: #71717a; } QPushButton:checked { color: #a78bfa; }")
        tb_layout.addWidget(self.btn_develop)
        tb_layout.addStretch()

        for name, text, slot in [
            ("btnMin", "─", self.showMinimized),
            ("btnMax", "□", self._toggle_maximize),
            ("btnClose", "✕", self.close),
        ]:
            btn = QPushButton(text)
            btn.setObjectName(name)
            btn.setFixedSize(48, 40)
            btn.clicked.connect(slot)
            tb_layout.addWidget(btn)

        root.addWidget(self._title_bar)

        # Menu Bar
        self._menu_bar = self.menuBar()
        root.setMenuBar(None)

        # Main content
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        # Left Toolbar
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedWidth(72)
        tb_v = QVBoxLayout(toolbar)
        tb_v.setContentsMargins(0, 8, 0, 8)
        tb_v.setSpacing(2)

        self._tools = {}
        tools = [
            ("move", "✥", "Move"), ("crop", "⬔", "Crop"),
            ("brush", "🖌", "Brush"), ("eraser", "◯", "Eraser"),
            ("clone", "⊕", "Clone"), ("heal", "✚", "Heal"),
            ("text", "T", "Text"),
        ]
        
        for name, icon, txt in tools:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setToolTip(f"{txt} Tool")
            
            # Vertical layout for icon + text
            l = QVBoxLayout(btn)
            l.setContentsMargins(0, 4, 0, 4)
            l.setSpacing(0)
            
            lbl_ico = QLabel(icon)
            lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_ico.setStyleSheet("font-size: 16px; background: transparent;")
            
            lbl_txt = QLabel(txt)
            lbl_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_txt.setStyleSheet("font-size: 9px; font-weight: bold; background: transparent;")
            
            l.addWidget(lbl_ico)
            l.addWidget(lbl_txt)
            
            btn.clicked.connect(lambda c, n=name: self._select_tool(n))
            tb_v.addWidget(btn)
            self._tools[name] = btn
            
        tb_v.addStretch()

        # Zoom buttons
        zoom_tools = [("⊕", "Zoom In", self._zoom_in), ("⊖", "Zoom Out", self._zoom_out), ("⊡", "Fit", self._fit_view)]
        for icon, txt, slot in zoom_tools:
            btn = QPushButton()
            btn.setToolTip(txt)
            
            l = QVBoxLayout(btn)
            l.setContentsMargins(0, 4, 0, 4)
            l.setSpacing(0)
            
            lbl_ico = QLabel(icon)
            lbl_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_ico.setStyleSheet("font-size: 16px; background: transparent;")
            
            lbl_txt = QLabel(txt.split()[0])
            lbl_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_txt.setStyleSheet("font-size: 9px; font-weight: bold; background: transparent;")
            
            l.addWidget(lbl_ico)
            l.addWidget(lbl_txt)
            
            btn.clicked.connect(slot)
            tb_v.addWidget(btn)

        content.addWidget(toolbar)

        # Canvas
        self.canvas = CanvasWidget()
        self.canvas.on_file_drop = self._load_file
        content.addWidget(self.canvas, 1)

        # Right Panel
        right = QWidget()
        right.setObjectName("rightPanel")
        right.setFixedWidth(330)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._tabs = QTabWidget()
        self._adj_panel = AdjustmentPanel()
        self._curves_panel = CurvesPanel()
        self._filters_panel = FiltersPanel()
        self._ai_panel = AIToolsPanel()
        self._layer_panel = LayerPanel()
        self._copilot_panel = CopilotPanel()
        self._tabs.addTab(self._adj_panel, "Edit")
        self._tabs.addTab(self._curves_panel, "Curves")
        self._tabs.addTab(self._filters_panel, "Filters")
        self._tabs.addTab(self._ai_panel, "AI")
        self._tabs.addTab(self._layer_panel, "Layers")
        right_layout.addWidget(self._tabs)

        content.addWidget(right)
        
        # Copilot Dock Widget (Prominent floating/docked panel)
        self.copilot_dock = QDockWidget("🧠 Advance Copilot", self)
        self.copilot_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.copilot_dock.setWidget(self._copilot_panel)
        self.copilot_dock.setStyleSheet("QDockWidget::title { background: #0f070a; color: #fbcfe8; font-weight: bold; padding: 4px; border-bottom: 1px solid rgba(236,72,153,0.2); }")
        
        # Dock it to the left side by default
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.copilot_dock)

        content_widget = QWidget()
        content_widget.setLayout(content)
        
        self.stacked_widget = QStackedWidget()
        root.addWidget(self.stacked_widget, 1)
        
        self.library = LibraryWidget()
        self.library.photo_selected.connect(self._load_from_library)
        self.library.btn_sync.clicked.connect(self._sync_edits_to_folder)
        self.stacked_widget.addWidget(self.library)
        self.stacked_widget.addWidget(content_widget)

        # Status Bar
        status = QWidget()
        status.setObjectName("statusBar")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(16, 0, 16, 0)
        status_layout.setSpacing(16)
        self._status_label = QLabel("Ready")
        status_layout.addWidget(self._status_label)
        status_layout.addStretch()

        # Model status badge
        self._model_badge = QLabel("● HF Models")
        self._model_badge.setObjectName("modelBadgeOffline")
        status_layout.addWidget(self._model_badge)

        self._zoom_label = QLabel("100%")
        status_layout.addWidget(self._zoom_label)
        self._pos_label = QLabel("")
        self._pos_label.setFixedWidth(80)
        status_layout.addWidget(self._pos_label)
        self._progress = QProgressBar()
        self._progress.setFixedWidth(140)
        self._progress.setVisible(False)
        status_layout.addWidget(self._progress)
        root.addWidget(status)

        # Welcome overlay (generous whitespace)
        self._welcome = QWidget(self.canvas)
        self._welcome.setObjectName("welcomeOverlay")
        wl = QVBoxLayout(self._welcome)
        wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.setSpacing(0)

        title = QLabel("Advance Editor")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(title)

        sub = QLabel("AI-Powered Photo Editing  ·  Powered by HuggingFace")
        sub.setObjectName("welcomeSubtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(sub)

        hint = QLabel("Drop an image here or press Ctrl+O")
        hint.setStyleSheet("color: #3f3f46; font-size: 12px; padding-bottom: 24px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(hint)

        drop = QPushButton("   Open Image   ")
        drop.setObjectName("openButton")
        drop.setFixedHeight(48)
        drop.clicked.connect(self._open_file)
        wl.addWidget(drop, alignment=Qt.AlignmentFlag.AlignCenter)

        # Model info
        model_info = QLabel("\n🧠 rembg (u2net)  ·  Depth Anything V2  ·  OpenCV DNN")
        model_info.setStyleSheet("color: #27272a; font-size: 11px; padding-top: 24px;")
        model_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(model_info)

    def _build_menu(self):
        mb = self._menu_bar

        file_menu = mb.addMenu("File")
        self._add_action(file_menu, "Open", "Ctrl+O", self._open_file)
        self._add_action(file_menu, "Save As...", "Ctrl+Shift+S", self._save_file)
        file_menu.addSeparator()
        self._add_action(file_menu, "Export PNG", "", lambda: self._export("png"))
        self._add_action(file_menu, "Export JPEG", "", lambda: self._export("jpg"))
        self._add_action(file_menu, "Export WebP", "", lambda: self._export("webp"))
        file_menu.addSeparator()
        self._add_action(file_menu, "Exit", "Alt+F4", self.close)

        edit_menu = mb.addMenu("Edit")
        self._add_action(edit_menu, "Undo", "Ctrl+Z", self._undo)
        self._add_action(edit_menu, "Redo", "Ctrl+Y", self._redo)
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Flatten Layers", "", self._flatten_layers)

        view_menu = mb.addMenu("View")
        self._add_action(view_menu, "Fit to Screen", "Ctrl+0", self._fit_view)
        self._add_action(view_menu, "Zoom In", "Ctrl+=", self._zoom_in)
        self._add_action(view_menu, "Zoom Out", "Ctrl+-", self._zoom_out)
        self._add_action(view_menu, "100%", "Ctrl+1", lambda: self.canvas.set_zoom(1.0))

        img_menu = mb.addMenu("Image")
        self._add_action(img_menu, "Rotate 90° CW", "", lambda: self._transform("rotate_cw"))
        self._add_action(img_menu, "Rotate 90° CCW", "", lambda: self._transform("rotate_ccw"))
        self._add_action(img_menu, "Flip Horizontal", "", lambda: self._transform("flip_h"))
        self._add_action(img_menu, "Flip Vertical", "", lambda: self._transform("flip_v"))

    def _add_action(self, menu, text, shortcut, slot):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)

    def _connect_signals(self):
        self._adj_panel.adjustment_changed.connect(self._on_adjustment)
        self._curves_panel.curve_changed.connect(self._on_curve_change)
        self._filters_panel.filter_applied.connect(self._on_filter_applied)
        self._ai_panel.ai_action.connect(self._on_ai_action)
        self._layer_panel.layer_action.connect(self._on_layer_action)
        self.canvas.zoom_changed.connect(lambda z: self._zoom_label.setText(f"{int(z*100)}%"))
        self.canvas.cursor_pos_changed.connect(lambda x, y: self._pos_label.setText(f"{x}, {y}"))
        self._copilot_panel.request_image.connect(self._on_copilot_request_image)
        self._copilot_panel.execute_command.connect(self._on_copilot_execute)

    # ─── File Operations ──────────────────────────────────

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif);;All Files (*)")
        if path:
            self._load_file(path)

    def _load_file(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            QMessageBox.warning(self, "Error", f"Cannot open: {path}")
            return

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        self._current_file = path
        self._title_label.setText(f"Advance Editor — {os.path.basename(path)}")

        self.layers.clear()
        self.history.clear()
        self.layers.add_layer("Background", img)
        self.history.push("Open image", self.layers)

        self._welcome.setVisible(False)
        self._refresh_canvas()
        self._refresh_layers()
        self._update_histogram()
        # Generate filter thumbnails in background
        QTimer.singleShot(500, lambda: self._filters_panel.update_thumbnails(img))
        QTimer.singleShot(100, self.canvas.fit_to_view)
        self._status("Loaded: " + os.path.basename(path))

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "",
            "PNG (*.png);;JPEG (*.jpg);;WebP (*.webp)")
        if path:
            self._export_to(path)

    def _export(self, fmt):
        name = os.path.splitext(os.path.basename(self._current_file or "image"))[0]
        path, _ = QFileDialog.getSaveFileName(self, f"Export {fmt.upper()}", f"{name}.{fmt}",
            f"{fmt.upper()} (*.{fmt})")
        if path:
            self._export_to(path)

    def _export_to(self, path):
        composed = self.layers.compose()
        if composed is None:
            return
        ext = os.path.splitext(path)[1].lower()
        params = []
        if ext in ['.jpg', '.jpeg']:
            params = [cv2.IMWRITE_JPEG_QUALITY, 95]
        elif ext == '.webp':
            params = [cv2.IMWRITE_WEBP_QUALITY, 95]
        cv2.imwrite(path, composed, params)
        self._status(f"Exported: {os.path.basename(path)}")

    # ─── Adjustments ──────────────────────────────────────

    def _on_adjustment(self, name, value):
        if name == "reset":
            layer = self.layers.get_active_layer()
            if layer:
                layer.adjustments.clear()
                layer.invalidate_cache()
                self._refresh_canvas()
            return
        self._adjust_timer.start()

    def _apply_adjustments_now(self):
        layer = self.layers.get_active_layer()
        if not layer:
            return
        values = self._adj_panel.get_all_values()
        for name, val in values.items():
            layer.set_adjustment(name, val)
        self._refresh_canvas()
        self._update_histogram()

    # ─── Curves ───────────────────────────────────────────

    def _on_curve_change(self, curves_dict):
        """Debounced curve change handler."""
        self._curve_timer.start()

    def _apply_curves_now(self):
        layer = self.layers.get_active_layer()
        if not layer:
            return
        curves = self._curves_panel.get_all_curves()
        # Store curves as a special adjustment
        layer.adjustments['_curves'] = curves
        layer.invalidate_cache()
        self._refresh_canvas()
        self._update_histogram()

    # ─── Filters ──────────────────────────────────────────

    def _on_filter_applied(self, preset_name, strength):
        layer = self.layers.get_active_layer()
        if not layer:
            return
        if not preset_name:
            # Remove filter — restore original
            if self._active_filter:
                self._active_filter = None
                self._status("Filter removed")
            return

        img = layer.image.copy()  # Apply filter to original, not cached
        result = FilterProcessor.apply_preset(img, preset_name, strength)
        layer.set_image(result)
        layer.adjustments.clear()
        layer.invalidate_cache()
        self._active_filter = preset_name

        # Reset adjustment sliders
        for s in self._adj_panel.sliders.values():
            if hasattr(s, 'slider'):
                s.slider.blockSignals(True)
                s.reset()
                s.slider.blockSignals(False)
            elif hasattr(s, 'blockSignals'):
                s.blockSignals(True)
                s.setValue(0)
                s.blockSignals(False)
        self._curves_panel.reset_all()

        self.history.push(f"Filter: {preset_name}", self.layers)
        self._refresh_canvas()
        self._refresh_layers()
        self._update_histogram()
        self._status(f"Applied filter: {preset_name} ({strength}%)")

    # ─── Histogram ────────────────────────────────────────

    def _update_histogram(self):
        """Update histogram display in both curves panel and adjustment panel."""
        composed = self.layers.compose()
        if composed is not None:
            hist = ImageProcessor.compute_histogram(composed)
            self._curves_panel.set_histogram(hist)
            try:
                hists = ImageProcessor.compute_rgb_histogram(composed)
                self._adj_panel.update_histogram(hists)
            except Exception:
                pass

    # ─── AI Actions ───────────────────────────────────────


    def _on_ai_action(self, action, params):
        layer = self.layers.get_active_layer()
        if not layer:
            return

        img = layer.get_rendered()

        if action == "erase_start":
            self.canvas.set_brush_mode(True, params.get("size", 20))
            self._status("Paint over the area you want to erase, then click 'Erase Selected Area'")
            return
        elif action == "erase_apply":
            mask = self.canvas.get_brush_mask()
            if mask is not None and np.any(mask > 0):
                self._run_ai("Erase AI", lambda: self.ai.erase_object(img, mask))
                self.canvas.set_brush_mode(False)
            return

        ai_map = {
            "accent": ("Accent AI", lambda: self.ai.auto_enhance(img, params.get("intensity", 50))),
            "sky": ("Sky AI", lambda: self.ai.replace_sky(img, params.get("sky_type", "blue"), params.get("blend", 70))),
            "portrait": ("Portrait AI", lambda: self.ai.portrait_enhance(img, params.get("skin_smooth", 50), params.get("eye_enhance", 30))),
            "bg_blur": ("Background AI", lambda: self.ai.blur_background(img, params.get("amount", 50))),
            "bg_remove": ("Background AI", lambda: self.ai.remove_background(img)),
            "relight": ("Relight AI", lambda: self.ai.relight(img, params.get("direction", 0), params.get("warmth", 50), params.get("intensity", 50))),
            "denoise": ("Noiseless AI", lambda: self.ai.denoise(img, params.get("luminance", 50), params.get("color", 50), params.get("detail", 50))),
            "supersharp": ("Supersharp AI", lambda: self.ai.sharpen(img, params.get("sharpness", 50), params.get("structure", 30))),
            "hdr": ("HDR Merge AI", lambda: HDRMergeAI.apply(img, 50)),
            "lens": ("Lens Correction AI", lambda: LensAI.correct_distortion(img, 50)),
            "style": ("Style Transfer AI", lambda: StyleTransferAI.transfer_color(self._get_reference_image(), img)),
            "wb": ("Auto White Balance", lambda: WhiteBalanceAI.auto_wb(img)),
            "cine_light_pink": ("Cinematic Relight", lambda: self.ai.cinematic_relight(img, color=(255, 50, 200), light_x=0.8, light_y=0.2)),
            "cine_light_cyan": ("Cinematic Relight", lambda: self.ai.cinematic_relight(img, color=(50, 200, 255), light_x=0.2, light_y=0.2)),
            "cine_fog": ("Volumetric Fog", lambda: self.ai.cinematic_fog(img, density=1.0, color=(180, 200, 220))),
        }

        if action in ai_map:
            name, func = ai_map[action]
            self._run_ai(name, func)

    def _get_reference_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Style Reference Image", "", "Images (*.jpg *.png)")
        if path:
            return cv2.imread(path)
        # Return a dummy neutral grey image if none selected to avoid crash
        return np.ones((64,64,3), dtype=np.uint8) * 128

    def _switch_module(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.btn_library.setChecked(index == 0)
        self.btn_develop.setChecked(index == 1)
        
        # Show sync button if we switch back to library and have an active edit
        if index == 0:
            layer = self.layers.get_active_layer()
            if layer and (layer.adjustments or self._active_filter):
                self.library.btn_sync.show()
            else:
                self.library.btn_sync.hide()

    def _sync_edits_to_folder(self):
        layer = self.layers.get_active_layer()
        if not layer:
            return
            
        recipe = Recipe().from_layer(layer, self._active_filter)
        
        # Get list of files from library
        folder = self.library._current_folder
        if not folder:
            return
            
        valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
        try:
            files = [os.path.join(folder, f) for f in os.listdir(folder) 
                     if os.path.splitext(f.lower())[1] in valid_exts]
        except Exception:
            return
            
        if not files:
            return
            
        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder for Synced Images")
        if not out_dir:
            return
            
        self._status("Batch Processing started...")
        self._progress.setVisible(True)
        self._progress.setRange(0, len(files))
        
        self._batch_thread = BatchProcessor(recipe, files, out_dir)
        self._batch_thread.progress.connect(lambda c, t, f: self._update_batch_progress(c, t, f))
        self._batch_thread.finished.connect(self._on_batch_done)
        self._batch_thread.error.connect(lambda f, e: log.error(f"Batch error on {f}: {e}"))
        self._batch_thread.start()
        
    def _update_batch_progress(self, current, total, filename):
        self._progress.setValue(current)
        self._status(f"Processing ({current}/{total}): {filename}")
        
    def _on_batch_done(self):
        self._progress.setVisible(False)
        self._status("Batch Processing completed!")
        QMessageBox.information(self, "Sync Complete", "Successfully applied edits to all photos.")

    def _load_from_library(self, filepath):
        self._switch_module(1)
        self._load_file(filepath)

    def _run_ai(self, name, func):
        self._status(f"Processing {name}...")
        self._progress.setVisible(True)
        self._progress.setRange(0, 0)
        self.canvas.show_ai_processing(name)

        self._worker = AIWorker(func)
        self._worker.finished.connect(lambda result: self._on_ai_done(name, result))
        self._worker.error.connect(lambda err: self._on_ai_error(name, err))
        self._worker.start()

    def _on_ai_done(self, name, result):
        self._progress.setVisible(False)
        self.canvas.hide_ai_processing()
        if result is None:
            self._status(f"{name}: No result")
            return

        layer = self.layers.get_active_layer()
        if layer:
            # Handle 4-channel (BGRA) results from background removal
            if len(result.shape) == 3 and result.shape[2] == 4:
                result = cv2.cvtColor(result, cv2.COLOR_BGRA2BGR)

            layer.set_image(result)
            layer.adjustments.clear()
            layer.invalidate_cache()

            # Reset sliders
            for s in self._adj_panel.sliders.values():
                if hasattr(s, 'slider'):
                    s.slider.blockSignals(True)
                    s.reset()
                    s.slider.blockSignals(False)
                elif hasattr(s, 'blockSignals'):
                    s.blockSignals(True)
                    s.setValue(0)
                    s.blockSignals(False)

            self.history.push(f"Apply {name}", self.layers)
            self._refresh_canvas()
            self._refresh_layers()
        self._status(f"{name} applied successfully")

    def _on_ai_error(self, name, err):
        self._progress.setVisible(False)
        self.canvas.hide_ai_processing()
        self._status(f"{name} error: {err}")
        QMessageBox.warning(self, f"{name} Error", str(err))

    # ─── Copilot Actions ──────────────────────────────────
    
    def _on_copilot_request_image(self):
        layer = self.layers.get_active_layer()
        if layer:
            self._copilot_panel.receive_image(layer.get_rendered())
        else:
            self._copilot_panel.receive_image(None)
            
    def _on_copilot_execute(self, tool, value_str):
        if tool == "apply_ai":
            self._on_ai_action(value_str, {})
            return
            
        try:
            val = float(value_str)
        except:
            return
            
        # Update slider in UI directly (this will trigger adjustment_changed and re-render)
        if tool in self._adj_panel.sliders:
            slider = self._adj_panel.sliders[tool]
            # Need to map values depending on the slider's range, but for now we assume Copilot uses the actual slider values [-100, 100]
            if hasattr(slider, 'set_value'):
                slider.set_value(val)
            elif hasattr(slider, 'setValue'):
                slider.setValue(int(val))

    # ─── Layer Actions ────────────────────────────────────

    def _on_layer_action(self, action, param):
        if action == "select":
            self.layers.set_active_layer(param)
            self._refresh_layers()
            self._load_layer_adjustments()
        elif action == "add":
            layer = self.layers.get_active_layer()
            if layer:
                h, w = layer.image.shape[:2]
                blank = np.ones((h, w, 3), dtype=np.uint8) * 128
                self.layers.add_layer(f"Layer {len(self.layers.layers)}", blank)
                self.history.push("Add layer", self.layers)
                self._refresh_layers()
        elif action == "duplicate":
            layer = self.layers.get_active_layer()
            if layer:
                self.layers.duplicate_layer(layer.id)
                self.history.push("Duplicate layer", self.layers)
                self._refresh_layers()
        elif action == "delete":
            layer = self.layers.get_active_layer()
            if layer and len(self.layers.layers) > 1:
                self.layers.remove_layer(layer.id)
                self.history.push("Delete layer", self.layers)
                self._refresh_canvas()
                self._refresh_layers()
        elif action == "up":
            layer = self.layers.get_active_layer()
            if layer:
                self.layers.move_layer(layer.id, 1)
                self._refresh_canvas()
                self._refresh_layers()
        elif action == "down":
            layer = self.layers.get_active_layer()
            if layer:
                self.layers.move_layer(layer.id, -1)
                self._refresh_canvas()
                self._refresh_layers()
        elif action == "visibility":
            layer = self.layers.get_layer(param)
            if layer:
                layer.visible = not layer.visible
                self._refresh_canvas()
                self._refresh_layers()
        elif action == "blend_mode":
            layer = self.layers.get_active_layer()
            if layer:
                layer.blend_mode = param
                self._refresh_canvas()
        elif action == "opacity":
            layer = self.layers.get_active_layer()
            if layer:
                layer.opacity = int(param)
                self._refresh_canvas()
        elif action == "flatten":
            self._flatten_layers()

    def _load_layer_adjustments(self):
        layer = self.layers.get_active_layer()
        if not layer:
            return
        for name, slider in self._adj_panel.sliders.items():
            val = layer.adjustments.get(name, 0)
            if hasattr(slider, 'slider'):
                slider.slider.blockSignals(True)
                slider.slider.setValue(val)
                slider.val_label.setText(str(val))
                slider.slider.blockSignals(False)
            elif hasattr(slider, 'blockSignals'):
                slider.blockSignals(True)
                slider.setValue(val)
                slider.blockSignals(False)

    # ─── Transforms ───────────────────────────────────────

    def _transform(self, action):
        layer = self.layers.get_active_layer()
        if not layer:
            return
        img = layer.get_rendered()
        if action == "rotate_cw":
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif action == "rotate_ccw":
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif action == "flip_h":
            img = ImageProcessor.flip_horizontal(img)
        elif action == "flip_v":
            img = ImageProcessor.flip_vertical(img)
        layer.set_image(img)
        layer.adjustments.clear()
        self.history.push(f"Transform: {action}", self.layers)
        self._refresh_canvas()

    # ─── Undo / Redo ─────────────────────────────────────

    def _undo(self):
        if self.history.undo(self.layers):
            self._refresh_canvas()
            self._refresh_layers()
            self._load_layer_adjustments()
            self._status("Undo")

    def _redo(self):
        if self.history.redo(self.layers):
            self._refresh_canvas()
            self._refresh_layers()
            self._load_layer_adjustments()
            self._status("Redo")

    def _flatten_layers(self):
        result = self.layers.flatten()
        if result is not None:
            self.history.push("Flatten layers", self.layers)
            self._refresh_canvas()
            self._refresh_layers()

    # ─── Helpers ──────────────────────────────────────────

    def _refresh_canvas(self):
        composed = self.layers.compose()
        if composed is not None:
            self.canvas.set_image(composed)

    def _refresh_layers(self):
        self._layer_panel.update_layers(self.layers.layers, self.layers.active_layer_id)

    def _show_welcome(self):
        self._welcome.setVisible(True)

    def _select_tool(self, name):
        for n, btn in self._tools.items():
            btn.setChecked(n == name)
        if name == "brush":
            self.canvas.set_brush_mode(True)
        else:
            self.canvas.set_brush_mode(False)

    def _zoom_in(self):
        self.canvas.set_zoom(self.canvas.get_zoom() * 1.25)

    def _zoom_out(self):
        self.canvas.set_zoom(self.canvas.get_zoom() / 1.25)

    def _fit_view(self):
        self.canvas.fit_to_view()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _status(self, msg):
        self._status_label.setText(msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_welcome'):
            self._welcome.setGeometry(self.canvas.geometry())

    # ─── Window Dragging ──────────────────────────────────

    def mousePressEvent(self, event):
        if event.position().y() < 40:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, '_drag_pos') and self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            if event.position().y() < 40 or self._drag_pos:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.position().y() < 40:
            self._toggle_maximize()
