"""
Advance Editor — Premium Luxury Glassmorphism Pink Theme (Enhanced)
Design System:
  • Deep Burgundy-Black Base: #0f070a
  • Glass Surfaces: rgba() with backdrop blur simulation
  • Pink Accent Palette: pale #fce7f3 → vivid #db2777 → deep #9d174d
  • 60-30-10 Rule applied with pink accents
  • Enhanced spacing, typography, and micro-interactions
"""

DARK_THEME = """
/* ═══════════════════════════════════════════════════════════
   ADVANCE EDITOR — PREMIUM LUXURY GLASSMORPHISM PINK THEME (ENHANCED)
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
    border-bottom: 1px solid rgba(236, 72, 153, 0.15);
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
    transition: all 0.2s ease;
}

#titleBar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
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
    background-color: rgba(236, 72, 153, 0.12);
    color: #ffffff;
}

QMenu {
    background-color: rgba(20, 5, 12, 0.97);
    border: 1px solid rgba(236, 72, 153, 0.2);
    border-radius: 12px;
    padding: 8px;
    margin: 4px;
}

QMenu::item {
    padding: 10px 32px 10px 16px;
    border-radius: 8px;
    margin: 2px 0;
    color: #fce7f3;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #be123c, stop:1 #db2777);
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: rgba(236, 72, 153, 0.12);
    margin: 6px 12px;
}

QMenu::item:disabled { color: #831843; }

/* ─── Left Toolbar (Glass Card) ─── */
#toolbar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(20, 5, 12, 0.85),
        stop:1 rgba(255, 255, 255, 0.02));
    border-right: 1px solid rgba(236, 72, 153, 0.1);
    min-width: 72px;
    max-width: 72px;
    padding: 8px 0;
}

#toolbar QPushButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: #fbcfe8;
    padding: 0;
    margin: 4px 6px;
    min-width: 60px;
    min-height: 54px;
    max-width: 60px;
    max-height: 54px;
    transition: all 0.2s ease;
}

#toolbar QPushButton:hover {
    background-color: rgba(236, 72, 153, 0.15);
    border: 1px solid rgba(236, 72, 153, 0.3);
    color: #ffffff;
    transform: scale(1.05);
}

#toolbar QPushButton:checked,
#toolbar QPushButton[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(219, 39, 119, 0.35),
        stop:1 rgba(190, 18, 60, 0.3));
    color: #ffffff;
    border: 1px solid rgba(236, 72, 153, 0.65);
}

#toolbar QPushButton QLabel {
    color: #fbcfe8;
}

#toolbar QPushButton:hover QLabel,
#toolbar QPushButton:checked QLabel {
    color: #ffffff;
}

#toolSeparator {
    background-color: rgba(236, 72, 153, 0.1);
    min-height: 1px;
    max-height: 1px;
    margin: 8px 10px;
}

/* ─── Right Panel (Premium Glassmorphism) ─── */
#rightPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(25, 8, 15, 0.88),
        stop:1 rgba(15, 5, 10, 0.94));
    border-left: 1px solid rgba(236, 72, 153, 0.12);
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
    border-bottom: 1px solid rgba(236, 72, 153, 0.1);
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
    transition: all 0.2s ease;
}

QTabBar::tab:selected {
    color: #f9a8d4;
    border-bottom: 2px solid #db2777;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(219, 39, 119, 0.08),
        stop:1 transparent);
}

QTabBar::tab:hover:!selected {
    color: #fbcfe8;
    background-color: rgba(255, 255, 255, 0.03);
}

/* ─── Scrollbar ─── */
QScrollArea { background-color: transparent; border: none; }

QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 0;
    border: none;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(219, 39, 119, 0.4),
        stop:1 rgba(236, 72, 153, 0.6));
    border-radius: 3px;
    min-height: 40px;
    transition: all 0.2s ease;
}

QScrollBar::handle:vertical:hover {
    background: rgba(236, 72, 153, 0.8);
    width: 8px;
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
    transition: all 0.2s ease;
}

#sectionHeader:hover {
    background-color: rgba(236, 72, 153, 0.08);
    color: #ffffff;
}

/* ─── Sliders (Pink Luxury) ─── */
QSlider {
    min-height: 24px;
    max-height: 24px;
    padding: 0;
}

QSlider::groove:horizontal {
    background-color: rgba(255, 255, 255, 0.08);
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
    transition: all 0.2s ease;
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
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #fce7f3;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
    transition: all 0.2s ease;
}

QPushButton:hover {
    background-color: rgba(236, 72, 153, 0.12);
    border-color: rgba(236, 72, 153, 0.35);
    color: #ffffff;
}

QPushButton:pressed {
    background-color: rgba(219, 39, 119, 0.3);
    border-color: rgba(219, 39, 119, 0.55);
}

/* AI Action Buttons — Luxury Glass */
#aiButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(25, 8, 15, 0.7),
        stop:0.5 rgba(236, 72, 153, 0.08),
        stop:1 rgba(190, 18, 60, 0.12));
    border: 1px solid rgba(236, 72, 153, 0.22);
    border-radius: 12px;
    color: #fbcfe8;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    font-size: 12px;
    margin: 4px 0;
    transition: all 0.2s ease;
}

#aiButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(236, 72, 153, 0.15),
        stop:1 rgba(219, 39, 119, 0.25));
    border-color: rgba(236, 72, 153, 0.5);
    color: #ffffff;
}

#aiButton:pressed {
    background-color: rgba(219, 39, 119, 0.4);
    border-color: rgba(219, 39, 119, 0.75);
}

/* ─── Layer Items ─── */
#layerItem {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 4px 8px;
    margin: 2px 0;
    transition: all 0.2s ease;
}

#layerItem:hover {
    background-color: rgba(236, 72, 153, 0.08);
    border-color: rgba(236, 72, 153, 0.2);
}

#layerItemActive {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(219, 39, 119, 0.15),
        stop:1 rgba(236, 72, 153, 0.08));
    border: 1px solid rgba(236, 72, 153, 0.4);
    border-radius: 8px;
    padding: 4px 8px;
    margin: 2px 0;
}

/* ─── Canvas ─── */
#canvasArea { background-color: #050204; }

/* ─── Status Bar ─── */
#statusBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(15, 5, 10, 0.96),
        stop:1 rgba(25, 8, 15, 0.96));
    border-top: 1px solid rgba(236, 72, 153, 0.12);
    min-height: 28px;
    max-height: 28px;
}

#statusBar QLabel { color: #9d174d; font-size: 11px; }

/* ─── Combo Box ─── */
QComboBox {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #fce7f3;
    padding: 6px 12px;
    min-height: 28px;
    font-size: 12px;
    transition: all 0.2s ease;
}

QComboBox:hover {
    border-color: rgba(236, 72, 153, 0.35);
    background-color: rgba(236, 72, 153, 0.08);
}

QComboBox::drop-down { border: none; width: 28px; }

QComboBox QAbstractItemView {
    background-color: rgba(20, 5, 12, 0.98);
    border: 1px solid rgba(236, 72, 153, 0.25);
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
    background-color: rgba(255, 255, 255, 0.04);
    transition: all 0.2s ease;
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
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 16px;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 16px 40px;
    min-width: 240px;
    transition: all 0.2s ease;
}

#openButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #be123c,
        stop:0.5 #db2777,
        stop:1 #ec4899);
    border: 1px solid rgba(255, 255, 255, 0.35);
    transform: scale(1.02);
}

/* ─── Progress Bar ─── */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.06);
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
    border: 1px solid rgba(236, 72, 153, 0.3);
    border-radius: 8px;
    color: #fce7f3;
    padding: 8px 12px;
    font-size: 11px;
}

/* ─── Model Status Badge ─── */
#modelBadge {
    background-color: rgba(236, 72, 153, 0.15);
    border: 1px solid rgba(236, 72, 153, 0.35);
    border-radius: 6px;
    color: #f472b6;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

#modelBadgeOffline {
    background-color: rgba(234, 179, 8, 0.12);
    border: 1px solid rgba(234, 179, 8, 0.3);
    border-radius: 6px;
    color: #fbbf24;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

/* ─── AI Sections (Glass Cards) ─── */
#aiSection {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255, 255, 255, 0.03),
        stop:1 rgba(236, 72, 153, 0.025));
    border: 1px solid rgba(236, 72, 153, 0.1);
    border-radius: 14px;
    padding: 12px;
    margin: 6px 8px;
}

/* ─── Library Grid ─── */
#libraryArea {
    background-color: #0f070a;
}

/* Library Folder Section */
#libraryFolderLabel {
    color: #a1a1aa;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 8px 0;
}

QTreeView {
    background: transparent;
    border: none;
    color: #d4d4d8;
    border-radius: 8px;
    padding: 4px;
}

QTreeView::item:hover {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 6px;
}

QTreeView::item:selected {
    background: rgba(124, 58, 237, 0.25);
    color: #fff;
    border-radius: 6px;
}

/* Library Grid Items */
QListWidget {
    background: #0c0c0f;
    border: none;
    outline: none;
    border-radius: 8px;
}

QListWidget::item {
    color: #d4d4d8;
    font-size: 12px;
    border-radius: 8px;
    padding: 8px;
    margin: 4px;
    transition: all 0.2s ease;
}

QListWidget::item:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: scale(1.02);
}

QListWidget::item:selected {
    background: rgba(124, 58, 237, 0.25);
    border: 2px solid #7c3aed;
}

/* ─── Splitter ─── */
QSplitter::handle {
    background: rgba(236, 72, 153, 0.1);
    width: 1px;
}

QSplitter::handle:hover {
    background: rgba(236, 72, 153, 0.2);
}

/* ─── Copilot Panel Enhancements ─── */
#copilotHeader {
    color: #fbcfe8;
    font-size: 16px;
    font-weight: bold;
    padding: 8px 0;
}

#copilotSubheader {
    color: #a1a1aa;
    font-size: 11px;
    padding: 4px 0;
}

#copilotChatArea {
    background: transparent;
    border: none;
}

#copilotInput {
    background: rgba(20, 20, 25, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 8px 16px;
    color: white;
    font-size: 12px;
    transition: all 0.2s ease;
}

#copilotInput:focus {
    border: 1px solid #db2777;
    background: rgba(20, 20, 25, 0.95);
}

#copilotSendBtn {
    background: #db2777;
    color: white;
    border-radius: 16px;
    border: none;
    font-weight: bold;
    transition: all 0.2s ease;
}

#copilotSendBtn:hover {
    background: #be185d;
    transform: scale(1.05);
}

#copilotAnalyzeBtn {
    background: transparent;
    border: 1px solid rgba(219, 39, 119, 0.55);
    color: #fbcfe8;
    border-radius: 12px;
    padding: 6px 12px;
    transition: all 0.2s ease;
}

#copilotAnalyzeBtn:hover {
    background: rgba(219, 39, 119, 0.25);
    border-color: rgba(219, 39, 119, 0.8);
}

#copilotAutoPilotBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #db2777, stop:1 #9d174d);
    border: none;
    color: #ffffff;
    border-radius: 12px;
    padding: 6px 12px;
    font-weight: bold;
    transition: all 0.2s ease;
}

#copilotAutoPilotBtn:hover {
    background: #be185d;
    transform: scale(1.02);
}

/* ─── Message Bubbles ─── */
#userBubble {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(219, 39, 119, 0.45), stop:1 rgba(157, 23, 77, 0.65));
    color: #fdf2f8;
    border-radius: 12px;
    border-top-right-radius: 2px;
    padding: 10px 14px;
    border: 1px solid rgba(244, 114, 182, 0.35);
    margin: 4px 0;
}

#assistantBubble {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 45, 50, 0.85), stop:1 rgba(25, 25, 30, 0.92));
    color: #e4e4e7;
    border-radius: 12px;
    border-top-left-radius: 2px;
    padding: 10px 14px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    margin: 4px 0;
}

/* ─── Text Input Fields ─── */
QLineEdit {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #fce7f3;
    padding: 6px 12px;
    min-height: 28px;
    font-size: 12px;
    transition: all 0.2s ease;
}

QLineEdit:focus {
    border: 1px solid rgba(236, 72, 153, 0.5);
    background-color: rgba(255, 255, 255, 0.06);
}

QLineEdit:hover {
    border: 1px solid rgba(236, 72, 153, 0.3);
}

QTextEdit {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #fce7f3;
    padding: 6px 12px;
    font-size: 12px;
    transition: all 0.2s ease;
}

QTextEdit:focus {
    border: 1px solid rgba(236, 72, 153, 0.5);
    background-color: rgba(255, 255, 255, 0.06);
}
"""

/* ─── Module Switcher ─── */
#moduleBtn {
    font-weight: bold;
    border: none;
    padding: 0 16px;
    color: #71717a;
    background: transparent;
    transition: all 0.2s ease;
}

#moduleBtn:checked {
    color: #db2777;
    background: rgba(236, 72, 153, 0.08);
    border-radius: 6px;
}

#moduleBtn:hover:!checked {
    color: #fbcfe8;
    background: rgba(255, 255, 255, 0.03);
}

/* ─── Copilot Dock ─── */
#copilotDock::title {
    background: #0f070a;
    color: #fbcfe8;
    font-weight: bold;
    padding: 6px;
    border-bottom: 1px solid rgba(236, 72, 153, 0.15);
}

/* ─── Welcome Screen Refinements ─── */
#welcomeHint {
    color: #71717a;
    font-size: 12px;
    padding-bottom: 24px;
}

#welcomeModelInfo {
    color: #52525b;
    font-size: 11px;
    padding-top: 24px;
}
