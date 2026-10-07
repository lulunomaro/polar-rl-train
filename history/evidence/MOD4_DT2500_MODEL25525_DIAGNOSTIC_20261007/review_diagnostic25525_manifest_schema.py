"""Explicit schema retry: flat raw omits probeSHA; exact runtime manifest supplies it."""
from pathlib import Path
import json

D = Path(__file__).resolve().parent
original = D / 'review_diagnostic25525_completed_once.py'
(D / 'reports/DIAGNOSTIC25525_FIRST_READER_ERROR.json').write_text(json.dumps({
    'error': 'KeyError probe_sha256 for flat raw',
    'scope': 'offline reader before any output report/Git/remote write',
    'actual_schema': 'flat probe.json has no probe_sha256; manifest.artifacts.runtime pins the entire probe runtime',
    'runtime_training_or_evaluation_changed': False,
}, indent=2), encoding='utf8')
code = original.read_text(encoding='utf8')
code = code.replace("probe_exact=base['probe_sha256'] == new['probe_sha256'],",
                    "probe_exact=(read(bdir / 'manifest.json')['artifacts']['runtime'] == manifest['artifacts']['runtime'] "
                    "and (kind == 'flat' or base['probe_sha256'] == new['probe_sha256'])),")
exec(compile(code, str(original), 'exec'), {'__file__': str(original), '__name__': '__main__'})
folder = D.parent / 'polar-rl-train/history/evidence/MOD4_DT2500_MODEL25525_DIAGNOSTIC_20261007'
(folder / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
(folder / 'FIRST_READER_ERROR.json').write_bytes((D / 'reports/DIAGNOSTIC25525_FIRST_READER_ERROR.json').read_bytes())
