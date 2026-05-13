"""
Advance Editor - Canvas Widget
Zoomable, pannable image viewport with checkerboard transparency background.
"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QPainter, QImage, QPixmap, QColor, QBrush, QPen, 
                          QWheelEvent, QFont, QConicalGradient, QRadialGradient)
import numpy as np
import cv2


class CanvasWidget(QWidget):
    """Image canvas with zoom, pan, and brush painting support."""

    zoom_changed = pyqtSignal(float)
    cursor_pos_changed = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("canvasArea")
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._image = None
        self._qimage = None
        self._pixmap = None
        self._zoom = 1.0
        self._pan_offset = QPoint(0, 0)
        self._panning = False
        self._pan_start = QPoint(0, 0)
        self._min_zoom = 0.05
        self._max_zoom = 16.0

        # Brush tool state
        self._brush_active = False
        self._brush_size = 20
        self._brush_painting = False
        self._brush_mask = None
        self.on_brush_stroke = None  # Callback

        # Checkerboard pattern for transparency
        self._checker = self._create_checker_pattern()

        # AI Processing overlay
        self._ai_processing = False
        self._ai_task_name = ""
        self._spinner_angle = 0
        self._pulse_phase = 0.0
        self._spinner_timer = QTimer()
        self._spinner_timer.setInterval(30)  # ~33fps animation
        self._spinner_timer.timeout.connect(self._animate_spinner)

    def _create_checker_pattern(self):
        size = 16
        pattern = QPixmap(size * 2, size * 2)
        painter = QPainter(pattern)
        painter.fillRect(0, 0, size * 2, size * 2, QColor(40, 40, 40))
        painter.fillRect(0, 0, size, size, QColor(50, 50, 50))
        painter.fillRect(size, size, size, size, QColor(50, 50, 50))
        painter.end()
        return pattern

    def set_image(self, cv_image):
        """Set image from OpenCV BGR numpy array."""
        self._image = cv_image
        if cv_image is None:
            self._qimage = None
            self._pixmap = None
            self.update()
            return

        if len(cv_image.shape) == 2:
            h, w = cv_image.shape
            rgb = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        elif cv_image.shape[2] == 4:
            h, w = cv_image.shape[:2]
            rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
            self._qimage = QImage(rgb.data, w, h, w * 4, QImage.Format.Format_RGBA8888).copy()
            self._pixmap = QPixmap.fromImage(self._qimage)
            self.update()
            return
        else:
            h, w = cv_image.shape[:2]
            rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        self._qimage = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888).copy()
        self._pixmap = QPixmap.fromImage(self._qimage)
        self.update()

    def fit_to_view(self):
        """Fit image to widget size."""
        if self._pixmap is None:
            return
        pw, ph = self._pixmap.width(), self._pixmap.height()
        ww, wh = self.width() - 40, self.height() - 40
        if pw == 0 or ph == 0:
            return
        self._zoom = min(ww / pw, wh / ph)
        self._pan_offset = QPoint(
            int((ww + 40 - pw * self._zoom) / 2),
            int((wh + 40 - ph * self._zoom) / 2)
        )
        self.zoom_changed.emit(self._zoom)
        self.update()

    def set_zoom(self, zoom):
        self._zoom = max(self._min_zoom, min(self._max_zoom, zoom))
        self.zoom_changed.emit(self._zoom)
        self.update()

    def get_zoom(self):
        return self._zoom

    def set_brush_mode(self, active, size=20):
        self._brush_active = active
        self._brush_size = size
        if active and self._image is not None:
            h, w = self._image.shape[:2]
            self._brush_mask = np.zeros((h, w), dtype=np.uint8)
        self.update()

    def get_brush_mask(self):
        return self._brush_mask

    def clear_brush_mask(self):
        if self._brush_mask is not None:
            self._brush_mask[:] = 0
        self.update()

    def _widget_to_image(self, pos):
        """Convert widget coordinates to image coordinates."""
        ix = int((pos.x() - self._pan_offset.x()) / self._zoom)
        iy = int((pos.y() - self._pan_offset.y()) / self._zoom)
        return ix, iy

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Background
        painter.fillRect(self.rect(), QColor(9, 9, 11))

        if self._pixmap is None:
            return

        # Compute image rectangle
        pw = int(self._pixmap.width() * self._zoom)
        ph = int(self._pixmap.height() * self._zoom)
        ox, oy = self._pan_offset.x(), self._pan_offset.y()

        # Draw checkerboard under image
        painter.save()
        painter.setClipRect(ox, oy, pw, ph)
        painter.drawTiledPixmap(QRect(ox, oy, pw, ph), self._checker)
        painter.restore()

        # Draw image
        target = QRect(ox, oy, pw, ph)
        painter.drawPixmap(target, self._pixmap)

        # Draw brush mask overlay
        if self._brush_mask is not None and np.any(self._brush_mask > 0):
            overlay = np.zeros((*self._brush_mask.shape, 4), dtype=np.uint8)
            overlay[:, :, 0] = 255  # Red
            overlay[:, :, 3] = (self._brush_mask * 0.4).astype(np.uint8)
            h, w = overlay.shape[:2]
            qimg = QImage(overlay.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
            painter.drawPixmap(target, QPixmap.fromImage(qimg))

        # Draw brush cursor
        if self._brush_active:
            cursor_pos = self.mapFromGlobal(self.cursor().pos())
            radius = int(self._brush_size * self._zoom / 2)
            painter.setPen(QPen(QColor(255, 255, 255, 150), 1.5))
            painter.drawEllipse(cursor_pos, radius, radius)

        # ─── AI Processing Overlay ────────────────────────
        if self._ai_processing:
            w_w, w_h = self.width(), self.height()
            
            # Dark overlay
            painter.fillRect(0, 0, w_w, w_h, QColor(5, 2, 4, 180))
            
            cx, cy = w_w // 2, w_h // 2
            
            # Outer pulsing glow
            pulse = 0.5 + 0.5 * np.sin(self._pulse_phase)
            glow_radius = 60 + pulse * 15
            glow = QRadialGradient(QPointF(cx, cy), glow_radius)
            glow.setColorAt(0.0, QColor(219, 39, 119, int(80 * pulse)))
            glow.setColorAt(0.5, QColor(219, 39, 119, int(30 * pulse)))
            glow.setColorAt(1.0, QColor(219, 39, 119, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), glow_radius, glow_radius)
            
            # Spinning arc ring
            ring_rect = QRectF(cx - 32, cy - 32, 64, 64)
            gradient = QConicalGradient(QPointF(cx, cy), self._spinner_angle)
            gradient.setColorAt(0.0, QColor(244, 114, 182, 255))  # vivid pink
            gradient.setColorAt(0.35, QColor(219, 39, 119, 200))
            gradient.setColorAt(0.7, QColor(157, 23, 77, 80))
            gradient.setColorAt(1.0, QColor(157, 23, 77, 0))
            
            pen = QPen(QBrush(gradient), 3.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(ring_rect)
            
            # Inner circle (dark glass)
            inner_rect = QRectF(cx - 24, cy - 24, 48, 48)
            inner_grad = QRadialGradient(QPointF(cx, cy - 5), 28)
            inner_grad.setColorAt(0.0, QColor(30, 12, 20, 220))
            inner_grad.setColorAt(1.0, QColor(15, 7, 10, 240))
            painter.setPen(QPen(QColor(236, 72, 153, 60), 1))
            painter.setBrush(QBrush(inner_grad))
            painter.drawEllipse(inner_rect)
            
            # Brain icon in center
            painter.setPen(Qt.PenStyle.NoPen)
            icon_font = QFont("Segoe UI Emoji", 16)
            painter.setFont(icon_font)
            painter.setPen(QColor(244, 114, 182, 230))
            painter.drawText(QRectF(cx - 16, cy - 14, 32, 28), 
                           Qt.AlignmentFlag.AlignCenter, "🧠")
            
            # Task name text
            text_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            painter.setFont(text_font)
            painter.setPen(QColor(251, 207, 232, 230))  # soft pink
            painter.drawText(QRectF(0, cy + 48, w_w, 24), 
                           Qt.AlignmentFlag.AlignCenter, self._ai_task_name)
            
            # Subtitle
            sub_font = QFont("Segoe UI", 9)
            painter.setFont(sub_font)
            painter.setPen(QColor(157, 23, 77, 180))
            dots = "." * (1 + int(self._pulse_phase) % 3)
            painter.drawText(QRectF(0, cy + 70, w_w, 20), 
                           Qt.AlignmentFlag.AlignCenter, f"Processing{dots}")

        painter.end()

    def show_ai_processing(self, task_name="AI Processing"):
        """Show the AI processing overlay with animation."""
        self._ai_processing = True
        self._ai_task_name = task_name
        self._spinner_angle = 0
        self._pulse_phase = 0.0
        self._spinner_timer.start()
        self.update()

    def hide_ai_processing(self):
        """Hide the AI processing overlay."""
        self._ai_processing = False
        self._spinner_timer.stop()
        self.update()

    def _animate_spinner(self):
        """Timer-driven animation tick."""
        self._spinner_angle = (self._spinner_angle + 4) % 360
        self._pulse_phase += 0.08
        self.update()

    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel."""
        delta = event.angleDelta().y()
        pos = event.position().toPoint()

        old_zoom = self._zoom
        factor = 1.1 if delta > 0 else 0.9
        new_zoom = max(self._min_zoom, min(self._max_zoom, self._zoom * factor))

        # Zoom towards cursor
        self._pan_offset = QPoint(
            int(pos.x() - (pos.x() - self._pan_offset.x()) * new_zoom / old_zoom),
            int(pos.y() - (pos.y() - self._pan_offset.y()) * new_zoom / old_zoom)
        )
        self._zoom = new_zoom
        self.zoom_changed.emit(self._zoom)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and
            event.modifiers() & Qt.KeyboardModifier.AltModifier):
            self._panning = True
            self._pan_start = event.pos() - self._pan_offset
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.LeftButton and self._brush_active:
            self._brush_painting = True
            ix, iy = self._widget_to_image(event.pos())
            self._paint_brush(ix, iy)

    def mouseMoveEvent(self, event):
        if self._panning:
            self._pan_offset = event.pos() - self._pan_start
            self.update()
        elif self._brush_painting and self._brush_active:
            ix, iy = self._widget_to_image(event.pos())
            self._paint_brush(ix, iy)

        # Update cursor position
        if self._image is not None:
            ix, iy = self._widget_to_image(event.pos())
            h, w = self._image.shape[:2]
            if 0 <= ix < w and 0 <= iy < h:
                self.cursor_pos_changed.emit(ix, iy)

        if self._brush_active:
            self.update()  # Redraw brush cursor

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton or \
           (event.button() == Qt.MouseButton.LeftButton and self._panning):
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif event.button() == Qt.MouseButton.LeftButton:
            self._brush_painting = False
            if self.on_brush_stroke and self._brush_mask is not None:
                self.on_brush_stroke(self._brush_mask)

    def _paint_brush(self, ix, iy):
        if self._brush_mask is None or self._image is None:
            return
        h, w = self._image.shape[:2]
        r = self._brush_size // 2
        if 0 <= ix < w and 0 <= iy < h:
            cv2.circle(self._brush_mask, (ix, iy), r, 255, -1)
            self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if hasattr(self, 'on_file_drop'):
                self.on_file_drop(file_path)
