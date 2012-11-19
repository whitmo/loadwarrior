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
