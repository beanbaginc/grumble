import fcntl
import hashlib
import os
import random
import shutil
import sys
import threading
import time
import traceback
from datetime import datetime
from pprint import pformat
from typing import List, Optional, Union


_GRUMBLE_EMOJIS: List[str] = [
    '😶',
    '🧐',
    '🤨',
    '😬',
    '🙄',
    '😑',
    '😕',
    '☹️',
    '😯',
    '😧',
    '😵',
    '😠',
    '😣',
    '😖',
    '😫',
    '😤',
    '😡',
    '🤬',
    '😒',
    '😪',
]

_NUM_GRUMBLE_EMOJIS = len(_GRUMBLE_EMOJIS)

_CLOCK_EMOJIS: List[str] = [
    '🕛',  #  0:00 / 12:00
    '🕧',  #  0:30 / 12:30
    '🕐',  #  1:00 / 13:00
    '🕜',  #  1:30 / 13:30
    '🕑',  #  2:00 / 14:00
    '🕝',  #  2:30 / 14:30
    '🕒',  #  3:00 / 15:00
    '🕞',  #  3:30 / 15:30
    '🕓',  #  4:00 / 16:00
    '🕟',  #  4:30 / 16:30
    '🕔',  #  5:00 / 17:00
    '🕠',  #  5:30 / 17:30
    '🕕',  #  6:00 / 18:00
    '🕡',  #  6:30 / 18:30
    '🕖',  #  7:00 / 19:00
    '🕢',  #  7:30 / 19:30
    '🕗',  #  8:00 / 20:00
    '🕣',  #  8:30 / 20:30
    '🕘',  #  9:00 / 21:00
    '🕤',  #  9:30 / 21:30
    '🕙',  # 10:00 / 22:00
    '🕥',  # 10:30 / 22:30
    '🕚',  # 11:00 / 23:00
    '🕦',  # 11:30 / 23:30
]

_thread_state = threading.local()
_thread_state.grumble_emoji_i = 0
_thread_state.log_i = 0

_cur_dir = os.getcwd()


def _get_log_dir() -> str:
    """Return the directory where logs will be stored.

    By default, this will be the current directory stored when the module
    was loaded.

    This can be overridden by setting the :envvar:`GRUMBLE_LOG_DIR` variable.

    Returns:
        str:
        The log directory.
    """
    return os.environ.get('GRUMBLE_LOG_DIR') or _cur_dir


def _get_log_file_path(
    log_tag: Optional[str] = None,
) -> str:
    """Return the log file path used to log new content.

    This will build a filename consisting of the process name, PID, thread
    information (if in a thread), and an optional log tag.

    Args:
        log_tag (str, optional):
            The log tag to include in the filename.

    Returns:
        str:
        The full file path to the log file.
    """
    proc_name = sys.argv[0]
    pid = os.getpid()
    thread = threading.current_thread()
    thread_name = thread.name

    filename_parts = [
        'grumble',
        proc_name or os.path.basename(sys.executable),
        str(pid),
    ]

    if thread_name != 'MainThread':
        filename_parts += [thread_name, str(thread.ident)]

    if log_tag:
        filename_parts.append(log_tag)

    filename = '%s.log' % '-'.join(filename_parts)

    return os.path.join(_get_log_dir(), filename)


def _write_log(
    *,
    log_path: str,
    header: str,
    details: str,
) -> None:
    """Write to a log file.

    This will use a lock file to ensure that log files don't get jumbled if
    more than one thing is trying to write to the same log at the same time.

    Args:
        log_path (str):
            The full path to the log file.

        header (str):
            The header to write before any details.

        details (str):
            The details to write.
    """
    lock_file = '%s.lock' % log_path

    while True:
        with open(lock_file, 'w') as lock_fp:
            lock_fd = lock_fp.fileno()

            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

                with open(log_path, 'a') as fp:
                    fp.write('%s\n' % header)
                    fp.write(details)

                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                os.remove(lock_file)
                break
            except Exception:
                time.sleep(0.1)


def _format_object(
    obj: object,
    leader: str = '',
) -> str:
    """Return a formatted representation of an object.

    Each line will be prefixed with a leader string, helping to identify the
    section in the log file.

    Args:
        obj (object):
            The object to format.

        leader (str):
            The prefix to include before each line.

    Returns:
        str:
        The formatted representation as a multi-line string.
    """
    return _prefix_lines(pformat(obj),
                         leader=leader)


def _prefix_lines(
    lines: Union[str, List[str]],
    leader: str = '',
) -> str:
    """Return a multi-line string with each line prefixed by a leader.

    Args:
        lines (str or list of str):
            The lines to prefix.

        leader (str):
            The prefix to include before each line.

    Returns:
        str:
        The new multi-line string.
    """
    if isinstance(lines, str):
        lines = lines.splitlines()

    return '\n'.join(
        '%s%s' % (leader, line)
        for line in lines
    )


