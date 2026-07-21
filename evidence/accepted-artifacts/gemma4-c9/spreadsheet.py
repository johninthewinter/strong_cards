from __future__ import annotations
import re

class SpreadsheetError(ValueError):
    pass

def evaluate_workbook(cells: dict[str, int | str]) -> dict[str, int]:
    cell_name_pattern = re.compile(r"^[A-Z]+[1-9][0-9]*$")
    for name in cells:
        if not cell_name_pattern.match(name):
            raise SpreadsheetError(f"Invalid cell name: {name}")

    memo = {}
    visiting = set()

    def parse_cell_coords(name: str) -> tuple[int, int]:
        match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", name)
        if not match:
            raise SpreadsheetError(f"Invalid cell reference: {name}")
        col_str, row_str = match.groups()
        col = 0
        for char in col_str:
            col = col * 26 + (ord(char) - ord('A') + 1)
        return col, int(row_str)

    def col_to_str(c):
        res = []
        while c > 0:
            c -= 1
            res.append(chr(ord('A') + (c % 26)))
            c //= 26
        return "".join(reversed(res))

    def get_range_cells(start_name: str, end_name: str):
        s_col, s_row = parse_cell_coords(start_name)
        e_col, e_row = parse_cell_coords(end_name)
        if s_col > e_col or s_row > e_row:
            raise SpreadsheetError("Invalid range")
        for col in range(s_col, e_col + 1):
            for row in range(s_row, e_row + 1):
                yield f"{col_to_str(col)}{row}"

    def evaluate(name: str) -> int:
        if name in memo: return memo[name]
        if name in visiting: raise SpreadsheetError("Cycle detected")
        if name not in cells: raise SpreadsheetError("Unknown cell")
        visiting.add(name)
        try:
            val = cells[name]
            if isinstance(val, int): res = val
            elif isinstance(val, str) and val.startswith('='):
                res = evaluate_expression(val[1:], name)
            else: raise SpreadsheetError("Invalid cell value")
        finally:
            visiting.remove(name)
        memo[name] = res
        return res

    def evaluate_expression(expr: str, current_cell: str) -> int:
        pos = [0]
        def peek(): return expr[pos[0]] if pos[0] < len(expr) else None
        def consume():
            c = peek()
            pos[0] += 1
            return c
        def skip():
            while peek() and peek().isspace(): pos[0] += 1

        def parse_expr() -> int:
            skip()
            node = parse_term()
            while True:
                skip()
                c = peek()
                if c not in ('+', '-'): break
                op = consume()
                right = parse_term()
                node = node + right if op == '+' else node - right
            return node

        def parse_term() -> int:
            skip()
            node = parse_factor()
            while True:
                skip()
                c = peek()
                if c not in ('*', '/'): break
                op = consume()
                right = parse_factor()
                if op == '*': node *= right
                else:
                    if right == 0: raise SpreadsheetError("Division by zero")
                    node = int(node / right)
            return node

        def parse_factor() -> int:
            skip()
            c = peek()
            if c == '+': consume(); return parse_factor()
            if c == '-': consume(); return -parse_factor()
            return parse_primary()

        def parse_primary() -> int:
            skip()
            c = peek()
            if c == '(':
                consume()
                res = parse_expr()
                skip()
                if consume() != ')': raise SpreadsheetError("Missing )")
                return res
            if c and c.isdigit():
                s = ""
                while peek() and peek().isdigit(): s += consume()
                return int(s)
            if c == 'S' and expr[pos[0]:pos[0]+3] == 'SUM':
                pos[0] += 3
                skip()
                if consume() != '(': raise SpreadsheetError("Missing (")
                start = ""
                while peek() and (peek().isupper() or peek().isdigit()): start += consume()
                if not start: raise SpreadsheetError("No start cell")
                skip()
                if consume() != ':': raise SpreadsheetError("Missing :")
                end = ""
                while peek() and (peek().isupper() or peek().isdigit()): end += consume()
                if not end: raise SpreadsheetError("No end cell")
                skip()
                if consume() != ')': raise SpreadsheetError("Missing )")
                total = 0
                for cell in get_range_cells(start, end): total += evaluate(cell)
                return total
            if c and c.isupper():
                ref = ""
                while peek() and (peek().isupper() or peek().isdigit()): ref += consume()
                return evaluate(ref)
            raise SpreadsheetError(f"Unexpected character: {c}")

        res = parse_expr()
        skip()
        if pos[0] < len(expr): raise SpreadsheetError("Trailing characters")
        return res

    results = {}
    for name in cells: results[name] = evaluate(name)
    return results

