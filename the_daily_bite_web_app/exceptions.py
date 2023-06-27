class InvokeFunctionException(Exception):
    def __init__(self, function_name: str, message: str = ""):
        if not message:
            self.message = f"Function {function_name} invocation failed."
        else:
            self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
