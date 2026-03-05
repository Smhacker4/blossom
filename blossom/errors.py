class BlossomError(Exception):
    def __init__(self, message, line=None):
        self.blossom_message = message
        self.line = line
        super().__init__(self._format())

    def _format(self):
        if self.line:
            return f"\n  Blossom Error on line {self.line}:\n  {self.blossom_message}\n"
        return f"\n  Blossom Error:\n  {self.blossom_message}\n"


class BlossomLexError(BlossomError):
    pass


class BlossomParseError(BlossomError):
    pass


class BlossomRuntimeError(BlossomError):
    pass
