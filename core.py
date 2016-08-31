import shlex
import random

PREDICTION_THRESHOLD = 0.5

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
    query_words, cmd_words = [shlex.split(x) for x in [query_string, command_string]]
    for qw, cw in zip(query_words, cmd_words):
        if is_arg(cw):
            maps[cw[1:-1]] = magic_type_convert(qw)
        else:
            if qw != cw: return False, {}
    return True, maps


# returns the probability that query string matches a command
def cmd_predict(query_string, command_string):
    return random.random()


# handles what commands to display to the user based on our predictions (True means confident in a single cmd)
def cmds_display(prediction_command_map):
    is_confident = False

    # note if confident in *only* 1 prediction
    if sum(1 for p in prediction_command_map.keys() if p > PREDICTION_THRESHOLD) == 1:
        is_confident = True

    # take the top 3 predictions
    cmds = sorted(prediction_command_map.values())[:3]
    return is_confident, cmds


class Assistant:

    def __init__(self):
        self.mappings = {}

    def execute(self, query_string):
        for cmd in self.mappings.keys():
            succ, map = arg_match(query_string, cmd)
            if succ:
                to_execute = self.mappings[cmd]
                args = [map[arg_name] for arg_name in to_execute["args"]]
                return True, to_execute["function"](*args)
        return False, None

    # returns dict of command predictions
    def predict(self, query_string):
        predictions = {}
        for cmd in self.mappings.keys():
            p = cmd_predict(query_string, cmd)
            predictions[p] = cmd
        print('Predictions: {}'.format(predictions))
        results = cmds_display(predictions)
        print('Results: {}'.format(results))
        return results


    def register(self, command_string):
        def inner(func):
            # sketchy hack to get function arg names CPython
            f_args = func.__code__.co_varnames[:func.__code__.co_argcount]
            self.mappings[command_string] = {"function":func, "args":f_args}
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return inner
