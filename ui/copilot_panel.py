from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QLineEdit, QScrollArea, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette

from engine.copilot_engine import CopilotWorker

class MessageBubble(QWidget):
    """Enhanced message bubble with improved styling."""
    def __init__(self, text, is_user=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(8)
        
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        
        # Glassmorphism styling for bubbles
        if is_user:
            bubble.setObjectName("userBubble")
            layout.addStretch()
            layout.addWidget(bubble, 8)
        else:
            bubble.setObjectName("assistantBubble")
            layout.addWidget(bubble, 8)
            layout.addStretch()

class CopilotPanel(QWidget):
    """Enhanced AI Copilot panel with improved UI and styling."""
    execute_command = pyqtSignal(str, str) # tool_name, value
    request_image = pyqtSignal() # Ask main window for current image
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self._current_image = None
        self._worker = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("🧠 AI Copilot")
        header.setObjectName("copilotHeader")
        layout.addWidget(header)
        
        sub = QLabel("Powered by OpenRouter (Nemotron + Ring)")
        sub.setObjectName("copilotSubheader")
        layout.addWidget(sub)
        
        # Chat area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setObjectName("copilotChatArea")
        
        self.chat_container = QWidget()
        self.chat_container.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(10)
        
        self.scroll.setWidget(self.chat_container)
        layout.addWidget(self.scroll, 1)
        
        # Add welcome message
        self._add_message("Hi! I'm your AI editing assistant. Ask me how to improve your photo, or just tell me what to do (e.g. 'Make it warmer and brighter'). You can also click 'Analyze Image' for my professional advice!", False)
        
        # Status
        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #f472b6; font-size: 11px; font-style: italic; font-weight: 500;")
        self.status_lbl.hide()
        layout.addWidget(self.status_lbl)
        
        # Input area
        inp_layout = QHBoxLayout()
        inp_layout.setSpacing(8)
        
        self.inp_text = QLineEdit()
        self.inp_text.setObjectName("copilotInput")
        self.inp_text.setPlaceholderText("Ask AI to edit...")
        self.inp_text.returnPressed.connect(self._send_message)
        inp_layout.addWidget(self.inp_text, 1)
        
        self.btn_send = QPushButton("➤")
        self.btn_send.setObjectName("copilotSendBtn")
        self.btn_send.setFixedSize(36, 36)
        self.btn_send.clicked.connect(self._send_message)
        inp_layout.addWidget(self.btn_send)
        layout.addLayout(inp_layout)
        
        self.btn_analyze = QPushButton("👁️ Analyze Image")
        self.btn_analyze.setObjectName("copilotAnalyzeBtn")
        self.btn_analyze.clicked.connect(self._analyze_image)
        
        self.btn_auto = QPushButton("✨ Auto-Pilot")
        self.btn_auto.setObjectName("copilotAutoPilotBtn")
        self.btn_auto.clicked.connect(self._auto_pilot)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addWidget(self.btn_analyze)
        btn_layout.addWidget(self.btn_auto)
        layout.addLayout(btn_layout)

    def _add_message(self, text, is_user):
        if not text.strip(): return
        bubble = MessageBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        # Scroll to bottom
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
        
        if is_user:
            self.messages.append({"role": "user", "content": text})
        else:
            self.messages.append({"role": "assistant", "content": text})

    def _send_message(self):
        text = self.inp_text.text().strip()
        if not text: return
        
        self.inp_text.clear()
        self._add_message(text, True)
        self._call_api(with_image=False)
        
    def _analyze_image(self):
        self._add_message("Please analyze my image and suggest edits.", True)
        self.request_image.emit() # Main window will call receive_image
        
    def _auto_pilot(self):
        self._add_message("Please take full autonomous control. Analyze the image and immediately execute all the necessary slider and AI adjustments to make it look professional.", True)
        self.request_image.emit()
        
    def receive_image(self, img):
        self._current_image = img
        self._call_api(with_image=True)

    def _call_api(self, with_image=False):
        self.btn_send.setEnabled(False)
        self.btn_analyze.setEnabled(False)
        self.status_lbl.setText("Thinking..." if not with_image else "Looking at image...")
        self.status_lbl.show()
        
        # Start worker thread
        self._worker = CopilotWorker(self.messages.copy(), self._current_image if with_image else None)
        self._worker.finished.connect(self._on_response)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_response(self, text, commands):
        self.btn_send.setEnabled(True)
        self.btn_analyze.setEnabled(True)
        self.status_lbl.hide()
        self._current_image = None
        
        self._add_message(text, False)
        
        # Execute commands!
        for cmd in commands:
            self.execute_command.emit(cmd["tool"], cmd["value"])
            
    def _on_error(self, err):
        self.btn_send.setEnabled(True)
        self.btn_analyze.setEnabled(True)
        self.status_lbl.hide()
        self._current_image = None
        
        self._add_message(f"⚠️ Error: {err}", False)
