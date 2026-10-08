"""Match the restricted bridge's existing identifier contract without changing it."""
import re
PATTERN=r'[a-z0-9][a-z0-9-]{5,95}'

def accepted(value):
    return isinstance(value,str) and re.fullmatch(PATTERN,value) is not None

def partition(values):
    valid=[];invalid=[]
    for value in values:
        (valid if accepted(value) else invalid).append(value)
    return valid,invalid
