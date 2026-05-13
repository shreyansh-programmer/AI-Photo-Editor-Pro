"""
Advance Editor - Right Panel Widgets
Adjustment sliders, AI tools panel, Layer panel.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QPushButton, QComboBox, QScrollArea, QFrame, QSizePolicy,
    QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal


class SliderControl(QWidget):
    """Custom labeled slider with value display."""
    value_changed = pyqtSignal(str, int)

    def __init__(self, name, label, min_val=-100, max_val=100, default=0, parent=None):
        super().__init__(parent)
        self.name = name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setObjectName("sliderLabel")
        lbl.setFixedWidth(85)
        layout.addWidget(lbl)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.valueChanged.connect(self._on_change)
        layout.addWidget(self.slider, 1)

        self.val_label = QLabel(str(default))
        self.val_label.setObjectName("sliderValue")
        self.val_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.val_label.setFixedWidth(35)
        layout.addWidget(self.val_label)

    def _on_change(self, v):
        self.val_label.setText(str(v))
        self.value_changed.emit(self.name, v)

    def reset(self):
        self.slider.setValue(0)

    def get_value(self):
        return self.slider.value()


class CollapsibleSection(QWidget):
    """Collapsible panel section."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._btn = QPushButton(f"▸  {title}")
        self._btn.setObjectName("sectionHeader")
        self._btn.clicked.connect(self._toggle)
        self._layout.addWidget(self._btn)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 4, 0, 8)
        self._content_layout.setSpacing(2)
        self._content.setVisible(False)
        self._layout.addWidget(self._content)
        self._expanded = False
        self._title = title

    def _toggle(self):
        self._expanded = not self._expanded
        self._content.setVisible(self._expanded)
        arrow = "▾" if self._expanded else "▸"
        self._btn.setText(f"{arrow}  {self._title}")

    def add_widget(self, widget):
        self._content_layout.addWidget(widget)

    def expand(self):
        if not self._expanded:
            self._toggle()


