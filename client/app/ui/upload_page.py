from pathlib import Path

from PySide2.QtCore import QThread, Signal
from PySide2.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from app.api.api_client import ApiClient
from app.workers.upload_worker import UploadWorker


class UploadPage(QWidget):
    uploaded = Signal()

    def __init__(self, api_client: ApiClient) -> None:
        super().__init__()
        self.api_client = api_client
        self.file_path: Path | None = None
        self.threads: list[QThread] = []

        self.page_title = QLabel("Upload Track")
        self.page_title.setObjectName("PageTitle")
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("MutedLabel")
        self.choose_button = QPushButton("Choose")
        self.title = QLineEdit()
        self.artist = QLineEdit()
        self.album = QLineEdit()
        self.genre = QLineEdit()
        self.upload_button = QPushButton("Upload")
        self.status = QLabel("")
        self.status.setObjectName("MutedLabel")
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.hide()
        self.choose_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.upload_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.upload_button.setObjectName("PrimaryButton")

        file_row = QHBoxLayout()
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(self.choose_button)

        form = QFormLayout()
        form.addRow("File", file_row)
        form.addRow("Title", self.title)
        form.addRow("Artist", self.artist)
        form.addRow("Album", self.album)
        form.addRow("Genre", self.genre)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self.page_title)
        layout.addLayout(form)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addStretch(1)

        self.choose_button.clicked.connect(self.choose_file)
        self.upload_button.clicked.connect(self.upload)

    def choose_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Choose audio file", "", "Audio (*.mp3 *.wav *.flac *.ogg *.m4a)")
        if filename:
            self.file_path = Path(filename)
            self.file_label.setText(self.file_path.name)
            if not self.title.text():
                self.title.setText(self.file_path.stem)

    def upload(self) -> None:
        if not self.file_path or not self.title.text().strip():
            QMessageBox.warning(self, "Eureka Music", "Choose a file and enter a title.")
            return
        thread = QThread(self)
        worker = UploadWorker(
            self.api_client,
            self.file_path,
            self.title.text().strip(),
            self.artist.text().strip() or None,
            self.album.text().strip() or None,
            self.genre.text().strip() or None,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self.upload_success)
        worker.failed.connect(self.upload_failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self._forget_thread(thread))
        self.threads.append(thread)
        self.upload_button.setEnabled(False)
        self.progress.setRange(0, 0)
        self.progress.show()
        self.status.setText("Uploading...")
        thread.start()

    def upload_success(self, payload: dict) -> None:
        self.status.setText(f"Uploaded {payload.get('title', 'track')}")
        self.progress.hide()
        self.upload_button.setEnabled(True)
        self.uploaded.emit()

    def upload_failed(self, message: str) -> None:
        self.status.setText("Upload failed")
        self.progress.hide()
        self.upload_button.setEnabled(True)
        QMessageBox.warning(self, "Eureka Music", message)

    def _forget_thread(self, thread: QThread) -> None:
        if thread in self.threads:
            self.threads.remove(thread)
