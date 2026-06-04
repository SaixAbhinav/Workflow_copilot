import os
import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QKeySequence, QTextOption
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.auto_scan import run_auto_scan
from core.llm_router import set_provider
from core.workflow_engine import run_workflow
from exports.exporter import export_csv, export_txt
from input_processing.cleaner import clean_text
from input_processing.email_handler import get_latest_emails
from input_processing.google_auth import (
    add_account,
    get_active_account,
    list_accounts,
    remove_account,
    set_active_account,
)
from input_processing.pdf_handler import read_pdf
from input_processing.text_handler import read_text_file
from services.calendar_service import push_tasks_to_calendar
from storage.history_manager import fetch, purge, record
from ui.samples import SAMPLES
from ui.settings_dialog import SettingsDialog
from ui.task_review_dialog import TaskReviewDialog

STYLESHEET = """
QWidget {
    background-color: #1c1c1e;
    color: #e5e5ea;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}
#header { background-color: #2c2c2e; border-bottom: 1px solid #3a3a3c; }
#header QLabel { background: transparent; color: #e5e5ea; border: none; }
#app_title { font-size: 18px; font-weight: 700; color: #ffffff; background: transparent; border: none; }
#app_subtitle { font-size: 11px; color: #8e8e93; background: transparent; border: none; }
#section_label {
    font-size: 11px; font-weight: 600; color: #8e8e93;
    letter-spacing: 1px; background: transparent; border: none; padding: 0px;
}
QTextEdit, QLineEdit {
    background-color: #1c1c1e;
    border: 1px solid #3a3a3c;
    border-radius: 8px;
    padding: 10px;
    color: #e5e5ea;
    selection-background-color: #0a84ff;
    font-size: 13px;
}
QLineEdit { padding: 6px 10px; }
QTextEdit:focus, QLineEdit:focus { border: 1px solid #0a84ff; }
QTextEdit[dragActive="true"] {
    border: 2px dashed #0a84ff;
    background-color: #1c2e47;
}
QListWidget {
    background-color: #1c1c1e;
    border: 1px solid #3a3a3c;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}
QListWidget::item { padding: 8px 10px; border-radius: 6px; color: #e5e5ea; }
QListWidget::item:hover { background-color: #3a3a3c; }
QListWidget::item:selected { background-color: #0a84ff; color: #ffffff; }
QComboBox {
    background-color: #3a3a3c;
    border: 1px solid #48484a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e5e5ea;
}
QComboBox:hover { border: 1px solid #636366; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #3a3a3c;
    border: 1px solid #48484a;
    border-radius: 6px;
    selection-background-color: #0a84ff;
    selection-color: #ffffff;
    color: #e5e5ea;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item {
    background-color: #3a3a3c;
    color: #e5e5ea;
    padding: 6px 10px;
    border: none;
    min-height: 22px;
}
QComboBox QAbstractItemView::item:selected,
QComboBox QAbstractItemView::item:hover {
    background-color: #0a84ff;
    color: #ffffff;
}
QPushButton {
    background-color: #3a3a3c;
    color: #e5e5ea;
    border: 1px solid #48484a;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}
QPushButton:hover { background-color: #48484a; border-color: #636366; }
QPushButton:pressed { background-color: #2c2c2e; }
QPushButton:disabled { background-color: #2c2c2e; color: #48484a; border-color: #3a3a3c; }
#primary_button {
    background-color: #0a84ff; color: #ffffff; border: none;
    border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600;
}
#primary_button:hover { background-color: #409cff; }
#primary_button:pressed { background-color: #0060df; }
#primary_button:disabled { background-color: #1c3a5e; color: #48484a; }
#success_button {
    background-color: #30d158; color: #ffffff; border: none;
    border-radius: 8px; padding: 8px 16px; font-weight: 600;
}
#success_button:hover { background-color: #4ae073; }
#success_button:disabled { background-color: #1c3a22; color: #48484a; }
#danger_button {
    background-color: transparent; color: #ff453a;
    border: 1px solid #ff453a; border-radius: 8px; padding: 6px 14px; font-size: 12px;
}
#danger_button:hover { background-color: #3a1c1c; }
#icon_button {
    background-color: transparent; border: 1px solid #48484a;
    border-radius: 8px; padding: 6px 10px; font-size: 14px;
}
#icon_button:hover { background-color: #3a3a3c; }
#divider { background-color: #3a3a3c; max-height: 1px; border: none; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
QScrollBar::handle:vertical { background: #48484a; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #636366; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
#status_label { font-size: 12px; color: #8e8e93; background: transparent; border: none; }
QProgressBar {
    background-color: #2c2c2e; border: none; border-radius: 3px; height: 4px;
}
QProgressBar::chunk { background-color: #0a84ff; border-radius: 3px; }
QTabWidget::pane { border: 1px solid #3a3a3c; border-radius: 8px; }
QTabBar::tab {
    background: #2c2c2e; color: #8e8e93;
    padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #3a3a3c; color: #ffffff; }
QTabBar::tab:hover { background: #3a3a3c; }
QSpinBox {
    background-color: #3a3a3c; border: 1px solid #48484a;
    border-radius: 6px; padding: 4px 8px; color: #e5e5ea;
}
QSplitter::handle { background-color: #2c2c2e; }
QSplitter::handle:horizontal { width: 6px; margin: 4px 0; border-radius: 3px; }
QSplitter::handle:vertical { height: 6px; margin: 0 4px; border-radius: 3px; }
QSplitter::handle:hover { background-color: #0a84ff; }
"""