class HistogramWidget(QWidget):
    """Live RGB + Luminance histogram (drawn in-widget)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self._hists = None

    def update_histogram(self, hists):
        self._hists = hists
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor, QPen
        from PyQt6.QtCore import QRect
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor(10, 4, 7))

        if not self._hists:
            painter.end()
            return

        channel_colors = [
            ('luma',  QColor(255, 255, 255, 40)),
            ('r',     QColor(255,  80, 120, 80)),
            ('g',     QColor( 80, 220, 130, 80)),
            ('b',     QColor( 80, 140, 255, 80)),
        ]
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF
        for ch, color in channel_colors:
            vals = self._hists.get(ch)
            if vals is None:
                continue
            pts = [QPointF(0, h)]
            for i, v in enumerate(vals):
                x = i * w / 255
                y = h - v * (h - 2)
                pts.append(QPointF(x, y))
            pts.append(QPointF(w, h))
            poly = QPolygonF(pts)
            painter.setBrush(color)
            painter.setPen(QPen(color.lighter(130), 0.5))
            painter.drawPolygon(poly)
        painter.end()


class AdjustmentPanel(QScrollArea):
    """Full Lightroom-equivalent Develop panel with all sliders."""
    adjustment_changed = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self.sliders = {}

        # ─ Histogram ─
        self.histogram = HistogramWidget()
        layout.addWidget(self.histogram)

        # ─ Light ─
        light = CollapsibleSection("☀  Light")
        for name, label, mn, mx in [
            ("exposure",   "Exposure",   -100, 100),
            ("brightness", "Brightness", -100, 100),
            ("contrast",   "Contrast",   -100, 100),
            ("highlights", "Highlights", -100, 100),
            ("shadows",    "Shadows",    -100, 100),
            ("whites",     "Whites",     -100, 100),
            ("blacks",     "Blacks",     -100, 100),
        ]:
            s = SliderControl(name, label, mn, mx)
            s.value_changed.connect(self.adjustment_changed.emit)
            light.add_widget(s)
            self.sliders[name] = s
        light.expand()
        layout.addWidget(light)

        # ─ Color ─
        color = CollapsibleSection("🎨  Color")
        for name, label, mn, mx in [
            ("temperature", "Temp",       -100, 100),
            ("tint",        "Tint",       -100, 100),
            ("vibrance",    "Vibrance",   -100, 100),
            ("saturation",  "Saturation", -100, 100),
            ("hue",         "Hue",        -180, 180),
        ]:
            s = SliderControl(name, label, mn, mx)
            s.value_changed.connect(self.adjustment_changed.emit)
            color.add_widget(s)
            self.sliders[name] = s
        layout.addWidget(color)

        # ─ HSL / Color Mixer ─
        hsl = CollapsibleSection("🌈  HSL / Color Mixer")
        hsl_colors = [
            ("Red",    15),  ("Orange", 25), ("Yellow", 45),
            ("Green",  75),  ("Aqua",  105), ("Blue",   120),
            ("Purple", 150), ("Magenta",165),
        ]
        for color_name, target_hue in hsl_colors:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(8, 0, 8, 0)
            lbl = QLabel(color_name)
            lbl.setObjectName("sliderLabel")
            lbl.setFixedWidth(60)
            rl.addWidget(lbl)
            # Hue, Sat, Lum sliders for this color
            for suffix, signal_name in [(" H", f"hsl_h_{color_name.lower()}"),
                                        (" S", f"hsl_s_{color_name.lower()}"),
                                        (" L", f"hsl_l_{color_name.lower()}")]:
                s = QSlider(Qt.Orientation.Horizontal)
                s.setRange(-100, 100)
                s.setValue(0)
                s.setFixedWidth(55)
                name_str = signal_name
                s.valueChanged.connect(lambda v, n=name_str: self.adjustment_changed.emit(n, v))
                rl.addWidget(s)
                self.sliders[signal_name] = s
            hsl.add_widget(row)
        layout.addWidget(hsl)

        # ─ Detail ─
        detail = CollapsibleSection("🔬  Detail")
        for name, label, mn, mx in [
            ("texture",          "Texture",       -100, 100),
            ("clarity",          "Clarity",        -100, 100),
            ("dehaze",           "Dehaze",          0,   100),
            ("sharpen",          "Sharpen",         0,   100),
            ("noise_reduction",  "Lum. Noise",      0,   100),
            ("color_noise",      "Color Noise",     0,   100),
            ("grain",            "Grain",           0,   100),
        ]:
            s = SliderControl(name, label, mn, mx)
            s.value_changed.connect(self.adjustment_changed.emit)
            detail.add_widget(s)
            self.sliders[name] = s
        layout.addWidget(detail)

        # ─ Effects ─
        effects = CollapsibleSection("✨  Effects")
        for name, label, mn, mx in [
            ("vignette", "Vignette",  0, 100),
            ("grain",    "Grain",     0, 100),
        ]:
            if name not in self.sliders:
                s = SliderControl(name, label, mn, mx)
                s.value_changed.connect(self.adjustment_changed.emit)
                effects.add_widget(s)
                self.sliders[name] = s
        layout.addWidget(effects)

        # ─ Split Toning ─
        split = CollapsibleSection("🌓  Split Toning")
        for name, label, mn, mx, default in [
            ("split_hi_hue",  "Hi Hue",   0, 360, 40),
            ("split_hi_sat",  "Hi Sat",   0, 100, 0),
            ("split_lo_hue",  "Lo Hue",   0, 360, 220),
            ("split_lo_sat",  "Lo Sat",   0, 100, 0),
            ("split_balance", "Balance", -100, 100, 0),
        ]:
            s = SliderControl(name, label, mn, mx, default)
            s.value_changed.connect(self.adjustment_changed.emit)
            split.add_widget(s)
            self.sliders[name] = s
        layout.addWidget(split)

        # ─ Transform ─
        transform = CollapsibleSection("📐  Transform")
        for name, label, mn, mx in [
            ("rotate",               "Straighten",  -45, 45),
            ("perspective_vertical", "Vert. Persp", -100, 100),
            ("perspective_horizontal", "Horiz. Persp", -100, 100),
        ]:
            s = SliderControl(name, label, mn, mx)
            s.value_changed.connect(self.adjustment_changed.emit)
            transform.add_widget(s)
            self.sliders[name] = s
        layout.addWidget(transform)

        # ─ Reset ─
        reset_btn = QPushButton("↺  Reset All Adjustments")
        reset_btn.clicked.connect(self.reset_all)
        layout.addWidget(reset_btn)

        layout.addStretch()
        self.setWidget(container)

    def reset_all(self):
        for s in self.sliders.values():
            if hasattr(s, 'slider'):
                s.slider.blockSignals(True)
                s.reset()
                s.slider.blockSignals(False)
            elif hasattr(s, 'blockSignals'):
                s.blockSignals(True)
                s.setValue(0)
                s.blockSignals(False)
        self.adjustment_changed.emit("reset", 0)

    def update_histogram(self, hists):
        self.histogram.update_histogram(hists)

    def get_all_values(self):
        result = {}
        for name, s in self.sliders.items():
            if hasattr(s, 'get_value'):
                result[name] = s.get_value()
            elif hasattr(s, 'value'):
                result[name] = s.value()
        return result


class AIToolsPanel(QScrollArea):
    """Panel with all AI tool buttons and controls."""
    ai_action = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Advanced AI Section
        sec = CollapsibleSection("🌟  Advanced AI (Pro)")
        btn = QPushButton("🌄  HDR Merge (Single Image)")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("hdr", {}))
        sec.add_widget(btn)
        
        btn = QPushButton("🔍  Lens Correction")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("lens", {}))
        sec.add_widget(btn)

        btn = QPushButton("🎨  Style Transfer (Match Color)")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("style", {}))
        sec.add_widget(btn)
        
        btn = QPushButton("⚖  Auto White Balance")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("wb", {}))
        sec.add_widget(btn)
        
        layout.addWidget(sec)

        # Cinematic Studio AI
        sec = CollapsibleSection("🎬  Cinematic Studio AI (3D)")
        btn = QPushButton("🔴  3D Point Light (Neon Pink)")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("cine_light_pink", {}))
        sec.add_widget(btn)
        
        btn = QPushButton("🔵  3D Point Light (Cyan)")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("cine_light_cyan", {}))
        sec.add_widget(btn)

        btn = QPushButton("🌫️  Volumetric 3D Fog")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("cine_fog", {}))
        sec.add_widget(btn)
        
        layout.addWidget(sec)

        # Accent AI
        sec = CollapsibleSection("✦  Accent AI — Auto Enhance")
        self._accent_slider = SliderControl("accent_intensity", "Intensity", 0, 100, 50)
        sec.add_widget(self._accent_slider)
        btn = QPushButton("⚡  Apply Auto Enhance")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("accent", {"intensity": self._accent_slider.get_value()}))
        sec.add_widget(btn)
        sec.expand()
        layout.addWidget(sec)

        # Sky AI
        sec = CollapsibleSection("☁  Sky AI — Sky Replacement")
        self._sky_type = QComboBox()
        self._sky_type.addItems(["blue", "sunset", "golden", "stormy", "night", "aurora"])
        sec.add_widget(self._sky_type)
        self._sky_blend = SliderControl("sky_blend", "Blend", 0, 100, 70)
        sec.add_widget(self._sky_blend)
        btn = QPushButton("🌅  Replace Sky")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("sky", {
            "sky_type": self._sky_type.currentText(),
            "blend": self._sky_blend.get_value()
        }))
        sec.add_widget(btn)
        layout.addWidget(sec)

        # Portrait AI
        sec = CollapsibleSection("👤  Portrait AI — Enhancement")
        self._skin_smooth = SliderControl("skin_smooth", "Skin Smooth", 0, 100, 40)
        self._eye_enhance = SliderControl("eye_enhance", "Eye Enhance", 0, 100, 30)
        sec.add_widget(self._skin_smooth)
        sec.add_widget(self._eye_enhance)
        btn = QPushButton("✨  Enhance Portrait")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("portrait", {
            "skin_smooth": self._skin_smooth.get_value(),
            "eye_enhance": self._eye_enhance.get_value()
        }))
        sec.add_widget(btn)
        layout.addWidget(sec)

        # Background AI
        sec = CollapsibleSection("🖼  Background AI")
        self._bg_blur = SliderControl("bg_blur", "Blur Amount", 0, 100, 50)
        sec.add_widget(self._bg_blur)
        btn1 = QPushButton("🔲  Blur Background")
        btn1.setObjectName("aiButton")
        btn1.clicked.connect(lambda: self.ai_action.emit("bg_blur", {"amount": self._bg_blur.get_value()}))
        sec.add_widget(btn1)
        btn2 = QPushButton("✂  Remove Background")
        btn2.setObjectName("aiButton")
        btn2.clicked.connect(lambda: self.ai_action.emit("bg_remove", {}))
        sec.add_widget(btn2)
        layout.addWidget(sec)

        # Relight AI
        sec = CollapsibleSection("💡  Relight AI")
        self._light_dir = SliderControl("light_dir", "Direction", 0, 360, 0)
        self._light_warmth = SliderControl("light_warmth", "Warmth", 0, 100, 50)
        self._light_intensity = SliderControl("light_intensity", "Intensity", 0, 100, 50)
        sec.add_widget(self._light_dir)
        sec.add_widget(self._light_warmth)
        sec.add_widget(self._light_intensity)
        btn = QPushButton("💡  Apply Relighting")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("relight", {
            "direction": self._light_dir.get_value(),
            "warmth": self._light_warmth.get_value(),
            "intensity": self._light_intensity.get_value()
        }))
        sec.add_widget(btn)
        layout.addWidget(sec)

        # Noiseless AI
        sec = CollapsibleSection("🔇  Noiseless AI — Denoise")
        self._denoise_lum = SliderControl("denoise_lum", "Luminance", 0, 100, 50)
        self._denoise_col = SliderControl("denoise_col", "Color", 0, 100, 50)
        self._denoise_det = SliderControl("denoise_det", "Detail", 0, 100, 50)
        sec.add_widget(self._denoise_lum)
        sec.add_widget(self._denoise_col)
        sec.add_widget(self._denoise_det)
        btn = QPushButton("🔇  Apply Denoise")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("denoise", {
            "luminance": self._denoise_lum.get_value(),
            "color": self._denoise_col.get_value(),
            "detail": self._denoise_det.get_value()
        }))
        sec.add_widget(btn)
        layout.addWidget(sec)

        # Supersharp AI
        sec = CollapsibleSection("🔍  Supersharp AI")
        self._sharp_amt = SliderControl("sharp_amt", "Sharpness", 0, 100, 50)
        self._sharp_str = SliderControl("sharp_str", "Structure", 0, 100, 30)
        sec.add_widget(self._sharp_amt)
        sec.add_widget(self._sharp_str)
        btn = QPushButton("🔍  Apply Supersharp")
        btn.setObjectName("aiButton")
        btn.clicked.connect(lambda: self.ai_action.emit("supersharp", {
            "sharpness": self._sharp_amt.get_value(),
            "structure": self._sharp_str.get_value()
        }))
        sec.add_widget(btn)
        layout.addWidget(sec)

        # Erase AI
        sec = CollapsibleSection("🧹  Erase AI — Object Removal")
        self._erase_size = SliderControl("erase_size", "Brush Size", 5, 100, 20)
        sec.add_widget(self._erase_size)
        btn_start = QPushButton("🖌  Paint Area to Erase")
        btn_start.setObjectName("aiButton")
        btn_start.clicked.connect(lambda: self.ai_action.emit("erase_start", {
            "size": self._erase_size.get_value()
        }))
        sec.add_widget(btn_start)
        btn_apply = QPushButton("🧹  Erase Selected Area")
        btn_apply.setObjectName("aiButton")
        btn_apply.clicked.connect(lambda: self.ai_action.emit("erase_apply", {}))
        sec.add_widget(btn_apply)
        layout.addWidget(sec)

        layout.addStretch()
        self.setWidget(container)


class LayerPanel(QScrollArea):
    """Layer management panel."""
    layer_action = pyqtSignal(str, str)  # action, layer_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(4)

        # Toolbar
        toolbar = QHBoxLayout()
        for action, icon, tip in [
            ("add", "+", "Add Layer"), ("duplicate", "⧉", "Duplicate"),
            ("delete", "✕", "Delete"), ("up", "↑", "Move Up"),
            ("down", "↓", "Move Down"), ("flatten", "⊟", "Flatten"),
        ]:
            btn = QPushButton(icon)
            btn.setToolTip(tip)
            btn.setFixedSize(32, 28)
            btn.clicked.connect(lambda checked, a=action: self.layer_action.emit(a, ""))
            toolbar.addWidget(btn)
        toolbar.addStretch()
        self._layout.addLayout(toolbar)

        # Blend mode
        blend_layout = QHBoxLayout()
        blend_layout.addWidget(QLabel("Blend:"))
        self._blend_combo = QComboBox()
        self._blend_combo.addItems([
            "normal", "multiply", "screen", "overlay", "soft_light",
            "hard_light", "color_dodge", "color_burn", "difference"
        ])
        self._blend_combo.currentTextChanged.connect(
            lambda t: self.layer_action.emit("blend_mode", t))
        blend_layout.addWidget(self._blend_combo, 1)
        self._layout.addLayout(blend_layout)

        # Opacity
        self._opacity = SliderControl("opacity", "Opacity", 0, 100, 100)
        self._opacity.value_changed.connect(
            lambda n, v: self.layer_action.emit("opacity", str(v)))
        self._layout.addWidget(self._opacity)

        # Layer list area
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 4, 0, 0)
        self._list_layout.setSpacing(2)
        self._list_layout.addStretch()
        self._layout.addWidget(self._list_widget)

        self._layout.addStretch()
        self.setWidget(self._container)

    def update_layers(self, layers, active_id):
        """Refresh layer list."""
        # Clear existing
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for layer in reversed(layers):
            item = QWidget()
            item.setObjectName("layerItemActive" if layer.id == active_id else "layerItem")
            item.setFixedHeight(36)
            h = QHBoxLayout(item)
            h.setContentsMargins(8, 4, 8, 4)

            vis = QCheckBox()
            vis.setChecked(layer.visible)
            vis.stateChanged.connect(
                lambda s, lid=layer.id: self.layer_action.emit("visibility", lid))
            h.addWidget(vis)

            name = QPushButton(layer.name)
            name.setFlat(True)
            name.setStyleSheet("text-align: left; color: #e4e4e7; border: none; padding: 2px 4px;")
            name.clicked.connect(
                lambda checked, lid=layer.id: self.layer_action.emit("select", lid))
            h.addWidget(name, 1)

            self._list_layout.insertWidget(self._list_layout.count() - 1, item)
