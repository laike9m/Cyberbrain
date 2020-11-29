# Cyberbrain Features

## Dataflow Analysis and Variable Tracing
 
Say you find a bug, where `foo` at line 10 should be 1 but instead is 2. What's causing the problem, you might wonder, and you may end up stepping through the program with a debugger. This is not too bad, but there's a bigger problem: **do you really remember what happened in every step?** Probably not. And that's a pain point of traditional debuggers: **debugging information is not persisted, and relies on programmers to remember them**.

Unlike other debuggers, Cyberbrain shows an accurate data flow, and persists every state of the program. Not only do you not need to remember anything, you don't even need to step through the program, and that can save tons of time when debugging.

So, here's how you debug with Cyberbrain.

![image](https://user-images.githubusercontent.com/2592205/95420137-d6ddd400-08ef-11eb-9464-aa10cfbc75ed.png)

Let's say you want to find out why the return value is wrong. By looking at the graph, you already have a rough idea on what lead to the return value.

Next, **hover on the "return" node**, and boom, all relevant values show up, forming a trace path from function start to the end:

![image](https://user-images.githubusercontent.com/2592205/95420475-59ff2a00-08f0-11eb-9340-0c77ea569b92.png)

See, why stepping through a program when all the information are available? All you need is a mouse move.

## Object Inspection

Now you might think, what if I have a big list that does not fit into the graph, can I inspect its value?

Of course! Don't underestimate the devtools.

![image](https://user-images.githubusercontent.com/2592205/95421146-ac8d1600-08f1-11eb-9807-6983da7b108e.png)

Upon launching, **Cyberbrain automatically opens a devtools window. When you hover on a variable, its value is logged in the devtools console**. So in this case, though there isn't enough space to show the entire list in the trace graph, you can still inspect its value from the devtools.

Almost all Python debuggers (PyCharm, VS Code, etc) truncate values, and is not able to show every element of a large list. But we believe "*the devil is in the detail*", every piece of information might be useful and should not be ignored. Thus, **Cyberbrain will not truncate values, unless you explicitly tell it to do so.**

## Loops

Cyberbrain has another unique feature: You can set loop counters while debugging.

![set_loop_counter](https://user-images.githubusercontent.com/2592205/95424989-6edfbb80-08f8-11eb-94bd-208f8798c555.gif)

This feature has some [known bugs](https://github.com/laike9m/Cyberbrain/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc+label%3Aloop) as the implementation is very complex. You can expect it to get better over time.

The UI is inspired by [birdseye](https://github.com/alexmojaki/birdseye), thanks Alex for making such a innovative tool.

## Known limitations

- Overhead. See [Lowering the overhead brought by Cyberbrain](https://github.com/laike9m/Cyberbrain/issues/58).

- Cyberbrain only traces the first call, no matter how many times the decorated function is called.

- You can only have one `@trace` decorator.

- No effort has been put on supporting threaded code (e.g. a multi-threaded web server), it may or may not work.

- Cyberbrain is not guaranteed to work if the program raises unhandled exceptions. You should first resolve or properly catch them.

- Cyberbrain can't display the content of certain objects, because they cannot be converted to JSON. In this case, Cyberbrain will show the repr string of that object. This should be rare.

- For generator functions, you need to manually call `trace.stop()`. see [test_generator.py](https://github.com/laike9m/Cyberbrain/blob/master/test/test_generator.py). 

- `async` and multi-threading are not supported.

**We will improve or support these use cases in [future versions](https://github.com/laike9m/Cyberbrain#status-quo-and-milestones).**