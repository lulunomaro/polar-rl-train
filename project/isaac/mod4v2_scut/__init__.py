"""MOD4v2 HW300N60 with the pinned SCUT equations and shared training lifecycle."""
import json
from pathlib import Path

BINDINGS = json.loads((Path(__file__).with_name('BINDINGS.json')).read_bytes())
__path__.append(BINDINGS['shared_package'])
if BINDINGS.get('fallback_package'):
    __path__.append(BINDINGS['fallback_package'])
