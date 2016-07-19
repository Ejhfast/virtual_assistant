from core import Assistant
import sys

assistant = Assistant()

# register simple function with assistant
@assistant.register("add {n1} and {n2}")
def add(n1,n2):
    return n1+n2

@assistant.register("say {word} {n} times")
def say(n,word):
    for _ in range(0,n): print(word)

print(assistant.execute(sys.argv[1]))
