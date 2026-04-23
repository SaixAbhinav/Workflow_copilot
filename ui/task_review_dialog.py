from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QHeaderView, QLabel, QAbstractItemView,
)
from PyQt5.QtCore import Qt


class TaskReviewDialog(QDialog):
    """Let the user edit/remove tasks before pushing to Google Calendar."""

    PRIORITIES = ["high", "medium", "low"]

    def __init__(self, action_items: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Review tasks before pushing to Calendar")
        self.resize(780, 440)
        self._build_ui()
        self._populate(action_items)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        root.addWidget(QLabel(
            "Review each task below. Edit title, deadline, or priority. "
            "Uncheck a row to skip it."
        ))

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["", "Task", "Deadline", "Priority"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 32)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        root.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        push_btn = QPushButton("Push to Calendar")
        push_btn.setObjectName("success_button")
        push_btn.setDefault(True)
        push_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(push_btn)
        root.addLayout(btn_row)

    def _populate(self, items: list[dict]):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check.setCheckState(Qt.Checked)
            self.table.setItem(row, 0, check)

            self.table.setItem(row, 1, QTableWidgetItem(item.get("task", "")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("deadline", "") or ""))

            combo = QComboBox()
            combo.addItems(self.PRIORITIES)
            current = (item.get("priority") or "medium").lower()
            if current not in self.PRIORITIES:
                current = "medium"
            combo.setCurrentText(current)
            self.table.setCellWidget(row, 3, combo)

    def approved_tasks(self) -> list[dict]:
        out = []
        for row in range(self.table.rowCount()):
            check = self.table.item(row, 0)
            if check.checkState() != Qt.Checked:
                continue
            task = (self.table.item(row, 1).text() or "").strip()
            if not task:
                continue
            deadline = (self.table.item(row, 2).text() or "").strip()
            priority = self.table.cellWidget(row, 3).currentText()
            out.append({"task": task, "deadline": deadline, "priority": priority})
        return out