class DropTextEdit(QTextEdit):
    """QTextEdit that accepts dropped .txt/.pdf files."""
    files_dropped = pyqtSignal(list)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self); self.style().polish(self)
        else:
            super().dragEnterEvent(e)

    def dragLeaveEvent(self, e):
        self.setProperty("dragActive", False)
        self.style().unpolish(self); self.style().polish(self)

    def dropEvent(self, e):
        self.setProperty("dragActive", False)
        self.style().unpolish(self); self.style().polish(self)
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        valid = [p for p in paths if p.lower().endswith((".txt", ".pdf"))]
        if valid:
            self.files_dropped.emit(valid)
            e.acceptProposedAction()
        else:
            super().dropEvent(e)


class Worker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()
    progress = pyqtSignal(int, int)  # (current_chunk, total_chunks)

    def __init__(self, text, workflow):
        super().__init__()
        self.text = text
        self.workflow = workflow
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            cleaned = clean_text(self.text)
            if self._cancel:
                self.cancelled.emit()
                return
            result = run_workflow(
                cleaned,
                workflow=self.workflow,
                progress_callback=self.progress.emit,
            )
            if self._cancel:
                self.cancelled.emit()
                return
            self.finished.emit(result)
        except Exception as e:
            if self._cancel:
                self.cancelled.emit()
            else:
                self.error.emit(str(e))


class AddAccountWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            self.finished.emit(add_account())
        except Exception as e:
            self.error.emit(str(e))


class CalendarWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, action_items, account=None):
        super().__init__()
        self.action_items = action_items
        self.account = account

    def run(self):
        try:
            self.finished.emit(push_tasks_to_calendar(self.action_items, account=self.account))
        except Exception as e:
            self.error.emit(str(e))


class AutoScanWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()
    progress = pyqtSignal(int, int, str)  # (current, total, subject)

    def __init__(self, window_hours: int, max_emails: int, account: str | None):
        super().__init__()
        self.window_hours = window_hours
        self.max_emails = max_emails
        self.account = account
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            results = run_auto_scan(
                window_hours=self.window_hours,
                max_emails=self.max_emails,
                account=self.account,
                progress_callback=lambda c, t, s: self.progress.emit(c, t, s),
                cancel_check=lambda: self._cancel,
            )
            if self._cancel:
                self.cancelled.emit()
            else:
                self.finished.emit(results)
        except Exception as e:
            if self._cancel:
                self.cancelled.emit()
            else:
                self.error.emit(str(e))


