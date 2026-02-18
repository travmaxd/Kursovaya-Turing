import os
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLineEdit, QTextEdit,
    QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QGroupBox, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")

def init_db():
    """Создать базу данных для хранения истории, если она не существует."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            result TEXT NOT NULL,
            is_palindrome INTEGER NOT NULL,
            steps INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


class DatabaseViewer(QDialog):
    """Окно для просмотра базы данных"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История проверок - База данных")
        self.setGeometry(200, 200, 800, 500)
        
        layout = QVBoxLayout()
        
        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Слово", "Результат", "Шаги", "Дата проверки"])
        
        # Настройка внешнего вида таблицы
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить")
        self.close_btn = QPushButton("Закрыть")
        
        self.refresh_btn.clicked.connect(self.load_data)
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из базы"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, word, result, steps, created_at 
                FROM history 
                ORDER BY created_at DESC
            """)
            data = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.table.setItem(row_idx, col_idx, item)
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")


class CompactTuringAppGUI(QWidget):
    """Минималистичный GUI для машины Тьюринга, с сохранением истории.
       Параметр animate_head=False отключает «движение» (подсветку текущего символа/стрелки).
    """
    def __init__(self, machine, animate_head: bool = True):
        super().__init__()
        self.machine = machine
        self.animate_head = animate_head
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_step)
        self.steps_count = 0
        self.is_loaded = False
        self.last_action = ""
        self.completion_shown = False  # Флаг для отслеживания показа завершения

        self.init_ui()
        self.apply_clean_styles()

    # ========================== ИНИЦИАЛИЗАЦИЯ UI ==============================
    def init_ui(self):
        self.setWindowTitle("Машина Тьюринга — Палиндром")
        self.setGeometry(100, 100, 900, 700)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Ввод слова
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите слово для проверки")
        self.input_field.setMinimumHeight(40)

        self.load_btn = QPushButton("Загрузить слово")
        self.load_btn.setMinimumHeight(40)

        input_layout.addWidget(QLabel("Слово:"))
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.load_btn)
        main_layout.addLayout(input_layout)

        # --- Кнопки управления
        control_layout = QHBoxLayout()
        self.step_btn = QPushButton("Шаг")
        self.run_btn = QPushButton("Автоматически")
        self.stop_btn = QPushButton("Стоп")
        self.reset_btn = QPushButton("Сброс")

        for btn in [self.step_btn, self.run_btn, self.stop_btn, self.reset_btn]:
            btn.setMinimumHeight(35)
            btn.setMinimumWidth(140)
            btn.setEnabled(False)
            control_layout.addWidget(btn)

        control_layout.addStretch()
        self.steps_label = QLabel("Шагов выполнено: 0")
        self.steps_label.setStyleSheet("font-weight: 500; color: #2c3e50; font-size: 13px;")
        control_layout.addWidget(self.steps_label)
        main_layout.addLayout(control_layout)

        # --- Кнопка показа базы данных
        db_layout = QHBoxLayout()
        self.show_db_btn = QPushButton("Показать базу данных")
        self.show_db_btn.setMinimumHeight(35)
        
        db_layout.addWidget(self.show_db_btn)
        db_layout.addStretch()
        
        main_layout.addLayout(db_layout)

        # --- Лента
        tape_group = QGroupBox("Лента машины Тьюринга")
        tape_layout = QVBoxLayout(tape_group)

        tape_scroll = QScrollArea()
        tape_scroll.setMinimumHeight(130)
        tape_scroll.setMaximumHeight(150)
        tape_scroll.setWidgetResizable(True)

        self.tape_widget = QWidget()
        self.tape_layout = QHBoxLayout(self.tape_widget)
        self.tape_layout.setAlignment(Qt.AlignLeft)
        self.tape_layout.setSpacing(3)
        tape_scroll.setWidget(self.tape_widget)
        tape_layout.addWidget(tape_scroll)
        main_layout.addWidget(tape_group)

        # --- Результат
        self.result_label = QLabel("Результат: Введите слово и нажмите 'Загрузить слово'")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            padding: 15px; background: #f8f9fa;
            border: 1px solid #e9ecef; border-radius: 6px;
            font-weight: 500; font-size: 14px;
        """)
        main_layout.addWidget(self.result_label)

        # --- Лог
        log_group = QGroupBox("Журнал выполнения")
        log_layout = QVBoxLayout(log_group)
        self.log_display = QTextEdit()
        self.log_display.setFont(QFont("Segoe UI", 10))
        log_layout.addWidget(self.log_display)
        self.clear_log_btn = QPushButton("Очистить журнал")
        log_layout.addWidget(self.clear_log_btn)
        main_layout.addWidget(log_group, 1)

        self.setLayout(main_layout)

        # Подключение сигналов
        self.load_btn.clicked.connect(self.load_word)
        self.step_btn.clicked.connect(self.do_step)
        self.run_btn.clicked.connect(self.start_auto)
        self.stop_btn.clicked.connect(self.stop_auto)
        self.reset_btn.clicked.connect(self.reset_machine)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.show_db_btn.clicked.connect(self.show_database)
        self.input_field.returnPressed.connect(self.load_word)

    # ========================== ЛЕНТА ==============================
    def create_tape_cell(self, symbol, index, is_current=False):
        cell = QWidget()
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        index_label = QLabel(str(index))
        index_label.setAlignment(Qt.AlignCenter)
        index_label.setStyleSheet("color: #6c757d; font-size: 10px;")
        symbol_label = QLabel(symbol)
        symbol_label.setAlignment(Qt.AlignCenter)
        symbol_label.setMinimumSize(35, 35)

        # показываем подсветку только если включена анимация и это текущая позиция
        if is_current and self.animate_head:
            symbol_label.setStyleSheet("border:2px solid #e74c3c; color:#e74c3c; font-weight:600;")
            head_label = QLabel("▼")
            head_label.setAlignment(Qt.AlignCenter)
            head_label.setStyleSheet("color:#e74c3c; font-size:12px;")
            layout.addWidget(index_label)
            layout.addWidget(symbol_label)
            layout.addWidget(head_label)
        else:
            symbol_label.setStyleSheet("border:1px solid #bdc3c7; color:#2c3e50;")
            layout.addWidget(index_label)
            layout.addWidget(symbol_label)
        return cell

    def update_tape_display(self):
        for i in reversed(range(self.tape_layout.count())):
            item = self.tape_layout.itemAt(i)
            if item is None:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

        if not self.is_loaded:
            msg = QLabel("Загрузите слово для отображения ленты")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet("color: #6c757d; font-style: italic;")
            self.tape_layout.addWidget(msg)
            return

        tape_str = str(self.machine.tape)
        for i, sym in enumerate(tape_str):
            s = "_" if sym == "⊔" else sym
            is_current = (i == self.machine.head)
            # если анимация отключена, передаём False
            self.tape_layout.addWidget(self.create_tape_cell(s, i, is_current))
        self.tape_layout.addStretch()

    # ========================== СТИЛИ ==============================
    def apply_clean_styles(self):
        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI'; background: white; }
            QPushButton {
                background: #3498db; color: white; border-radius: 6px;
                padding: 8px; font-weight: 500;
            }
            QPushButton:hover { background: #2980b9; }
            QPushButton:disabled { background: #bdc3c7; }
            QLineEdit {
                border: 1px solid #bdc3c7; border-radius: 6px; padding: 8px;
            }
            QTextEdit { border: 1px solid #bdc3c7; border-radius: 6px; padding: 10px; }
        """)

    # ========================== ЛОГИКА ==============================
    def load_word(self):
        word = self.input_field.text().strip()
        if not word:
            self.show_message("Ошибка", "Введите слово для проверки!", QMessageBox.Warning)
            return
        
        self.completion_shown = False  # Сбрасываем флаг при загрузке нового слова
        self.machine.load_tape(word)
        self.steps_count = 0
        self.is_loaded = True
        
        for btn in [self.step_btn, self.run_btn, self.stop_btn]:
            btn.setEnabled(True)
            
        self.update_tape_display()
        self.update_display(f"Загружено слово: {word}")

    def do_step(self):
        if not self.is_loaded: 
            return
            
        # Если уже показали завершение, больше не выполняем шаги
        if self.completion_shown:
            return
            
        if self.machine.is_halted():
            self.show_completion_message()
            return
            
        action = self.machine.step()
        self.steps_count += 1
        self.update_tape_display()
        self.update_steps_counter()
        self.update_state_info()
        self.update_display(f"Шаг {self.steps_count}: {action}")
        
        if self.machine.is_halted():
            self.show_completion_message()

    def start_auto(self):
        if not self.is_loaded or self.completion_shown: 
            return
            
        self.timer.start(800)
        self.run_btn.setEnabled(False)
        self.step_btn.setEnabled(False)

    def stop_auto(self):
        self.timer.stop()
        self.run_btn.setEnabled(True)
        self.step_btn.setEnabled(True)

    def auto_step(self):
        if self.machine.is_halted() or self.completion_shown:
            self.stop_auto()
            if not self.completion_shown:
                self.show_completion_message()
            return
            
        self.do_step()

    def reset_machine(self):
        self.timer.stop()
        self.machine.reset()
        self.steps_count = 0
        self.is_loaded = False
        self.completion_shown = False  # Сбрасываем флаг при сбросе
        
        self.update_tape_display()
        self.update_steps_counter()
        self.update_state_info(reset=True)
        
        for btn in [self.step_btn, self.run_btn, self.stop_btn]:
            btn.setEnabled(False)
            
        self.update_display("Машина сброшена")

    def clear_log(self):
        self.log_display.clear()

    # ========================== ОБНОВЛЕНИЕ UI ==============================
    def update_display(self, text):
        self.log_display.append(text)
        self.log_display.ensureCursorVisible()

    def update_state_info(self, reset=False):
        if reset:
            self.result_label.setText("Результат: Введите слово и нажмите 'Загрузить слово'")
            self.result_label.setStyleSheet("background:#f8f9fa; border:1px solid #e9ecef;")
            return

        if self.machine.is_halted():
            if self.machine.state == self.machine.accept_state:
                self.result_label.setText("Результат: Слово — палиндром")
                self.result_label.setStyleSheet("background:#d4edda; border:1px solid #c3e6cb;")
            elif self.machine.state == self.machine.reject_state:
                self.result_label.setText("Результат: Слово не палиндром")
                self.result_label.setStyleSheet("background:#f8d7da; border:1px solid #f5c6cb;")
        else:
            self.result_label.setText("Результат: Выполняется проверка...")

    def update_steps_counter(self):
        self.steps_label.setText(f"Шагов выполнено: {self.steps_count}")

    # ========================== ЗАВЕРШЕНИЕ ==============================
    def show_completion_message(self):
        # Защита от повторного вызова
        if self.completion_shown:
            return
            
        self.completion_shown = True
        
        word = self.input_field.text().strip()
        result = ""
        is_palindrome = 0

        if self.machine.state == self.machine.accept_state:
            result = "Палиндром"
            is_palindrome = 1
        elif self.machine.state == self.machine.reject_state:
            result = "Не палиндром"
        else:
            result = f"Завершено ({self.machine.state})"

        self.save_to_db(word, result, is_palindrome, self.steps_count)
        self.update_state_info()
        self.show_message("Результат", f"Слово '{word}': {result}", QMessageBox.Information)

    # ========================== SQLITE ==============================
    def save_to_db(self, word, result, is_palindrome, steps):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (word, result, is_palindrome, steps)
                VALUES (?, ?, ?, ?)
            """, (word, result, is_palindrome, steps))
            conn.commit()
            conn.close()
            self.update_display(f" Результат сохранён: {word} — {result}")
        except Exception as e:
            self.update_display(f"Ошибка при сохранении в базу: {e}")

    def show_database(self):
        """Показать окно с базой данных"""
        self.db_viewer = DatabaseViewer(self)
        self.db_viewer.exec()

    # ========================== УТИЛИТЫ ==============================
    def show_message(self, title, message, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.exec()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()


# Совместимость
TuringAppGUI = CompactTuringAppGUI
init_db()
