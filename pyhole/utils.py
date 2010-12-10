"""Pyhole Utility Library"""


from threading import Thread


def admin(func):
    """Administration Decorator"""

    def f(self, *args, **kwargs):
        if self.irc.source == self.irc.admin:
            func(self, *args, **kwargs)
        else:
            self.irc.say("Sorry, you are not authorized to do that.")
    f.__doc__ = func.__doc__
    return f


def spawn(func):
    """Thread Spawning Decorator"""

    def f(self, *args, **kwargs):
        if args and args[0]:
            params = " ".join(args)
            t = Thread(target=func, args=(self, params), kwargs=kwargs)
        else:
            t = Thread(target=func, args=(self,), kwargs=kwargs)
        self.irc.log.debug("Spawning: %s" % t.name)
        t.start()
    f.__doc__ = func.__doc__
    return f
