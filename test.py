from core import Assistant, arg_match

# simple tests for argument matcher
print("Should be true", arg_match("add 3 and 4", "add {n1} and {n2}"))
print("Should be false", arg_match("add 3 and 4", "add {n1} and 43"))

assistant = Assistant()

# register simple function with assistant
@assistant.register("add {n1} and {n2}")
def add(n1,n2):
    return n1+n2

# attempt to execute on input
print(assistant.execute("add 42 and 54"))
