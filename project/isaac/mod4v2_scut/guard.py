"""Same constructor nominal/DR guard, explicitly rebound to the released v2 asset."""
import hashlib
import json
from pathlib import Path

_binding = json.loads(Path(__file__).with_name('BINDINGS.json').read_bytes())
_path = Path(_binding['shared_guard'])
_raw = _path.read_bytes()
if hashlib.sha256(_raw).hexdigest() != _binding['shared_guard_SHA']:
    raise ValueError('Shared nominal guard changed')
exec(compile(_raw, str(_path), 'exec'), globals())
USD_SHA256 = '97e845c8dcc2485d91081949a8531d67771893731e31d04316b4e67d7ec9dbaa'
CONTRACT_SHA256 = '00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e'
_original_read = read_asset_identity


def read_asset_identity(asset_dir):
    identity = _original_read(asset_dir)
    for name, gas in identity.contract['gas_springs'].items():
        require(abs(gas['target_position_m'] - .1706394410901294) < 1e-10,
                'Wrong HW300N60 gas target: ' + name)
        require(identity.contract['joints'][name]['limits_si'] ==
                [-.039360558909870585, .020639441090129412], 'Wrong 60mm gas stroke')
    return identity
