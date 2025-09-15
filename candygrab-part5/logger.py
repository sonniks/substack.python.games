# logger.py


from datetime import datetime


_last_message = None
_repeat_count = 0
_enable_logging = True


def conlog(message):
    """
    Log a message to the console with a timestamp.
    :param message:
    :return:
    """
    if _enable_logging:
        global _last_message, _repeat_count
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if message == _last_message:
            _repeat_count += 1
            return
        if _repeat_count > 0:
            print(f"{now} Previous message repeated {_repeat_count} times")
            _repeat_count = 0
        print(f"{now} {message}")
        _last_message = message