def _section_label(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("section_label")
    return label

def _divider() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFrameShape(QFrame.HLine)
    return line


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Workflow Copilot")
        self.setMinimumSize(1200, 720)
        self.emails_data = []
        self._emails_next_page_token = None
        self._history_data = []
        self._last_result = {}
        self._last_workflow = "summary"
        self._mode = "manual"
        self._auto_results: list[dict] = []
        self._build_ui()
        self._register_shortcuts()
        self._apply_mode()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(64)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("AI Workflow Copilot")
        title.setObjectName("app_title")
        subtitle = QLabel("Summarise · Tasks · Insights · Compare")
        subtitle.setObjectName("app_subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        hl.addLayout(title_col)

        hl.addSpacing(20)
        hl.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Manual", "Auto"])
        self.mode_combo.setFixedWidth(110)
        self.mode_combo.setToolTip(
            "Manual: pick an input and a workflow.\n"
            "Auto: scan recent emails and rank by importance."
        )
        self.mode_combo.currentTextChanged.connect(self._on_mode_change)
        hl.addWidget(self.mode_combo)

        hl.addStretch()

        hl.addWidget(QLabel("Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["ollama"])
        self.provider_combo.setFixedWidth(110)
        self.provider_combo.currentTextChanged.connect(self._on_provider_change)
        hl.addWidget(self.provider_combo)

        hl.addWidget(QLabel("Account:"))
        self.account_combo = QComboBox()
        self.account_combo.setMinimumWidth(200)
        self.account_combo.activated.connect(self._on_account_activated)
        hl.addWidget(self.account_combo)
        self._refresh_accounts()

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("icon_button")
        settings_btn.setToolTip("Settings (Ctrl+,)")
        settings_btn.setFixedWidth(38)
        settings_btn.clicked.connect(self._open_settings)
        hl.addWidget(settings_btn)

        root.addWidget(header)
        root.addWidget(_divider())

        # ── Body ──────────────────────────────────────────────────────────
        body_wrap = QHBoxLayout()
        body_wrap.setContentsMargins(16, 16, 16, 16)
        body_wrap.setSpacing(0)
        root.addLayout(body_wrap)

        self.body_splitter = QSplitter(Qt.Horizontal)
        self.body_splitter.setChildrenCollapsible(False)
        left_widget = QWidget()
        left_widget.setLayout(self._left_panel())
        self.body_splitter.addWidget(left_widget)
        self.body_splitter.addWidget(self._right_tabs())
        self.body_splitter.setStretchFactor(0, 3)
        self.body_splitter.setStretchFactor(1, 2)
        self.body_splitter.setSizes([720, 480])
        body_wrap.addWidget(self.body_splitter)

    def _left_panel(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(10)

        self._input_label = _section_label("Input · drop files here")
        layout.addWidget(self._input_label)
        self.input_text = DropTextEdit()
        self.input_text.setPlaceholderText(
            "Paste text, drop .txt/.pdf files, upload files, or select an email…"
        )
        self.input_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_text.setMinimumHeight(140)
        self.input_text.files_dropped.connect(self._load_paths)
        layout.addWidget(self.input_text, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.file_button = QPushButton("⬆  Upload File(s)")
        self.file_button.clicked.connect(self.load_file)
        self.email_button = QPushButton("✉  Fetch Emails")
        self.email_button.clicked.connect(self.load_emails)
        self.sample_button = QPushButton("📄  Sample ▾")
        self.sample_button.setToolTip("Load a built-in demo document")
        self.sample_button.clicked.connect(self._show_sample_menu)
        btn_row.addWidget(self.file_button)
        btn_row.addWidget(self.email_button)
        btn_row.addWidget(self.sample_button)
        layout.addLayout(btn_row)
        self._input_buttons = [self.file_button, self.email_button, self.sample_button]

        self._left_divider = _divider()
        layout.addWidget(self._left_divider)
        self._workflow_label = _section_label("Workflow")
        layout.addWidget(self._workflow_label)
        self.workflow_selector = QComboBox()
        self.workflow_selector.addItems(["summary", "tasks", "insights", "compare"])
        layout.addWidget(self.workflow_selector)

        # Auto-mode descriptor that replaces the manual-mode controls
        self._auto_hint = QLabel(
            "Auto mode scans your most recent emails, ranks them by\n"
            "task urgency, and surfaces what needs your attention."
        )
        self._auto_hint.setObjectName("status_label")
        self._auto_hint.setWordWrap(True)
        self._auto_hint.setAlignment(Qt.AlignLeft)
        layout.addWidget(self._auto_hint)

        auto_window_row = QHBoxLayout()
        auto_window_row.setSpacing(8)
        self._auto_window_label = QLabel("Window:")
        self._auto_window_label.setObjectName("section_label")
        self.auto_window_combo = QComboBox()
        self.auto_window_combo.addItems(["4 hours", "12 hours", "24 hours", "48 hours"])
        self.auto_window_combo.setCurrentIndex(1)
        auto_window_row.addWidget(self._auto_window_label)
        auto_window_row.addWidget(self.auto_window_combo, 1)
        self._auto_window_row_widgets = [self._auto_window_label, self.auto_window_combo]
        layout.addLayout(auto_window_row)

        self.process_button = QPushButton("▶  Process   (Ctrl+Enter)")
        self.process_button.setObjectName("primary_button")
        self.process_button.setFixedHeight(44)
        self.process_button.clicked.connect(self.process_input)
        layout.addWidget(self.process_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        return layout

    def _right_tabs(self) -> QTabWidget:
        tabs = QTabWidget()
        self.tabs = tabs

        # ── Output tab ─────────────────────────────────────────────────────
        out_widget = QWidget()
        ol = QVBoxLayout(out_widget)
        ol.setSpacing(0)
        ol.setContentsMargins(8, 8, 8, 8)

        # Emails pane (top of vertical splitter)
        emails_pane = QWidget()
        ep = QVBoxLayout(emails_pane)
        ep.setSpacing(8)
        ep.setContentsMargins(0, 0, 0, 0)
        ep.addWidget(_section_label("Emails"))
        self.email_search = QLineEdit()
        self.email_search.setPlaceholderText(
            "Gmail search (e.g. from:boss@co is:unread subject:invoice) — Enter to search"
        )
        self.email_search.returnPressed.connect(self.load_emails)
        ep.addWidget(self.email_search)

        self.email_list = QListWidget()
        self.email_list.setMinimumHeight(80)
        self.email_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.email_list.itemClicked.connect(self.show_email_preview)
        ep.addWidget(self.email_list, 1)

        use_email_row = QHBoxLayout()
        use_email_row.addStretch()
        self.use_emails_btn = QPushButton("⬆  Use selected in input")
        self.use_emails_btn.clicked.connect(self._load_selected_emails)
        use_email_row.addWidget(self.use_emails_btn)
        ep.addLayout(use_email_row)

        # Output pane (bottom of vertical splitter)
        output_pane = QWidget()
        op = QVBoxLayout(output_pane)
        op.setSpacing(8)
        op.setContentsMargins(0, 0, 0, 0)
        op.addWidget(_section_label("Output"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Results will appear here…")
        self.output_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_text.setMinimumHeight(80)
        _justify = QTextOption()
        _justify.setAlignment(Qt.AlignJustify)
        _justify.setWrapMode(QTextOption.WordWrap)
        self.output_text.document().setDefaultTextOption(_justify)
        op.addWidget(self.output_text, 1)

        export_row = QHBoxLayout()
        export_row.setSpacing(8)
        self.export_txt_btn = QPushButton("⬇  Export TXT   (Ctrl+S)")
        self.export_txt_btn.clicked.connect(self._export_txt)
        self.export_txt_btn.setEnabled(False)
        self.export_csv_btn = QPushButton("⬇  Export CSV   (Ctrl+Shift+S)")
        self.export_csv_btn.clicked.connect(self._export_csv)
        self.export_csv_btn.setEnabled(False)
        export_row.addWidget(self.export_txt_btn)
        export_row.addWidget(self.export_csv_btn)
        op.addLayout(export_row)

        self.calendar_btn = QPushButton("📅  Push Tasks to Google Calendar")
        self.calendar_btn.setObjectName("success_button")
        self.calendar_btn.clicked.connect(self._push_to_calendar)
        self.calendar_btn.setVisible(False)
        op.addWidget(self.calendar_btn)

        self.output_splitter = QSplitter(Qt.Vertical)
        self.output_splitter.setChildrenCollapsible(False)
        self.output_splitter.addWidget(emails_pane)
        self.output_splitter.addWidget(output_pane)
        self.output_splitter.setStretchFactor(0, 1)
        self.output_splitter.setStretchFactor(1, 2)
        self.output_splitter.setSizes([280, 420])
        ol.addWidget(self.output_splitter)

        tabs.addTab(out_widget, "Output")

        # ── History tab ────────────────────────────────────────────────────
        hist_widget = QWidget()
        hl = QVBoxLayout(hist_widget)
        hl.setSpacing(10)
        hl.setContentsMargins(8, 8, 8, 8)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("🔍  Search history (workflow, text)…")
        self.history_search.textChanged.connect(self._filter_history)
        hl.addWidget(self.history_search)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self._load_history_item)
        hl.addWidget(self.history_list)

        clear_btn = QPushButton("Clear History")
        clear_btn.setObjectName("danger_button")
        clear_btn.clicked.connect(self._clear_history)
        hl.addWidget(clear_btn, alignment=Qt.AlignRight)

        tabs.addTab(hist_widget, "History")

        # ── Auto digest tab ───────────────────────────────────────────────
        auto_widget = QWidget()
        al = QVBoxLayout(auto_widget)
        al.setSpacing(10)
        al.setContentsMargins(8, 8, 8, 8)

        al.addWidget(_section_label("Inbox triage"))
        self.auto_summary_label = QLabel(
            "Switch to Auto mode and click Scan to triage your recent inbox."
        )
        self.auto_summary_label.setObjectName("status_label")
        self.auto_summary_label.setWordWrap(True)
        al.addWidget(self.auto_summary_label)

        self.auto_output = QTextEdit()
        self.auto_output.setReadOnly(True)
        self.auto_output.setPlaceholderText("Scan results will appear here…")
        self.auto_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        al.addWidget(self.auto_output)

        self.auto_push_btn = QPushButton("📅  Push all high/medium tasks to Calendar")
        self.auto_push_btn.setObjectName("success_button")
        self.auto_push_btn.clicked.connect(self._push_auto_tasks_to_calendar)
        self.auto_push_btn.setVisible(False)
        al.addWidget(self.auto_push_btn)

        self._auto_tab_index = tabs.addTab(auto_widget, "Auto")

        tabs.currentChanged.connect(lambda i: self._refresh_history() if i == 1 else None)

        return tabs

    # ── Keyboard shortcuts ─────────────────────────────────────────────────

    def _register_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.process_input)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self.process_input)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._export_txt)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, activated=self._export_csv)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.load_file)
        QShortcut(QKeySequence("Ctrl+E"), self, activated=self.load_emails)
        QShortcut(QKeySequence("Ctrl+,"), self, activated=self._open_settings)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: self.input_text.clear())

    # ── Settings ───────────────────────────────────────────────────────────

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            self.status_label.setText("Preferences saved.")

    # ── Mode ───────────────────────────────────────────────────────────────

    def _on_mode_change(self, label: str):
        self._mode = "auto" if label.lower() == "auto" else "manual"
        self._apply_mode()

    def _apply_mode(self):
        is_auto = self._mode == "auto"

        # Manual-only controls
        self._input_label.setVisible(not is_auto)
        self.input_text.setVisible(not is_auto)
        for btn in self._input_buttons:
            btn.setVisible(not is_auto)
        self._left_divider.setVisible(not is_auto)
        self._workflow_label.setVisible(not is_auto)
        self.workflow_selector.setVisible(not is_auto)

        # Auto-only controls
        self._auto_hint.setVisible(is_auto)
        for w in self._auto_window_row_widgets:
            w.setVisible(is_auto)

        # Process button label and tab focus
        if is_auto:
            self.process_button.setText("🔍  Scan recent emails")
            if hasattr(self, "tabs") and hasattr(self, "_auto_tab_index"):
                self.tabs.setCurrentIndex(self._auto_tab_index)
        else:
            self.process_button.setText("▶  Process   (Ctrl+Enter)")
            if hasattr(self, "tabs"):
                self.tabs.setCurrentIndex(0)

    # ── Provider ───────────────────────────────────────────────────────────

    def _on_provider_change(self, provider: str):
        set_provider(provider)
        self.status_label.setText(f"Provider: {provider}")

    # ── Accounts ───────────────────────────────────────────────────────────

    ADD_ACCOUNT_SENTINEL = "＋  Add account…"
    REMOVE_ACCOUNT_SENTINEL = "✕  Remove current account"

    def _refresh_accounts(self):
        self.account_combo.blockSignals(True)
        self.account_combo.clear()
        accounts = list_accounts()
        active = get_active_account()
        if accounts:
            self.account_combo.addItems(accounts)
            if active in accounts:
                self.account_combo.setCurrentIndex(accounts.index(active))
            self.account_combo.insertSeparator(len(accounts))
            self.account_combo.addItem(self.ADD_ACCOUNT_SENTINEL)
            self.account_combo.addItem(self.REMOVE_ACCOUNT_SENTINEL)
        else:
            self.account_combo.addItem("(no accounts)")
            self.account_combo.insertSeparator(1)
            self.account_combo.addItem(self.ADD_ACCOUNT_SENTINEL)
        self.account_combo.blockSignals(False)

    def _current_account(self) -> str | None:
        text = self.account_combo.currentText()
        if text in (self.ADD_ACCOUNT_SENTINEL, self.REMOVE_ACCOUNT_SENTINEL, "(no accounts)"):
            return get_active_account()
        return text or None

    def _on_account_activated(self, index: int):
        text = self.account_combo.itemText(index)
        if text == self.ADD_ACCOUNT_SENTINEL:
            self._start_add_account()
            return
        if text == self.REMOVE_ACCOUNT_SENTINEL:
            self._remove_current_account()
            return
        if text and text != "(no accounts)":
            try:
                set_active_account(text)
                self.status_label.setText(f"Active account: {text}")
            except Exception as e:
                self.status_label.setText(f"Could not switch account: {e}")
                self._refresh_accounts()

    def _start_add_account(self):
        self.status_label.setText("Opening Google sign-in in your browser…")
        self.account_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._add_worker = AddAccountWorker()
        self._add_worker.finished.connect(self._on_account_added)
        self._add_worker.error.connect(self._on_account_add_error)
        self._add_worker.start()

    def _on_account_added(self, email: str):
        self.progress_bar.setVisible(False)
        self.account_combo.setEnabled(True)
        self._refresh_accounts()
        self.status_label.setText(f"Signed in as {email}.")

    def _on_account_add_error(self, msg: str):
        self.progress_bar.setVisible(False)
        self.account_combo.setEnabled(True)
        self._refresh_accounts()
        QMessageBox.critical(self, "Sign-in failed", msg)
        self.status_label.setText("Sign-in failed.")

    def _remove_current_account(self):
        active = get_active_account()
        if not active:
            self._refresh_accounts()
            return
        reply = QMessageBox.question(
            self, "Remove account",
            f"Remove '{active}' from this app?\n"
            "You'll need to sign in again to use it.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            self._refresh_accounts()
            return
        try:
            remove_account(active)
            self.status_label.setText(f"Removed {active}.")
        except Exception as e:
            self.status_label.setText(f"Remove failed: {e}")
        self._refresh_accounts()

    # ── File loading ───────────────────────────────────────────────────────

    def load_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open File(s)", "", "Documents (*.txt *.pdf)"
        )
        if paths:
            self._load_paths(paths)

    def _load_paths(self, paths: list):
        texts = []
        for path in paths:
            try:
                if path.endswith(".txt"):
                    texts.append(read_text_file(path))
                elif path.endswith(".pdf"):
                    texts.append(read_pdf(path))
            except Exception as e:
                self.status_label.setText(f"Failed to load {os.path.basename(path)}: {e}")
                return
        if len(texts) > 1:
            # Separate documents for compare workflow
            combined = "\n\n--- DOCUMENT BREAK ---\n\n".join(texts)
        else:
            combined = "\n\n".join(texts)
        self.input_text.setText(combined)
        names = ", ".join(os.path.basename(p) for p in paths)
        self.status_label.setText(f"Loaded: {names}")

    # ── Sample documents ───────────────────────────────────────────────────

    def _show_sample_menu(self):
        menu = QMenu(self)
        for name, info in SAMPLES.items():
            action = QAction(name, self)
            action.setToolTip(info.get("hint", ""))
            action.triggered.connect(lambda _checked, n=name: self._load_sample(n))
            menu.addAction(action)
        # Anchor below the button
        menu.exec_(self.sample_button.mapToGlobal(self.sample_button.rect().bottomLeft()))

    def _load_sample(self, name: str):
        sample = SAMPLES.get(name)
        if not sample:
            return
        self.input_text.setText(sample["text"])
        workflow = sample.get("workflow")
        if workflow:
            idx = self.workflow_selector.findText(workflow)
            if idx >= 0:
                self.workflow_selector.setCurrentIndex(idx)
        self.status_label.setText(f"Loaded sample: {name}")

    # ── Email loading ──────────────────────────────────────────────────────

    SHOW_MORE_SENTINEL = "＋  Show more"
    EMAIL_PAGE_SIZE = 5

    def load_emails(self):
        self.emails_data = []
        self._emails_next_page_token = None
        self.email_list.clear()
        self._fetch_email_page(append=False)

    def _fetch_email_page(self, append: bool):
        self.email_button.setEnabled(False)
        self.email_button.setText("Loading…")
        try:
            page = get_latest_emails(
                max_results=self.EMAIL_PAGE_SIZE,
                account=self._current_account(),
                page_token=self._emails_next_page_token,
                query=(self.email_search.text().strip() or None),
            )
            new_emails = page["emails"]
            self._emails_next_page_token = page["next_page_token"]

            if not append:
                self.email_list.clear()
                self.emails_data = []

            # Remove previous "Show more" row if present (last item).
            if self.email_list.count():
                last = self.email_list.item(self.email_list.count() - 1)
                if last and last.text() == self.SHOW_MORE_SENTINEL:
                    self.email_list.takeItem(self.email_list.count() - 1)

            if not new_emails and not self.emails_data:
                self.email_list.addItem("No emails found.")
                return

            self.emails_data.extend(new_emails)
            for e in new_emails:
                self.email_list.addItem(
                    f"{e.get('subject','No Subject')}  ·  {e.get('sender','Unknown')}"
                )

            if self._emails_next_page_token:
                self.email_list.addItem(self.SHOW_MORE_SENTINEL)

            self.status_label.setText(f"{len(self.emails_data)} email(s) loaded.")
        except Exception as e:
            if not append:
                self.email_list.clear()
                self.email_list.addItem("Error loading emails.")
            self.status_label.setText(f"Email error: {e}")
        finally:
            self.email_button.setEnabled(True)
            self.email_button.setText("✉  Fetch Emails")

    def show_email_preview(self, item):
        if item.text() == self.SHOW_MORE_SENTINEL:
            self._fetch_email_page(append=True)
            return
        # Only preview when exactly one row is selected — otherwise let the user
        # build up a multi-selection without the input thrashing.
        if len(self.email_list.selectedItems()) > 1:
            return
        index = self.email_list.row(item)
        if index < 0 or index >= len(self.emails_data):
            return
        e = self.emails_data[index]
        self.input_text.setText(f"From: {e['sender']}\nSubject: {e['subject']}\n\n{e['body']}")

    def _load_selected_emails(self):
        rows = []
        for item in self.email_list.selectedItems():
            if item.text() == self.SHOW_MORE_SENTINEL:
                continue
            row = self.email_list.row(item)
            if 0 <= row < len(self.emails_data):
                rows.append(row)
        if not rows:
            self.status_label.setText("Select one or more emails first.")
            return
        rows.sort()
        chunks = []
        for row in rows:
            e = self.emails_data[row]
            chunks.append(
                f"From: {e['sender']}\nSubject: {e['subject']}\n\n{e['body']}"
            )
        separator = "\n\n--- DOCUMENT BREAK ---\n\n" if len(chunks) > 1 else "\n\n"
        self.input_text.setText(separator.join(chunks))
        self.status_label.setText(f"Loaded {len(chunks)} email(s) into input.")

    # ── Processing ─────────────────────────────────────────────────────────

    def process_input(self):
        # If a manual run is active, this acts as Cancel.
        if getattr(self, "worker", None) and self.worker.isRunning():
            self.worker.cancel()
            self.process_button.setText("Cancelling…")
            self.process_button.setEnabled(False)
            return
        # If an auto scan is active, this acts as Cancel.
        if getattr(self, "auto_worker", None) and self.auto_worker.isRunning():
            self.auto_worker.cancel()
            self.process_button.setText("Cancelling…")
            self.process_button.setEnabled(False)
            return

        if self._mode == "auto":
            self.start_auto_scan()
            return

        text = self.input_text.toPlainText().strip()
        if not text:
            self.status_label.setText("⚠  Please enter or load some text first.")
            return
        self._last_workflow = self.workflow_selector.currentText()
        self.process_button.setText("■  Cancel")
        self.export_txt_btn.setEnabled(False)
        self.export_csv_btn.setEnabled(False)
        self.calendar_btn.setVisible(False)
        self.progress_bar.setRange(0, 0)  # indeterminate until first progress event
        self.progress_bar.setVisible(True)
        self.status_label.setText("Running workflow…")
        self.output_text.clear()

        self.worker = Worker(text, self._last_workflow)
        self.worker.finished.connect(lambda r: self._on_result(r, text))
        self.worker.error.connect(self._on_error)
        self.worker.cancelled.connect(self._on_cancelled)
        self.worker.progress.connect(self._on_progress)
        self.worker.start()

    def _on_progress(self, current: int, total: int):
        # Switch the bar to determinate mode the first time we know the total.
        if self.progress_bar.maximum() != total:
            self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        if current == 0:
            self.status_label.setText(f"Processing {total} chunk{'s' if total != 1 else ''}…")
        else:
            self.status_label.setText(f"Processing chunk {current} / {total}…")

    def _reset_progress(self):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)

    def _on_cancelled(self):
        self._reset_progress()
        self.output_text.setText("")
        self.status_label.setText("Cancelled.")
        self.process_button.setText("▶  Process   (Ctrl+Enter)")
        self.process_button.setEnabled(True)

    def _on_result(self, result: dict, original_text: str):
        self._last_result = result
        self._reset_progress()

        if "error" in result:
            self.output_text.setText(f"Error: {result['error']}")
            self.status_label.setText("Processing failed.")
        else:
            self.output_text.setText(self._format_result(result))
            self.export_txt_btn.setEnabled(True)
            self.export_csv_btn.setEnabled(True)
            if result.get("action_items"):
                self.calendar_btn.setVisible(True)
            self.status_label.setText("Done.")
            record(self._last_workflow, original_text, result)

        self.process_button.setText("▶  Process   (Ctrl+Enter)")
        self.process_button.setEnabled(True)

    def _format_bullet(self, item) -> list:
        """Render one bullet, gracefully handling both plain strings and the
        structured dicts the LLM sometimes returns for compare-style outputs.
        """
        if isinstance(item, str):
            return [f"  •  {item.strip()}"]
        if isinstance(item, dict):
            # Heuristic header: a "text"/"topic"/"title" field describing what's being compared.
            header = (
                item.get("text")
                or item.get("topic")
                or item.get("title")
                or item.get("aspect")
            )
            # Side-by-side answers under arbitrary key naming.
            a = item.get("option_a") or item.get("a") or item.get("doc_a") or item.get("document_a")
            b = item.get("option_b") or item.get("b") or item.get("doc_b") or item.get("document_b")
            if header and (a or b):
                out = [f"  •  {str(header).strip()}"]
                if a:
                    out.append(f"        A: {str(a).strip()}")
                if b:
                    out.append(f"        B: {str(b).strip()}")
                return out
            # Generic dict — flatten scalar key/values, skip noise.
            parts = [
                f"{k}: {v}"
                for k, v in item.items()
                if isinstance(v, (str, int, float, bool)) and str(v).strip()
            ]
            if parts:
                return [f"  •  {' · '.join(parts)}"]
        return [f"  •  {item}"]

    def _format_result(self, result: dict) -> str:
        lines = []
        summary = result.get("summary")
        if isinstance(summary, list):
            points = [p.strip() for p in summary if isinstance(p, str) and p.strip()]
            if points:
                lines += ["📝  SUMMARY", "─" * 40]
                for p in points:
                    lines += [f"  •  {p}", ""]
        elif isinstance(summary, str) and summary.strip():
            lines += ["📝  SUMMARY", "─" * 40, summary.strip(), ""]
        if result.get("common_themes"):
            lines += ["🔗  COMMON THEMES", "─" * 40]
            for t in result["common_themes"]:
                lines += self._format_bullet(t) + [""]
        if result.get("differences"):
            lines += ["🔀  DIFFERENCES", "─" * 40]
            for d in result["differences"]:
                lines += self._format_bullet(d) + [""]
        if result.get("key_insights"):
            lines += ["🧠  INSIGHTS", "─" * 40]
            for i in result["key_insights"]:
                lines += self._format_bullet(i) + [""]
        if result.get("action_items"):
            lines += ["📋  TASKS", "─" * 40]
            for task in result["action_items"]:
                lines.append(f"  •  {task['task']}")
                lines.append(f"     Priority: {task.get('priority','N/A')}   Deadline: {task.get('deadline','N/A')}")
            lines.append("")
        elif "action_items" in result and result.get("source_type") == "non_actionable":
            lines += [
                "ℹ  No tasks found.",
                "",
                "This content looks like narrative, discussion, or reference",
                "material rather than instructions addressed to you.",
                "",
            ]
        elif "action_items" in result:
            lines += ["ℹ  No tasks found in this content.", ""]
        return "\n".join(lines)

    def _on_error(self, msg: str):
        self._reset_progress()
        self.output_text.setText(f"Error: {msg}")
        self.status_label.setText("Processing failed.")
        self.process_button.setText("▶  Process   (Ctrl+Enter)")
        self.process_button.setEnabled(True)

    # ── Auto scan ──────────────────────────────────────────────────────────

    AUTO_MAX_EMAILS = 8

    def _auto_window_hours(self) -> int:
        text = self.auto_window_combo.currentText()
        # "12 hours" → 12
        try:
            return int(text.split()[0])
        except (ValueError, IndexError):
            return 12

    def start_auto_scan(self):
        if not self._current_account():
            self.status_label.setText("Sign in to an account first (top-right).")
            self.auto_output.setPlainText(
                "No Google account is connected.\n\n"
                "Click the Account dropdown in the header to add one — Auto mode "
                "needs Gmail access to scan your inbox."
            )
            return

        hours = self._auto_window_hours()
        self.auto_output.clear()
        self.auto_push_btn.setVisible(False)
        self._auto_results = []
        self.auto_summary_label.setText(f"Fetching emails from the past {hours} hours…")
        self.process_button.setText("■  Cancel")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning…")
        if hasattr(self, "tabs") and hasattr(self, "_auto_tab_index"):
            self.tabs.setCurrentIndex(self._auto_tab_index)

        self.auto_worker = AutoScanWorker(
            window_hours=hours,
            max_emails=self.AUTO_MAX_EMAILS,
            account=self._current_account(),
        )
        self.auto_worker.progress.connect(self._on_auto_progress)
        self.auto_worker.finished.connect(self._on_auto_finished)
        self.auto_worker.error.connect(self._on_auto_error)
        self.auto_worker.cancelled.connect(self._on_auto_cancelled)
        self.auto_worker.start()

    def _on_auto_progress(self, current: int, total: int, subject: str):
        if total <= 0:
            return
        if self.progress_bar.maximum() != total:
            self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        if current == 0:
            self.status_label.setText(f"Analysing {total} email{'s' if total != 1 else ''}…")
        else:
            short = (subject[:50] + "…") if len(subject) > 50 else subject
            self.status_label.setText(f"Email {current} / {total} — {short}")

    def _on_auto_finished(self, results: list):
        self._auto_results = results
        self._reset_progress()
        self.process_button.setText("🔍  Scan recent emails")
        self.process_button.setEnabled(True)
        self._render_auto_results(results)
        self.status_label.setText(f"Done. {len(results)} email(s) analysed.")

    def _on_auto_error(self, msg: str):
        self._reset_progress()
        self.process_button.setText("🔍  Scan recent emails")
        self.process_button.setEnabled(True)
        self.auto_output.setPlainText(f"Scan failed: {msg}")
        self.auto_summary_label.setText("Scan failed.")
        self.status_label.setText("Scan failed.")

    def _on_auto_cancelled(self):
        self._reset_progress()
        self.process_button.setText("🔍  Scan recent emails")
        self.process_button.setEnabled(True)
        self.auto_summary_label.setText("Scan cancelled.")
        self.status_label.setText("Cancelled.")

    _TIER_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢", "none": "⚪"}
    _TIER_LABEL = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW", "none": "FYI"}

    def _render_auto_results(self, results: list):
        if not results:
            self.auto_output.setPlainText(
                "No emails found in the selected window.\n\n"
                "Try widening the window, or check that the active account is correct."
            )
            self.auto_summary_label.setText("No emails in window.")
            return

        counts = {"high": 0, "medium": 0, "low": 0, "none": 0}
        for r in results:
            counts[r["tier"]] = counts.get(r["tier"], 0) + 1
        self.auto_summary_label.setText(
            f"{len(results)} email(s) · 🔴 {counts['high']} high · "
            f"🟡 {counts['medium']} medium · 🟢 {counts['low']} low · ⚪ {counts['none']} FYI"
        )

        lines = []
        for r in results:
            email = r["email"]
            tier = r["tier"]
            score = r["score"]
            subject = email.get("subject") or "(no subject)"
            sender = email.get("sender") or ""
            icon = self._TIER_ICON.get(tier, "⚪")
            label = self._TIER_LABEL.get(tier, "FYI")
            lines.append(f"{icon}  {label} (score {score}) — {subject}")
            lines.append(f"     From: {sender}")
            reason = (r["result"].get("reason") if isinstance(r["result"], dict) else "") or ""
            if reason:
                lines.append(f"     “{reason}”")
            tasks = (r["result"].get("action_items") if isinstance(r["result"], dict) else []) or []
            if not tasks:
                if "error" in (r["result"] or {}):
                    lines.append(f"     (analysis error: {r['result']['error']})")
                elif not reason:
                    lines.append("     (no tasks detected)")
            else:
                for t in tasks:
                    prio = (t.get("priority") or "n/a").strip()
                    deadline = (t.get("deadline") or "no deadline").strip()
                    lines.append(f"     • {t.get('task','(unnamed task)')}  ({prio} · {deadline})")
            lines.append("")
        self.auto_output.setPlainText("\n".join(lines).rstrip())

        # Offer to push every actionable task from high/medium tier emails
        actionable = self._collect_auto_tasks(tiers=("high", "medium"))
        self.auto_push_btn.setVisible(bool(actionable))
        if actionable:
            self.auto_push_btn.setText(
                f"📅  Push {len(actionable)} high/medium task(s) to Calendar"
            )

    def _collect_auto_tasks(self, tiers=("high", "medium")) -> list:
        out = []
        for r in self._auto_results:
            if r["tier"] not in tiers:
                continue
            tasks = (r["result"].get("action_items") if isinstance(r["result"], dict) else []) or []
            out.extend(tasks)
        return out

    def _push_auto_tasks_to_calendar(self):
        tasks = self._collect_auto_tasks(tiers=("high", "medium"))
        if not tasks:
            return
        dialog = TaskReviewDialog(tasks, parent=self)
        if not dialog.exec_():
            return
        approved = dialog.approved_tasks()
        if not approved:
            self.status_label.setText("No tasks selected.")
            return
        self.auto_push_btn.setEnabled(False)
        self.auto_push_btn.setText(f"Creating {len(approved)} event(s)…")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.cal_worker = CalendarWorker(approved, account=self._current_account())
        self.cal_worker.finished.connect(self._on_auto_calendar_done)
        self.cal_worker.error.connect(self._on_auto_calendar_error)
        self.cal_worker.start()

    def _on_auto_calendar_done(self, stats: dict):
        self._reset_progress()
        self.auto_push_btn.setEnabled(True)
        actionable = self._collect_auto_tasks(tiers=("high", "medium"))
        self.auto_push_btn.setText(
            f"📅  Push {len(actionable)} high/medium task(s) to Calendar"
        )
        msg = f"Created {stats['created']} event(s)."
        if stats.get("failed"):
            msg += f" {stats['failed']} failed."
        self.status_label.setText(msg)
        QMessageBox.information(self, "Calendar", msg)

    def _on_auto_calendar_error(self, msg: str):
        self._reset_progress()
        self.auto_push_btn.setEnabled(True)
        actionable = self._collect_auto_tasks(tiers=("high", "medium"))
        self.auto_push_btn.setText(
            f"📅  Push {len(actionable)} high/medium task(s) to Calendar"
        )
        self.status_label.setText(f"Calendar error: {msg}")
        QMessageBox.critical(self, "Calendar Error", msg)

    # ── Calendar ───────────────────────────────────────────────────────────

    def _push_to_calendar(self):
        tasks = self._last_result.get("action_items") or []
        if not tasks:
            return
        dialog = TaskReviewDialog(tasks, parent=self)
        if not dialog.exec_():
            return
        approved = dialog.approved_tasks()
        if not approved:
            self.status_label.setText("No tasks selected.")
            return

        self.calendar_btn.setEnabled(False)
        self.calendar_btn.setText(f"Creating {len(approved)} event(s)…")
        self.progress_bar.setVisible(True)

        self.cal_worker = CalendarWorker(approved, account=self._current_account())
        self.cal_worker.finished.connect(self._on_calendar_done)
        self.cal_worker.error.connect(self._on_calendar_error)
        self.cal_worker.start()

    def _on_calendar_done(self, stats: dict):
        self.progress_bar.setVisible(False)
        self.calendar_btn.setEnabled(True)
        self.calendar_btn.setText("📅  Push Tasks to Google Calendar")
        msg = f"Created {stats['created']} event(s)."
        if stats["failed"]:
            msg += f" {stats['failed']} failed."
        self.status_label.setText(msg)
        QMessageBox.information(self, "Calendar", msg)

    def _on_calendar_error(self, msg: str):
        self.progress_bar.setVisible(False)
        self.calendar_btn.setEnabled(True)
        self.calendar_btn.setText("📅  Push Tasks to Google Calendar")
        self.status_label.setText(f"Calendar error: {msg}")
        QMessageBox.critical(self, "Calendar Error", msg)

    # ── Export ─────────────────────────────────────────────────────────────

    def _export_txt(self):
        if not self._last_result or "error" in self._last_result:
            return
        directory = QFileDialog.getExistingDirectory(self, "Choose Export Folder")
        if not directory:
            return
        try:
            path = export_txt(self._last_result, self._last_workflow, directory)
            self.status_label.setText(f"Saved: {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")

    def _export_csv(self):
        if not self._last_result or "error" in self._last_result:
            return
        directory = QFileDialog.getExistingDirectory(self, "Choose Export Folder")
        if not directory:
            return
        try:
            path = export_csv(self._last_result, self._last_workflow, directory)
            self.status_label.setText(f"Saved: {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")

    # ── History ────────────────────────────────────────────────────────────

    def _refresh_history(self):
        self.history_list.clear()
        try:
            self._history_data = fetch(50)
            if not self._history_data:
                self.history_list.addItem("No history yet.")
                return
            self._render_history(self._history_data)
        except Exception as e:
            self.history_list.addItem(f"Error loading history: {e}")

    def _render_history(self, items: list):
        self.history_list.clear()
        for item in items:
            preview = item["input_preview"] or ""
            label = f"[{item['timestamp'][:16]}]  {item['workflow'].upper()}  —  {preview[:60]}"
            self.history_list.addItem(label)

    def _filter_history(self, query: str):
        query = query.lower().strip()
        if not query:
            self._render_history(self._history_data)
            return
        filtered = [
            item for item in self._history_data
            if query in item["workflow"].lower()
            or query in (item["input_preview"] or "").lower()
        ]
        if not filtered:
            self.history_list.clear()
            self.history_list.addItem("No matches.")
        else:
            self._render_history(filtered)

    def _load_history_item(self, item):
        row = self.history_list.row(item)
        # Map row back via current filter
        query = self.history_search.text().lower().strip()
        source = (
            [x for x in self._history_data
             if query in x["workflow"].lower()
             or query in (x["input_preview"] or "").lower()]
            if query else self._history_data
        )
        if row >= len(source):
            return
        entry = source[row]
        self._last_result = entry["result"]
        self._last_workflow = entry["workflow"]
        self.output_text.setText(self._format_result(entry["result"]))
        self.export_txt_btn.setEnabled(True)
        self.export_csv_btn.setEnabled(True)
        self.calendar_btn.setVisible(bool(entry["result"].get("action_items")))
        self.status_label.setText(f"Loaded from history: {entry['timestamp'][:16]}")

    def _clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History", "Delete all history entries?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            purge()
            self._refresh_history()


def run_app():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
