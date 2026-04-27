import ast


class Calculator:
    """Safe arithmetic evaluator supporting +, -, *, /, parentheses and numbers.

    Used to demonstrate observable tool-calls by the agent.
    """

    ALLOWED_NODES = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.Mod,
        ast.FloorDiv,
        ast.Tuple,
    }

    def compute(self, expr: str):
        try:
            node = ast.parse(expr, mode='eval')
            for n in ast.walk(node):
                if type(n) not in self.ALLOWED_NODES:
                    raise ValueError(f'Unsupported expression element: {type(n).__name__}')
            return eval(compile(node, filename='<ast>', mode='eval'))
        except Exception as e:
            raise ValueError(f'Invalid expression: {e}')
