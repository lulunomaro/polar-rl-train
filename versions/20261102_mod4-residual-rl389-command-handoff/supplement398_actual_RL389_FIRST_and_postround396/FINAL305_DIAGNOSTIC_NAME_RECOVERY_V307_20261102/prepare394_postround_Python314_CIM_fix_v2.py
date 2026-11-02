"""Preserve the unexecuted generator failure and prepare independent postround394."""
from pathlib import Path
import ast
import json
import time

source = Path(__file__).with_name('prepare394_postround_Python314_CIM_fix.py')
report = source.parent / 'reports/LOCAL394_GENERATOR_SYNTAX_AND_MISSING_BIND_FAILURE_PRESERVED.json'
with report.open('x', encoding='utf8') as stream:
    json.dump(dict(
        epoch=time.time(), passed=False,
        source=str(source),
        generator_error='SyntaxError: invalid decimal literal at keyword 390unusedpreserved=True',
        followup_error='bind388_after389FIRST_and_launch_once.py missing because generator did not execute',
        evidence='Actual tool failures retained in this chat; no generator side effects occurred',
        training389_changed=False, network=0, model_reads=0, SDK=0,
        repair='Independent v2 wrapper changes only the invalid keyword before AST compilation; original file preserved'
    ), stream, indent=2)
text = source.read_text(encoding='utf8')
assert text.count('390unusedpreserved=True') == 1
text = text.replace('390unusedpreserved=True', 'unused390preserved=True')
ast.parse(text, filename=str(source))
exec(compile(text, str(source), 'exec'), {'__file__': str(source), '__name__': '__main__'})
