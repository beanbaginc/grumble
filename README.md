Grumble...
==========

Grumble is a Python library for print debuggers who are drowning in `print()`
statements..

It's for developers who need to capture lots of data between runs.

It's for developers banging their head against the wall trying to dive deep
into code that's not quite working right, or not working consistently.


Installation is easy
--------------------

```
$ pip3 install grumble
```

Why would you want to install Grumble? Well...


It's a Friday evening, and everything you wrote is busted
---------------------------------------------------------

You spent all week trying to get your code work. And it should work, but it's
not. You're furiously trying to debug it as you get increasingly exhausted,
your brain begining to melt into a pile of goo.

The hours are ticking away with nothing to show for it. Your console is full
of print output, and it's beginning to blur together into some kind of blended
soup of green Matrix code nonsense.

Log messages mixed with tracebacks, mixed with variable dumps, all coming from
different classes, threads, processes. Screens full of it.

The details change between runs. You're writing it all down, trying to keep it
straight in your head. But it's begun to fall apart. And you're wondering
why you turned to a life of coding instead of a life of farming.

True story.


This is where Grumble comes in
------------------------------

Grumble gives one simple command to log debug output:

```python
def grumble(msg='', state=None, category=None, log_tag=None):
    ...
```

When you `grumble(...)`, it'll print a simple log message to standard output,
and log details to a log file.

By default, the log message will show:

1. An emoji (to help you visually separate that log statement from other noise).

2. A timestamp of the log message.

3. A log file with more details.

   This identifies "grumble", the process name, the PID, a thread name (if using
   threads), and an extra log tag name (if setting `log_tag`).

4. A searchable hash within that log file.

For example:

```python
>>> from grumble import grumble
>>> grumble()
😶  🕧 2022-10-16 12:46:36  💾 grumble-python3-86256.log [b6589fc6ab0dc82cf12099d1c2d40ab994e8410c]
```

Good at a glance, and you can customize that with a log message or category:

```python
>>> grumble('Look, a log message!', category='ui', log_tag='uilogs')
🧐 [ui] Look, a log message!  🕧 2022-10-16 12:47:10  💾 grumble-python3-86256-uilogs.log [356a192b7913b04c54574d18c28d46e6395428ab]
```

And we can add some state. Anything at all.

```python
>>> grumble('Logging the generated object', state=some_object)
🤨 [ui] Look, a log message!  🕧2022-10-16 12:48:43  💾 grumble-python3-86256.log [da4b9237bacccdf19c0760cab7aec4a8359010b0]
```

State will show up, nicely formatted, in the log file. Which we'll cover right
about... now.


Going deeper with logs
----------------------

That log message is handy, but it doesn't tell us much more than a normal
`print()` statement.

It does point to a log file, though. Let's look into that.

Let's write a little program to print the output of a directory, filtered by
a file pattern:


```python
import os
from fnmatch import fnmatch

from grumble import grumble


def filter_filenames(filenames, file_pattern):
    return [
        filename
        for filename in filenames
        if fnmatch(filename, file_pattern)
    ]


def list_directory(path, file_pattern):
    path = os.path.abspath(path)
    results = filter_filenames(os.listdir(path),
                               file_pattern)

    grumble("Let's look at a directory",
            state={
                'raw os.listdir output': os.listdir(path),
            })

    return results

filenames = list_directory('.', file_pattern='*.txt')

print('Files:')
print('\n'.join(filenames))
```

And let's run it!

```
$ python3 dirtest.py
😶 Let's look at a directory  🕒 2022-10-16 13:01:21  💾 grumble-dirtest.py-7154.log [b6589fc6ab0dc82cf12099d1c2d40ab994e8410c]
Files:
world.txt
hello.txt
```

We have our Grumble log statement, and our resulting directory listing. Time to
look at what's in the log:

```
😶
😶  Grumble ID:  b6589fc6ab0dc82cf12099d1c2d40ab994e8410c
😶   Timestamp:  🕒 2022-10-16 13:01:21
😶     Message:  Let's look at a directory
😶

## State:
##   {'raw os.listdir output': ['world.txt',
##                              'hello.txt',
##                              'dirtest.py']}
##

>> Traceback:
>>   File "/tmp/grumble/dirtest.py", line 28, in <module>
>>     filenames = list_directory('.', file_pattern='*.txt')
>>   File "/tmp/grumble/dirtest.py", line 20, in list_directory
>>     grumble("Let's look at a directory",
>>

$$ Locals:
$$  {'file_pattern': '*.txt',
$$   'path': '/tmp/grumble',
$$   'results': ['world.txt', 'hello.txt']}
$$
```

Look at all that debugging information! We have:

1. An easy visual and searchable reference from the log output.
2. Any and all state we passed to that call to `grumble()`.
3. A traceback of where we are.
4. All local variables.

As you `grumble()` your way through your debugging session, your log file
(or files, if using threads or different logging tag names) will grow with
helpful information that you can read through or even diff.

Logs are outputted in the current directory by default. You can specify a
different directory by setting the `GRUMBLE_LOG_DIR=...` environment variable,

You can also output full logs to the console by setting `GRUMBLE_OUT=1`.


Works great as an exception handler
-----------------------------------

This log file can also help with exceptions. Say we had:

```python
try:
    raise Exception('bad things happened')
except Exception as e:
    grumble('Uh oh, we hit an exception: %s' % e)

return results
```

Our log file would also contain:

```
!! Exception:
!!   Type: <class 'type'>
!!   Value: Exception('bad things happened')
!!   String: bad things happened
!!   __dict__:
!!     {}
!!
```

Pretty handy. Especially for exceptions that contain additional state.


Works with threads and multiple processes!
------------------------------------------

Logs are differentiated by thread and process IDs. Lock files ensure that
logs don't get jumbled together. Because that would be annoying to deal with.


Emojis and hashes are deterministic
-----------------------------------

Grumble will cycle through emojis in the following order, every time:

😶 🧐 🤨 😬 🙄 😑 😕 ☹️ 😯 😧 😵 😠 😣 😖 😫 😤 😡 🤬 😒 😪

Hashes used to identify the matching part in a log file are also consistent
between runs. They're a SHA1 of a 0-based index into the log.

This makes the log output more consistent between runs.

If you run the same process multiple times with different results or behavior,
you'll want to narrow down what's going on. By keeping the order of emojis and
hashes the same, and tagging each log file with process/thread IDs, you'll be
able to more easily diff two runs and see if anything has changed.


What else can it do?
--------------------

No, that's about it. Nothing hidden in the module. Nothing at all. Nope.

Install Grumble today!
