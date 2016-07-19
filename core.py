
# placeholder for something that needs to convert string input into a python value
def magic_type_convert(x):
    try:
        return int(x)
    except:
        return x

# is this word an argument?
def is_arg(s):
    if len(s)>2 and s[0] == "{" and s[-1] == "}": return True
    return False

# attempt to match query string to command and return mappings
def arg_match(query_string, command_string):
    maps = {}
    query_words, cmd_words = query_string.split(), command_string.split()
    for qw, cw in zip(query_words, cmd_words):
        if is_arg(cw):
            maps[cw[1:-1]] = magic_type_convert(qw)
        else:
            if qw != cw: return False, {}
    return True, maps

class Assistant:

    def __init__(self):
        self.mappings = {}

    def execute(self, query_string):
        for cmd in self.mappings.keys():
            succ, map = arg_match(query_string, cmd)
            if succ:
                to_execute = self.mappings[cmd]
                args = [map[arg_name] for arg_name in to_execute["args"]]
                return to_execute["function"](*args)

    def register(self, command_string):
        def inner(func):
            # sketchy hack to get function arg names CPython
            f_args = func.__code__.co_varnames[:func.__code__.co_argcount]
            self.mappings[command_string] = {"function":func, "args":f_args}
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return inner
