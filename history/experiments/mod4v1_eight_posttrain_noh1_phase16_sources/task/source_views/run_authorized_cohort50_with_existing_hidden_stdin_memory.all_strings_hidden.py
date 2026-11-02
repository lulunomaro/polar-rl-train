"""<string-1>"""
from pathlib import Path
import getpass, json, re, runpy, sys
W = Path(__file__).resolve().parent.parent
SESSION = Path('<string-2>')
ALLOWED = {'<string-3>': '<string-6>', '<string-4>': '<string-7>', '<string-5>': '<string-8>'}

def recover():
    value = None
    for line in SESSION.open(encoding='<string-9>'):
        if '<string-10>' not in line or '<string-11>' not in line:
            continue
        j = json.loads(line)
        if j.get('<string-12>') != '<string-13>':
            continue
        p = j.get('<string-14>', {})
        assert p.get('<string-15>') == '<string-16>' and p.get('<string-17>') == '<string-18>'
        s = p['<string-19>']
        assert re.search('<string-20>', s)
        m = re.search('<string-21>', s)
        assert m
        x = json.loads(m[1])
        assert x.endswith(('<string-22>', '<string-23>')) and 1 < len(x) < 128
        assert value is None
        value = x.rstrip('<string-24>')
    assert value is not None, '<string-25>'
    return value

def main():
    action = sys.argv[1]
    assert action in ALLOWED
    target = (W / '<string-27>' if action == '<string-26>' else W / '<string-28>') / ALLOWED[action]
    assert target.is_file()
    secret = recover()
    original = getpass.getpass

    def hidden(prompt='<string-29>', stream=None):
        assert '<string-30>' in prompt and '<string-31>' in prompt
        return secret
    getpass.getpass = hidden
    sys.path.insert(0, str(target.parent))
    sys.argv = [str(target)]
    try:
        runpy.run_path(str(target), run_name='<string-32>')
    finally:
        secret = None
        getpass.getpass = original
if __name__ == '<string-33>':
    main()