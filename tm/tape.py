# tm/tape.py
class Tape:
    """
    Простая лента Тьюринга с символом пустоты по умолчанию '⊔'.
    Хранит символы в списке self.cells, автоматически расширяется вправо при записи.
    """
    def __init__(self, input_str: str = "", blank: str = "⊔"):
        self.blank = blank
        # Если пустая входная строка — создаём одну ячейку с blank,
        # чтобы чтение/запись работали корректно.
        self.cells = list(input_str) if input_str else [self.blank]

    def read(self, pos: int) -> str:
        if pos < 0:
            return self.blank
        if pos >= len(self.cells):
            return self.blank
        return self.cells[pos]

    def write(self, pos: int, symbol: str):
        if pos < 0:
            # Для простоты: если пишут в отрицательный индекс, вставляем в начало
            # и сдвигаем ленту вправо, сохраняя головку у 0 (внешняя логика должна учесть сдвиг)
            raise IndexError("Запись в отрицательный индекс не поддерживается напрямую.")
        # расширяем ленту вправо при необходимости
        while pos >= len(self.cells):
            self.cells.append(self.blank)
        self.cells[pos] = symbol

    def ensure_index(self, pos: int):
        """Гарантирует, что индекс pos доступен (расширяет ленту вправо)."""
        while pos >= len(self.cells):
            self.cells.append(self.blank)

    def __len__(self):
        return len(self.cells)

    def __bool__(self):
        return len(self.cells) > 0

    def __str__(self):
        return ''.join(self.cells)

    def __repr__(self):
        return f"<Tape {''.join(self.cells)}>"
