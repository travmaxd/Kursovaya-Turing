class TransitionTable:
    def __init__(self, transitions: dict):
        self.transitions = transitions or {}

    def get(self, state: str, symbol: str):
        if state in self.transitions:
            state_transitions = self.transitions[state]
            if symbol in state_transitions:
                return state_transitions[symbol]
            if "_any_" in state_transitions:
                return state_transitions["_any_"]
        return None

    def __contains__(self, state: str):
        return state in self.transitions

    def __repr__(self):
        return f"<TransitionTable states={len(self.transitions)}>"

    @staticmethod
    def strict_palindrome_table():
        """
        Машина Тьюринга для строгой проверки палиндрома.
        Различает символы, помечает их и сверяет зеркальные пары.
        """
        symbols = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz")
        t = {}

        # --- Начало ---
        t["q0"] = {
            "X": ("X", "R", "q0"),
            "⊔": ("⊔", "S", "q_accept"),
        }
        for s in symbols:
            t["q0"][s] = ("X", "R", f"q_mark_{s}")

        # --- Поиск конца для данного символа ---
        for s in symbols:
            t[f"q_mark_{s}"] = {
                "X": ("X", "R", f"q_mark_{s}"),
                "_any_": ("_any_", "R", f"q_mark_{s}"),
                "⊔": ("⊔", "L", f"q_check_{s}")
            }

            # Проверяем справа символ
            t[f"q_check_{s}"] = {
                s: ("X", "L", "q_back"),          # нашли нужный символ справа
                "X": ("X", "L", f"q_check_{s}"),  # пропускаем отмеченные
                "⊔": ("⊔", "S", "q_accept"),      # дошли до конца — центр, палиндром
                "_any_": ("_any_", "S", "q_reject")
            }

        # --- Возврат в начало ---
        t["q_back"] = {
            "X": ("X", "L", "q_back"),
            "_any_": ("_any_", "L", "q_back"),
            "⊔": ("⊔", "R", "q0")
        }

        # --- Конечные ---
        t["q_accept"] = {}
        t["q_reject"] = {}

        return TransitionTable(t)
