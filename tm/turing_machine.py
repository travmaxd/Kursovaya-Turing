# tm/turing_machine.py
from .tape import Tape
from .transitions import TransitionTable

class TuringMachine:
    """
    Универсальная Turing Machine на основе таблицы переходов TransitionTable.
    Конструктор гибкий:
      - если first_arg — TransitionTable, то используется он и состояния берутся из аргументов start_state/accept_state/reject_state
      - если first_arg — строка, то считается входной словом и используется default_palindrome_table()
    """
    def __init__(self, first_arg=None, start_state: str = "q0",
                 accept_state: str = "q_accept", reject_state: str = "q_reject",
                 blank: str = "⊔"):
        # если передали таблицу переходов
        if isinstance(first_arg, TransitionTable):
            self.transitions = first_arg
            self.tape = Tape("", blank=blank)
        else:
            # иначе — первый аргумент может быть входной строкой
            self.transitions = TransitionTable.strict_palindrome_table()
            self.tape = Tape(first_arg if isinstance(first_arg, str) else "", blank=blank)

        self.head = 0
        self.state = start_state
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.blank = blank
        self.step_count = 0
        self.max_steps = 100_000  # защита от бесконечных циклов

    def load_tape(self, input_str: str):
        self.tape = Tape(input_str, blank=self.blank)
        self.head = 0
        self.state = self.start_state
        self.step_count = 0

    def read_symbol(self):
        return self.tape.read(self.head)

    def write_symbol(self, symbol: str):
        # если символ обозначен как '_any_' — записываем текущий символ (логика таблицы)
        if symbol == "_any_":
            # ничего не меняем (символ остаётся тем же)
            return
        self.tape.ensure_index(self.head)
        self.tape.write(self.head, symbol)

    def move_head(self, direction: str):
        if direction == "L":
            if self.head == 0:
                # если идём за левую границу — вставим blank в начало и оставим голову на 0
                self.tape.cells.insert(0, self.blank)
                # head остаётся 0 (мы как бы добавили ячейку слева)
            else:
                self.head -= 1
        elif direction == "R":
            self.head += 1
            # расширим ленту, если нужно
            self.tape.ensure_index(self.head)
        elif direction == "S":
            pass
        else:
            raise ValueError(f"Неизвестное направление движения: {direction}")

    def step(self) -> str:
        """
        Выполнить один шаг. Возвращает человеко-читаемую строку с действием.
        Если перехода нет — переводит машину в reject_state.
        """
        if self.is_halted():
            return f"Машина остановлена в состоянии {self.state}"

        if self.step_count >= self.max_steps:
            self.state = self.reject_state
            return "Превышен лимит шагов — остановлено."

        cur_symbol = self.read_symbol()
        trans = self.transitions.get(self.state, cur_symbol)

        # Поддержка wildcard: если у таблицы есть '_any_' — transitions.get уже вернёт его.
        if trans is None:
            # Нет перехода — считаем, что машина останавливается и отвергает
            self.state = self.reject_state
            return f"Нет перехода для ({self.state}, {cur_symbol}) — отклонено."

        write_sym, direction, new_state = trans

        # если write_sym == "_any_" — записываем текущий символ (ничего не меняем)
        if write_sym != "_any_":
            self.write_symbol(write_sym)

        # сдвиг головки
        self.move_head(direction)

        prev_state = self.state
        self.state = new_state
        self.step_count += 1

        direction_text = {"L": "влево", "R": "вправо", "S": "остались"}
        action = (
            f"[{self.step_count}] "
            f"Символ: '{cur_symbol}' → Записали: '{write_sym if write_sym != '_any_' else cur_symbol}', "
            f"движение: {direction_text.get(direction, direction)}, "
            f"состояние: {prev_state} → {new_state}"
        )

        return action

    def run(self):
        """
        Запустить до остановки (accept/reject) или до max_steps.
        Возвращает итоговый результат (True — accept, False — reject).
        """
    
        for _ in range(self.max_steps):
            if self.is_halted():
                return self.state == self.accept_state
            self.step()
        # Превышен лимит
        self.state = self.reject_state  
        return False

    def is_halted(self) -> bool:
        return self.state in (self.accept_state, self.reject_state)

    def get_result(self) -> str:
        if self.state == self.accept_state:
            return "Слово является палиндромом!"
        elif self.state == self.reject_state:
            return "Слово не является палиндромом"
        else:
            return f"Машина в состоянии {self.state} (неостанавливается)"
