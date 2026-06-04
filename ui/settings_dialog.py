from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from config import settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self._build_ui()
        self.setStyleSheet(parent.styleSheet() if parent else "")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Preferences")
        title.setStyleSheet("font-size: 16px; font-weight: 700; background: transparent; border: none;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.ollama_model_input = QLineEdit(settings.OLLAMA_MODEL)
        self.ollama_model_input.setPlaceholderText("mistral")
        form.addRow("Ollama model:", self.ollama_model_input)

        self.chunk_size_input = QSpinBox()
        self.chunk_size_input.setRange(50, 2000)
        self.chunk_size_input.setSingleStep(50)
        self.chunk_size_input.setValue(settings.CHUNK_SIZE)
        self.chunk_size_input.setSuffix(" words")
        form.addRow("Chunk size:", self.chunk_size_input)

        layout.addLayout(form)

        hint = QLabel("Preferences are saved to config/user_prefs.json and applied immediately.")
        hint.setStyleSheet("font-size: 11px; color: #8e8e93; background: transparent; border: none;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setObjectName("primary_button")
        save.clicked.connect(self._save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def _save(self):
        settings.save_prefs({
            "ollama_model": self.ollama_model_input.text().strip() or "mistral",
            "chunk_size": self.chunk_size_input.value(),
        })
        self.accept()
