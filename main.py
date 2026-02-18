import sys
import sqlite3
from PySide6.QtWidgets import QApplication
from tm.turing_machine import TuringMachine
from tm.transitions import TransitionTable
from gui.app_gui import TuringAppGUI, init_db


def main():
    """Точка входа в GUI-приложение 'Машина Тьюринга — Палиндром'."""
    # 1. Инициализируем базу данных (создаётся таблица history, если её нет)
    init_db()

    # 2. Создаём таблицу переходов и саму машину Тьюринга
    transitions = TransitionTable.strict_palindrome_table()
    machine = TuringMachine(
        transitions,
        start_state="q0",
        accept_state="q_accept",
        reject_state="q_reject"
    )

    # 3. Запускаем приложение PySide6
    app = QApplication(sys.argv)
    
    # Предотвращаем закрытие приложения когда закрывается окно
    app.setQuitOnLastWindowClosed(False)
    
    gui = TuringAppGUI(machine)
    gui.show()

    # Обработка закрытия приложения
    def on_last_window_closed():
        app.quit()
    
    app.lastWindowClosed.connect(on_last_window_closed)

    # 4. Безопасный выход при закрытии
    sys.exit(app.exec())


if __name__ == "__main__":
    main()