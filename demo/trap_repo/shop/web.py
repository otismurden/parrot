class _App:
    def route(self, path):
        def wrap(fn):
            return fn
        return wrap


app = _App()
