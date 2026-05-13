"""
Advance Editor — Premium Luxury Glassmorphism Pink Theme
Design System:
  • Deep Burgundy-Black Base: #0f070a
  • Glass Surfaces: rgba() with backdrop blur simulation
  • Pink Accent Palette: pale #fce7f3 → vivid #db2777 → deep #9d174d
  • 60-30-10 Rule applied with pink accents
"""

DARK_THEME = """
/* ═══════════════════════════════════════════════════════════
   ADVANCE EDITOR — PREMIUM LUXURY GLASSMORPHISM PINK THEME
   Base: #0f070a  Surface: rgba glass  Accent: #db2777 pink
   ═══════════════════════════════════════════════════════════ */

* { outline: none; }

QWidget {
    background-color: #0f070a;
    color: #fce7f3;
    font-family: 'Segoe UI Variable', 'Segoe UI', 'Inter', system-ui, sans-serif;
    font-size: 12px;
    selection-background-color: #db2777;
    selection-color: #ffffff;
}

QMainWindow { background-color: #0f070a; }

/* ─── Title Bar ─── */
#titleBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(20, 5, 12, 0.98),
        stop:1 rgba(30, 8, 18, 0.98));
    border-bottom: 1px solid rgba(236, 72, 153, 0.12);
    min-height: 40px;
    max-height: 40px;
}

#appIcon {
    color: #f472b6;
    font-size: 20px;
    padding: 0 10px;
}

#titleLabel {
    color: #fbcfe8;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding-left: 4px;
}

#titleBar QPushButton {
    background: transparent;
    border: none;
    border-radius: 0;
    color: #9d174d;
    font-size: 11px;
    padding: 0;
    min-width: 48px;
    max-width: 48px;
    min-height: 40px;
    max-height: 40px;
}

#titleBar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.05);
    color: #f9a8d4;
}

#btnClose:hover {
    background-color: #be123c;
    color: #ffffff;
}

/* ─── Menu Bar ─── */
QMenuBar {
    background-color: transparent;
    color: #fbcfe8;
    border: none;
    padding: 0 8px;
    font-size: 12px;
    min-height: 32px;
}

QMenuBar::item {
    padding: 6px 14px;
    border-radius: 6px;
    margin: 2px 1px;
    background: transparent;
}

QMenuBar::item:selected {
    background-color: rgba(236, 72, 153, 0.1);
    color: #ffffff;
}

QMenu {
    background-color: rgba(20, 5, 12, 0.97);
    border: 1px solid rgba(236, 72, 153, 0.15);
    border-radius: 12px;
    padding: 6px;
    margin: 4px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 8px;
    margin: 1px 0;
    color: #fce7f3;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #be123c, stop:1 #db2777);
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: rgba(236, 72, 153, 0.1);
    margin: 6px 12px;
}

QMenu::item:disabled { color: #831843; }

/* ─── Left Toolbar (Glass Card) ─── */
#toolbar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(20, 5, 12, 0.8),
        stop:1 rgba(255, 255, 255, 0.01));
    border-right: 1px solid rgba(236, 72, 153, 0.08);
    min-width: 72px;
    max-width: 72px;
    padding: 8px 0;
}

#toolbar QPushButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #fbcfe8; /* Bright pink instead of dark burgundy */
    padding: 0;
    margin: 4px 6px;
    min-width: 60px;
    min-height: 54px;
    max-width: 60px;
    max-height: 54px;
}

#toolbar QPushButton:hover {
    background-color: rgba(236, 72, 153, 0.1);
    border: 1px solid rgba(236, 72, 153, 0.25);
    color: #ffffff; /* White on hover */
}

#toolbar QPushButton:checked,
#toolbar QPushButton[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(219, 39, 119, 0.3),
        stop:1 rgba(190, 18, 60, 0.25));
    color: #ffffff; /* White when active */
    border: 1px solid rgba(236, 72, 153, 0.6);
}

/* Explicitly pass the inherited color to inner QLabels */
#toolbar QPushButton QLabel {
    color: #fbcfe8;
}
#toolbar QPushButton:hover QLabel,
#toolbar QPushButton:checked QLabel {
    color: #ffffff;
}

#toolSeparator {
    background-color: rgba(236, 72, 153, 0.08);
    min-height: 1px;
    max-height: 1px;
    margin: 8px 10px;
}

/* ─── Right Panel (Premium Glassmorphism) ─── */
#rightPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(25, 8, 15, 0.85),
        stop:1 rgba(15, 5, 10, 0.92));
    border-left: 1px solid rgba(236, 72, 153, 0.1);
    min-width: 330px;
    max-width: 330px;
}

/* ─── Tab Widget ─── */
QTabWidget::pane {
    background-color: transparent;
    border: none;
    padding: 0;
}

QTabBar {
    background-color: transparent;
    border-bottom: 1px solid rgba(236, 72, 153, 0.08);
}

QTabBar::tab {
    background-color: transparent;
    color: #9d174d;
    padding: 12px 16px;
    border-bottom: 2px solid transparent;
    font-weight: 700;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 0;
}

QTabBar::tab:selected {
    color: #f9a8d4;
    border-bottom: 2px solid #db2777;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(219, 39, 119, 0.06),
        stop:1 transparent);
}

QTabBar::tab:hover:!selected {
    color: #fbcfe8;
    background-color: rgba(255, 255, 255, 0.02);
}

/* ─── Scrollbar ─── */
QScrollArea { background-color: transparent; border: none; }

QScrollBar:vertical {
    background-color: transparent;
    width: 4px;
    margin: 0;
    border: none;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(219, 39, 119, 0.3),
        stop:1 rgba(236, 72, 153, 0.5));
    border-radius: 2px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(236, 72, 153, 0.7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0; background: none; border: none;
}

/* ─── Section Headers ─── */
#sectionHeader {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    color: #fbcfe8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 12px 16px;
    text-align: left;
    margin: 4px 0 0 0;
}

#sectionHeader:hover {
    background-color: rgba(236, 72, 153, 0.06);
    color: #ffffff;
}

/* ─── Sliders (Pink Luxury) ─── */
QSlider {
    min-height: 24px;
    max-height: 24px;
    padding: 0;
}

QSlider::groove:horizontal {
    background-color: rgba(255, 255, 255, 0.06);
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        fx:0.4, fy:0.4,
        stop:0 #fce7f3,
        stop:0.4 #f472b6,
        stop:1 #db2777);
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: none;
}

QSlider::handle:horizontal:hover {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        fx:0.3, fy:0.3,
        stop:0 #ffffff,
        stop:0.4 #f9a8d4,
        stop:1 #ec4899);
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:pressed {
    background-color: #be123c;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #9d174d, stop:0.5 #db2777, stop:1 #f472b6);
    border-radius: 2px;
    height: 4px;
}

#sliderLabel { color: #fce7f3; font-size: 11px; font-weight: 500; }

#sliderValue {
    color: #f472b6;
    font-size: 11px;
    font-weight: 700;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    min-width: 36px;
}

/* ─── Buttons (Glass Pink) ─── */
QPushButton {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    color: #fce7f3;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: rgba(236, 72, 153, 0.08);
    border-color: rgba(236, 72, 153, 0.3);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: rgba(219, 39, 119, 0.25);
    border-color: rgba(219, 39, 119, 0.5);
}

/* AI Action Buttons — Luxury Glass */
#aiButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(20, 5, 12, 0.6),
        stop:0.5 rgba(236, 72, 153, 0.06),
        stop:1 rgba(190, 18, 60, 0.1));
    border: 1px solid rgba(236, 72, 153, 0.18);
    border-radius: 12px;
    color: #fbcfe8;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    font-size: 12px;
    margin: 3px 0;
}

#aiButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(236, 72, 153, 0.12),
        stop:1 rgba(219, 39, 119, 0.2));
    border-color: rgba(236, 72, 153, 0.45);
    color: #ffffff;
}

#aiButton:pressed {
    background-color: rgba(219, 39, 119, 0.35);
    border-color: rgba(219, 39, 119, 0.7);
}

/* ─── Layer Items ─── */
#layerItem {
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4px 8px;
    margin: 2px 0;
}

#layerItem:hover {
    background-color: rgba(236, 72, 153, 0.05);
    border-color: rgba(236, 72, 153, 0.15);
}

#layerItemActive {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(219, 39, 119, 0.12),
        stop:1 rgba(236, 72, 153, 0.06));
    border: 1px solid rgba(236, 72, 153, 0.35);
    border-radius: 8px;
    padding: 4px 8px;
    margin: 2px 0;
}

/* ─── Canvas ─── */
#canvasArea { background-color: #050204; }

/* ─── Status Bar ─── */
#statusBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(15, 5, 10, 0.95),
        stop:1 rgba(25, 8, 15, 0.95));
    border-top: 1px solid rgba(236, 72, 153, 0.1);
    min-height: 28px;
    max-height: 28px;
}

#statusBar QLabel { color: #9d174d; font-size: 11px; }

/* ─── Combo Box ─── */
QComboBox {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    color: #fce7f3;
    padding: 6px 12px;
    min-height: 28px;
    font-size: 12px;
}

QComboBox:hover {
    border-color: rgba(236, 72, 153, 0.3);
    background-color: rgba(236, 72, 153, 0.05);
}

QComboBox::drop-down { border: none; width: 28px; }

QComboBox QAbstractItemView {
    background-color: rgba(20, 5, 12, 0.98);
    border: 1px solid rgba(236, 72, 153, 0.2);
    border-radius: 10px;
    selection-background-color: #db2777;
    color: #fce7f3;
    padding: 4px;
    outline: none;
}

/* ─── Checkbox ─── */
QCheckBox { color: #fbcfe8; spacing: 8px; font-size: 11px; }

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid #9d174d;
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.03);
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #be123c, stop:1 #db2777);
    border-color: #f472b6;
}

QCheckBox::indicator:hover { border-color: #f472b6; }

/* ─── Welcome Overlay (Hero) ─── */
#welcomeOverlay {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(5, 2, 4, 0.97),
        stop:0.5 rgba(15, 5, 10, 0.97),
        stop:1 rgba(5, 2, 4, 0.97));
}

#welcomeTitle {
    color: #ffffff;
    font-size: 40px;
    font-weight: 800;
    letter-spacing: -1px;
}

#welcomeSubtitle {
    color: #fbcfe8;
    font-size: 15px;
    font-weight: 400;
    padding: 8px 0 28px 0;
}

#welcomeAccent { color: #f472b6; }

#openButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #9d174d,
        stop:0.4 #be123c,
        stop:1 #db2777);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 16px 40px;
    min-width: 240px;
}

#openButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #be123c,
        stop:0.5 #db2777,
        stop:1 #ec4899);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* ─── Progress Bar ─── */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 3px;
    height: 6px;
    color: transparent;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #9d174d,
        stop:0.5 #db2777,
        stop:1 #f472b6);
    border-radius: 3px;
}

/* ─── Tooltips ─── */
QToolTip {
    background-color: rgba(20, 5, 12, 0.98);
    border: 1px solid rgba(236, 72, 153, 0.25);
    border-radius: 8px;
    color: #fce7f3;
    padding: 8px 12px;
    font-size: 11px;
}

/* ─── Model Status Badge ─── */
#modelBadge {
    background-color: rgba(236, 72, 153, 0.12);
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 6px;
    color: #f472b6;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

#modelBadgeOffline {
    background-color: rgba(234, 179, 8, 0.1);
    border: 1px solid rgba(234, 179, 8, 0.25);
    border-radius: 6px;
    color: #fbbf24;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

/* ─── AI Sections (Glass Cards) ─── */
#aiSection {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 255, 255, 0.025),
        stop:1 rgba(236, 72, 153, 0.02));
    border: 1px solid rgba(236, 72, 153, 0.08);
    border-radius: 14px;
    padding: 10px;
    margin: 4px 8px;
}

/* ─── Library Grid ─── */
#libraryArea {
    background-color: #0f070a;
}

/* ─── Splitter ─── */
QSplitter::handle {
    background: rgba(236, 72, 153, 0.08);
    width: 1px;
}
"""
