import json
import logging
import os
import threading
import time
import traceback

import psutil
import qtawesome as qta
from PyQt6.QtCore import QProcess, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QLabel, QListWidgetItem, QMessageBox, QWidget
from result import is_ok
from ui_game_monitor import Ui_GameMonitor

from fmcllib import show_qerrormessage
from fmcllib.game import Instance, get_launch_args, get_launch_program


class GameMonitor(QWidget, Ui_GameMonitor):
    _launchArgsGot = pyqtSignal(list)

    def __init__(self, instance_path: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(qta.icon("mdi6.rocket-launch-outline"))
        self.setWindowTitle(f"{self.windowTitle()}: {instance_path}")
        self.instance = Instance(instance_path)

        self.level_color = {
            "DEBUG": "#eee9e0",
            "INFO": "#ffffff",
            "WARN": "#ffeecc",
            "ERROR": "#ffccbb",
            "FATAL": "#f7a699",
        }
        self.level_count = {level: 0 for level in self.level_color}
        for level, color in self.level_color.items():
            label = QLabel()
            label.setText(f"0 {level.lower()}s")
            label.setStyleSheet(
                f"""QLabel{{background-color:{color};border: 1px solid black;}}"""
            )
            setattr(self, level, label)
            self.counter_layout.addWidget(label)

        self.process = QProcess()
        self.process.readyRead.connect(self.addLog)
        self.process.started.connect(self.recordStart)
        self.process.finished.connect(self.recordEnd)
        self.process.setWorkingDirectory(self.instance.game_directory)

        self._launchArgsGot.connect(self.launch)

        QApplication.instance().aboutToQuit.connect(self.onAppAboutToQuit)

        threading.Thread(
            target=lambda: (
                self._launchArgsGot.emit(args.ok_value)
                if is_ok(args := get_launch_args(instance_path))
                else show_qerrormessage(
                    self.tr(f"无法运行: {instance_path}"), args.err_value, self
                )
            ),
            daemon=True,
        ).start()

    def launch(self, args: list[str]):
        logging.info(f"运行'{self.instance.path}': {args}")
        program = get_launch_program(self.instance.path)
        if not program:
            QMessageBox.critical(
                None,  # 防止嵌入时出现bug
                self.tr(f"无法运行'{self.instance.path}'"),
                self.tr("没有合适的Java"),
            )
            return
        self.process.start(program, args)
        self.process.waitForStarted()

        self.p_process = psutil.Process(self.process.processId())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePerformance)
        self.timer.start(1000)

    def addLog(self):
        try:
            log = self.process.readLine()
            while log:
                log = log.data().decode().rstrip()

                item = QListWidgetItem()
                item.setText(log)
                for level, color in self.level_color.items():
                    if level in log:
                        item.setBackground(QColor(color))
                        self.level_count[level] += 1
                        getattr(self, level).setText(
                            f"{self.level_count[level]} {level.lower()}s"
                        )
                        break
                self.log_viewer.addItem(item)
                if self.auto_scroll.isChecked():
                    self.log_viewer.scrollToBottom()

                log = self.process.readLine()
        except:
            logging.error(traceback.format_exc())

    def updatePerformance(self):
        try:
            performance = [
                f"{self.tr('CPU使用率')}: {round(self.p_process.cpu_percent()/ psutil.cpu_count(),1)}%",
                f"{self.tr('内存使用率')}: {round(self.p_process.memory_percent(),1)}%({round(self.p_process.memory_info().rss/1024/1024,1)}MB)",
            ]
            self.performance.setText(", ".join(performance))
        except:
            self.timer.stop()
            self.performance.setText(self.tr("游戏已结束"))

    @pyqtSlot(bool)
    def on_kill_button_clicked(self, _):
        self.process.kill()
        self.process.waitForFinished()

    def recordStart(self):
        self.start = time.time()

        record_path = self.instance.time_record_path
        os.makedirs(os.path.dirname(record_path), exist_ok=True)

        records = self.instance.time_records
        self.record_index = len(records)

        records.append({"start": self.start, "end": self.start})
        json.dump(records, open(record_path, mode="w", encoding="utf-8"), indent=4)

    def recordEnd(self):
        self.end = time.time()

        if not hasattr(self, "record_index"):
            return

        records = self.instance.time_records
        records[self.record_index]["end"] = self.end

        json.dump(
            records,
            open(self.instance.time_record_path, mode="w", encoding="utf-8"),
            indent=4,
        )

    def onAppAboutToQuit(self):
        # 等待游戏结束
        try:
            self.process.readyRead.disconnect(self.addLog)
            while self.p_process.is_running():
                pass
            # 保证能够记录结束时间, 即使重复调用也没关系
            self.recordEnd()
        except:
            pass
