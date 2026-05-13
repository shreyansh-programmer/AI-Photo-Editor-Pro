"""
Advance Editor — Interactive Tone Curves Widget
Professional curve editor like Adobe Lightroom Classic.
Supports RGB composite + individual R, G, B channel curves.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QLinearGradient, QImage, QPixmap
import numpy as np


class CurveEditor(QWidget):
    """Interactive bezier tone curve editor."""
    curve_changed = pyqtSignal(str, list)  # channel, points

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(280, 200)
        self.setMaximumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMouseTracking(True)

        # Channel curves: each is a list of (x, y) normalized [0,1]
        self._curves = {
            'rgb': [(0.0, 0.0), (1.0, 1.0)],
            'red': [(0.0, 0.0), (1.0, 1.0)],
            'green': [(0.0, 0.0), (1.0, 1.0)],
            'blue': [(0.0, 0.0), (1.0, 1.0)],
        }
        self._active_channel = 'rgb'
        self._dragging_point = -1
        self._hover_point = -1
        self._histogram = None

        # Colors per channel
        self._channel_colors = {
            'rgb': QColor(220, 220, 220),
            'red': QColor(239, 68, 68),
            'green': QColor(34, 197, 94),
            'blue': QColor(96, 165, 250),
        }

    def set_channel(self, channel):
        self._active_channel = channel
        self.update()

    def get_channel(self):
        return self._active_channel

    def set_histogram(self, histogram_data):
        """Set histogram data for background display. histogram_data: 256 values."""
        self._histogram = histogram_data
        self.update()

    def get_curve_points(self, channel=None):
        ch = channel or self._active_channel
        return list(self._curves[ch])

    def get_all_curves(self):
        return {ch: list(pts) for ch, pts in self._curves.items()}

    def reset_channel(self, channel=None):
        ch = channel or self._active_channel
        self._curves[ch] = [(0.0, 0.0), (1.0, 1.0)]
        self.curve_changed.emit(ch, self._curves[ch])
        self.update()

    def reset_all(self):
        for ch in self._curves:
            self._curves[ch] = [(0.0, 0.0), (1.0, 1.0)]
        self.curve_changed.emit('rgb', self._curves['rgb'])
        self.update()

    def _get_curve_rect(self):
        m = 8  # margin
        return QRectF(m, m, self.width() - 2 * m, self.height() - 2 * m)

    def _to_widget(self, nx, ny):
        r = self._get_curve_rect()
        return QPointF(r.x() + nx * r.width(), r.y() + (1.0 - ny) * r.height())

    def _from_widget(self, pos):
        r = self._get_curve_rect()
        nx = max(0, min(1, (pos.x() - r.x()) / r.width()))
        ny = max(0, min(1, 1.0 - (pos.y() - r.y()) / r.height()))
        return nx, ny

    def _interpolate_curve(self, points, num_samples=256):
        """Cubic spline interpolation of curve points."""
        if len(points) < 2:
            return np.linspace(0, 255, 256)

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        try:
            from scipy.interpolate import CubicSpline
            cs = CubicSpline(xs, ys, bc_type='clamped')
            x_out = np.linspace(0, 1, num_samples)
            y_out = np.clip(cs(x_out), 0, 1)
        except Exception:
            x_out = np.linspace(0, 1, num_samples)
            y_out = np.interp(x_out, xs, ys)

        return y_out

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self._get_curve_rect()

        # Background
        p.fillRect(self.rect(), QColor(12, 12, 15))

        # Draw histogram if available
        if self._histogram is not None:
            max_val = self._histogram.max() if self._histogram.max() > 0 else 1
            hist_color = QColor(255, 255, 255, 15)
            for i in range(min(256, len(self._histogram))):
                x = r.x() + (i / 255.0) * r.width()
                h = (self._histogram[i] / max_val) * r.height() * 0.8
                p.fillRect(QRectF(x, r.bottom() - h, max(1, r.width() / 256), h), hist_color)

        # Grid lines
        grid_pen = QPen(QColor(255, 255, 255, 12), 1)
        p.setPen(grid_pen)
        for i in range(1, 4):
            t = i / 4.0
            x = r.x() + t * r.width()
            y = r.y() + t * r.height()
            p.drawLine(QPointF(x, r.y()), QPointF(x, r.bottom()))
            p.drawLine(QPointF(r.x(), y), QPointF(r.right(), y))

        # Diagonal reference line
        ref_pen = QPen(QColor(255, 255, 255, 20), 1, Qt.PenStyle.DashLine)
        p.setPen(ref_pen)
        p.drawLine(QPointF(r.x(), r.bottom()), QPointF(r.right(), r.y()))

        # Draw inactive channel curves
        for ch in ['red', 'green', 'blue']:
            if ch != self._active_channel and self._active_channel == 'rgb':
                continue
            if ch == self._active_channel:
                continue
            pts = self._curves[ch]
            if len(pts) >= 2:
                y_vals = self._interpolate_curve(pts)
                path = QPainterPath()
                first = self._to_widget(0, y_vals[0])
                path.moveTo(first)
                for i in range(1, 256):
                    pt = self._to_widget(i / 255.0, y_vals[i])
                    path.lineTo(pt)
                color = QColor(self._channel_colors[ch])
                color.setAlpha(40)
                p.setPen(QPen(color, 1))
                p.drawPath(path)

        # Draw active channel curve
        pts = self._curves[self._active_channel]
        y_vals = self._interpolate_curve(pts)
        path = QPainterPath()
        first = self._to_widget(0, y_vals[0])
        path.moveTo(first)
        for i in range(1, 256):
            pt = self._to_widget(i / 255.0, y_vals[i])
            path.lineTo(pt)

        color = self._channel_colors[self._active_channel]
        p.setPen(QPen(color, 2))
        p.drawPath(path)

        # Draw control points
        for i, (px, py) in enumerate(pts):
            center = self._to_widget(px, py)
            radius = 6 if i == self._hover_point else 5

            if i == self._dragging_point:
                p.setBrush(QBrush(color))
                p.setPen(QPen(QColor(255, 255, 255), 2))
            elif i == self._hover_point:
                p.setBrush(QBrush(QColor(40, 40, 45)))
                p.setPen(QPen(color, 2))
            else:
                p.setBrush(QBrush(QColor(20, 20, 24)))
                p.setPen(QPen(color, 1.5))

            p.drawEllipse(center, radius, radius)

        # Border
        p.setPen(QPen(QColor(255, 255, 255, 8), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(r, 4, 4)

        p.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pts = self._curves[self._active_channel]
        nx, ny = self._from_widget(event.position())

        # Check if clicking near existing point
        for i, (px, py) in enumerate(pts):
            wp = self._to_widget(px, py)
            if (event.position() - wp).manhattanLength() < 15:
                self._dragging_point = i
                return

        # Add new point (insert in sorted x order)
        new_pt = (nx, ny)
        insert_idx = 0
        for i, (px, _) in enumerate(pts):
            if nx > px:
                insert_idx = i + 1
        pts.insert(insert_idx, new_pt)
        self._dragging_point = insert_idx
        self.curve_changed.emit(self._active_channel, pts)
        self.update()

    def mouseMoveEvent(self, event):
        pts = self._curves[self._active_channel]

        if self._dragging_point >= 0:
            nx, ny = self._from_widget(event.position())
            idx = self._dragging_point

            # First and last points can only move vertically
            if idx == 0:
                nx = 0.0
            elif idx == len(pts) - 1:
                nx = 1.0
            else:
                # Constrain between neighbors
                nx = max(pts[idx - 1][0] + 0.01, min(pts[idx + 1][0] - 0.01, nx))

            pts[idx] = (nx, ny)
            self.curve_changed.emit(self._active_channel, pts)
            self.update()
            return

        # Hover detection
        old_hover = self._hover_point
        self._hover_point = -1
        for i, (px, py) in enumerate(pts):
            wp = self._to_widget(px, py)
            if (event.position() - wp).manhattanLength() < 15:
                self._hover_point = i
                break
        if old_hover != self._hover_point:
            self.update()

    def mouseReleaseEvent(self, event):
        if self._dragging_point >= 0:
            self._dragging_point = -1
            self.update()

    def mouseDoubleClickEvent(self, event):
        """Double-click to remove a point (except endpoints)."""
        pts = self._curves[self._active_channel]
        for i, (px, py) in enumerate(pts):
            wp = self._to_widget(px, py)
            if (event.position() - wp).manhattanLength() < 15:
                if 0 < i < len(pts) - 1:
                    pts.pop(i)
                    self._dragging_point = -1
                    self._hover_point = -1
                    self.curve_changed.emit(self._active_channel, pts)
                    self.update()
                return


class CurvesPanel(QWidget):
    """Complete curves panel with channel selector and curve editor."""
    curve_changed = pyqtSignal(dict)  # all curves

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Channel selector
        ch_layout = QHBoxLayout()
        ch_layout.setSpacing(4)
        self._channel_btns = {}
        channels = [
            ('rgb', 'RGB', '#d4d4d8'),
            ('red', 'R', '#ef4444'),
            ('green', 'G', '#22c55e'),
            ('blue', 'B', '#60a5fa'),
        ]
        for ch, label, color in channels:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(ch == 'rgb')
            btn.setFixedSize(40, 28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.03);
                    border: 1px solid transparent;
                    border-radius: 6px;
                    color: #52525b;
                    font-weight: 700;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background: rgba({self._hex_to_rgba(color, 0.12)});
                    border-color: rgba({self._hex_to_rgba(color, 0.3)});
                    color: {color};
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.05);
                    color: {color};
                }}
            """)
            btn.clicked.connect(lambda c, ch=ch: self._set_channel(ch))
            ch_layout.addWidget(btn)
            self._channel_btns[ch] = btn
        ch_layout.addStretch()

        # Reset button
        reset_btn = QPushButton("↺")
        reset_btn.setFixedSize(28, 28)
        reset_btn.setToolTip("Reset curve")
        reset_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 6px; color: #52525b; font-size: 14px; }
            QPushButton:hover { color: #a1a1aa; background: rgba(255,255,255,0.06); }
        """)
        reset_btn.clicked.connect(self._reset_curve)
        ch_layout.addWidget(reset_btn)
        layout.addLayout(ch_layout)

        # Curve editor
        self.editor = CurveEditor()
        self.editor.curve_changed.connect(self._on_curve_change)
        layout.addWidget(self.editor)

        # Info label
        self._info = QLabel("Click to add points · Double-click to remove · Drag to adjust")
        self._info.setStyleSheet("color: #3f3f46; font-size: 10px; padding: 4px 0 0 0;")
        self._info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._info)

    def _hex_to_rgba(self, hex_color, alpha):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r},{g},{b},{alpha}"

    def _set_channel(self, ch):
        for name, btn in self._channel_btns.items():
            btn.setChecked(name == ch)
        self.editor.set_channel(ch)

    def _on_curve_change(self, channel, points):
        self.curve_changed.emit(self.editor.get_all_curves())

    def _reset_curve(self):
        self.editor.reset_channel()
        self.curve_changed.emit(self.editor.get_all_curves())

    def get_all_curves(self):
        return self.editor.get_all_curves()

    def set_histogram(self, data):
        self.editor.set_histogram(data)

    def reset_all(self):
        self.editor.reset_all()