def bounce(
    num: int = 10,
) -> None:
    """Bounce."""
    width, height = shutil.get_terminal_size()

    grumbles = [
        {
            'c': c,
            'x': random.randint(1, width),
            'y': random.randint(1, height),
            'v': [random.choice([-1, 1]), random.choice([-1, 1])],
        }
        for c in random.choices(_GRUMBLE_EMOJIS, k=num)
    ]

    sys.stdout.write('\u001b[?47h\u001b[2J\u001b[?25l')

    try:
        while True:
            sys.stdout.write('\u001b[2J')

            for g in grumbles:
                c = g['c']
                x = g['x']
                y = g['y']
                v = g['v']

                assert v[0] in (-1, 1)
                assert v[1] in (-1, 1)

                sys.stdout.write('\u001b[%s;%sH%s' % (y, x, c))

                new_x = x + v[0]
                new_y = y + v[1]

                if new_x <= 0 or new_x >= width:
                    new_x = x
                    v[0] *= -1

                if new_y <= 0 or new_y >= height:
                    new_y = y
                    v[1] *= -1

                g['x'] = new_x
                g['y'] = new_y

            sys.stdout.flush()
            time.sleep(0.05)
    except (KeyboardInterrupt, Exception):
        sys.stdout.write('\u001b[?47l')
        sys.stdout.write('\u001b[?25h')
        print('The bouncing has ceased 😞')
        sys.stdout.flush()


def grumble(
    msg: str = '',
    *,
    state: Optional[object] = None,
    category: Optional[str] = None,
    log_tag: Optional[str] = None,
) -> None:
    """Log useful output to standard out and to a log file.

    Grumble is a replacement for :py:func:`print` that outputs information
    to standard out in a visually-identifable way (using emojis), and includes
    a reference to a log file.

    The companion log file contains more information on the context around
    that log statement, including:

    * A unique ID matching the log output
    * The timestamp of the log
    * A category for that log entry
    * Any explicitly-provided state (any Python object)
    * Exception information (if running in an exception handler)
    * A full traceback
    * Local variables

    Log filenames incorporate the process name and ID, any thread information,
    and the optional ``log_tag``, helping to keep log details organized, and
    to capture details that can later be compared or diffed.

    Args:
        msg (str, optional):
            A log message to display.

            This is not required. Contextual details will still be generated
            for the log.

        state (object, optional):
            Any specific Python object state to log with that message.

        category (str, optional):
            A category for the log output, to help identify what the output
            pertains to.

        log_tag (str, optional):
            A custom tag to include in the generated log filename.
    """
    # Set up some identifying information.
    log_path = _get_log_file_path(log_tag=log_tag)
    sha = hashlib.sha1(b'%d' % _thread_state.log_i).hexdigest()
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    _thread_state.log_i += 1

    # Select an emoji.
    #
    # We'll cycle through the list, wrapping around when we hit the last
    # one.
    emoji_i = _thread_state.grumble_emoji_i
    emoji = _GRUMBLE_EMOJIS[emoji_i]

    if emoji_i < _NUM_GRUMBLE_EMOJIS:
        emoji_i += 1
    else:
        emoji_i = 0

    _thread_state.grumble_emoji_i = emoji_i

    # Select a clock emoji.
    #
    # We'll convert to a 0:00-11:30 range, and then convert to an index out
    # of the 12 clock emojis based on whether we're past half the hour.
    norm_hour = now.hour

    if norm_hour >= 12:
        norm_hour = norm_hour - 12

    clock_i = norm_hour * 2

    if now.minute >= 30:
        clock_i += 1

    clock_emoji = _CLOCK_EMOJIS[clock_i]

    # Build the message for the log.
    log_header_lines = [
        emoji,
        '%s  Grumble ID:  %s' % (emoji, sha),
        '%s   Timestamp:  %s %s' % (emoji, clock_emoji, now_str),
    ]

    if category:
        log_header_lines.append('%s    Category:  %s' % (emoji, category))

    if msg:
        log_header_lines.append('%s     Message:  %s' % (emoji, msg))

    log_header_lines += [
        emoji,
    ]

    log_header = '\n'.join(log_header_lines)

    # Build the details of the log message.
    details_lines = ['']
    exc_info = sys.exc_info()
    frame = sys._getframe().f_back

    if state:
        details_lines += [
            '## State:',
            _format_object(state,
                           leader='##   '),
            '##',
            '',
        ]

    if exc_info[0] is not None:
        details_lines += [
            '!! Exception:',
            '!!   Type: %s' % type(exc_info[0]),
            '!!   Value: %r' % exc_info[1],
            '!!   String: %s' % exc_info[1],
            '!!   __dict__:',
            _format_object(exc_info[1].__dict__,
                           leader='!!     '),
            '!!',
            '',
        ]

    if frame is not None:
        details_lines += [
            '>> Traceback:',
            _prefix_lines(
                ''.join(traceback.format_stack(frame)),
                leader='>> '),
            '>>',
            '',
        ]

        details_lines += [
            '$$ Locals:',
            _prefix_lines(
                pformat({
                    key: value
                    for key, value in frame.f_locals.items()
                    if not key.startswith('__')
                }),
                leader='$$  '),
            '$$',
            '',
        ]

    details_lines += ['', '']
    details = '\n'.join(details_lines)

    if os.environ.get('GRUMBLE_OUT') == '1':
        # Write to stdout.
        print(log_header)
        print(details)
    else:
        # Write to the log file.
        _write_log(log_path=log_path,
                   header=log_header,
                   details=details)

        # Build the message for the console.
        output_parts = [emoji]

        if category:
            output_parts.append('[%s]' % category)

        if msg:
            output_parts.append(msg)

        log_dir = _get_log_dir()

        if log_dir.startswith(_cur_dir):
            norm_log_path = os.path.relpath(log_path, _cur_dir)
        else:
            norm_log_path = log_path

        output_parts.append('  %s %s  💾 %s [%s]'
                            % (clock_emoji, now_str, norm_log_path, sha))

        print(' '.join(output_parts))
