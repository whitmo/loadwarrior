from logging import getLogger

logger = getLogger(__name__)


def find_config(filename, candidates=None, raise_error=True, logger=logger):
    """
    Iterate over possible candidate paths for a filename, return the
    first one that exists

    Raise or log error if no path is found

    filename: a string represent the config file
    
    candidates: callable that takes a string returns an iterable of
                possible files
    """
    notfound = []
    for candidate in candidates(filename):
        if candidate.exists():
            return candidate
        notfound.append(candidate)
    nf = ",".join(notfound)
    msg = "%s not found in %s"
    if raise_error:
        raise ValueError("%s not found in %s" %(filename, nf))
    logger.error(msg, filename, nf)
    return None


class reify(object):
    #@@ from pyramid
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  An example:

    .. code-block:: python

       class Foo(object):
           @reify
           def jammy(self):
               print 'jammy called'
               return 1

    And usage of Foo:

    .. code-block:: text

       >>> f = Foo()
       >>> v = f.jammy
       'jammy called'
       >>> print v
       1
       >>> f.jammy
       1
       >>> # jammy func not called the second time; it replaced itself with 1
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val

