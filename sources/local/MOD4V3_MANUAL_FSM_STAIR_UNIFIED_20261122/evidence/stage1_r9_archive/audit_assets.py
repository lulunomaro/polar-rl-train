"""Hash protected source/weights/contracts without writing into donor directories."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
from fsm_paths import HERE, LOCAL, REPO, E0_PATH, JUMP_PATH
from fsm_io import put, sha256

def paths():
    folders = [LOCAL/n for n in (
        'MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120', 'MOD4V3_AUTONOMOUS_MOE_REPAIR_20261120',
        'MOD4V3_UNIFIED_SILKY_LOCO_GPU_RL_20261121', 'MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121')]
    folders += [REPO/'deliveries/MOD4v4gemini_20261121',
                REPO/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/plant',
                REPO/'deliveries/MOD4V3_LOW_PITCH_20261116']
    result = {E0_PATH, JUMP_PATH}
    for folder in folders:
        if folder.exists():
            result.update(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in
                          ('.py', '.pt', '.pth', '.bat', '.json', '.xml', '.usd', '.usda', '.usdc')
                          and '__pycache__' not in p.parts and 'kit_isolation' not in p.parts)
    result.update(REPO.glob('deliveries/CURRENT*.json'))
    return sorted(result)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify', action='store_true')
    args = p.parse_args()
    baseline = HERE/'evidence/PROTECTION_BASELINE.json'
    if args.verify:
        import json
        old = json.loads(baseline.read_text(encoding='utf-8'))['sha256']
        missing = [n for n in old if not Path(n).is_file()]
        changed = [n for n,v in old.items() if Path(n).is_file() and sha256(n) != v]
        put(HERE/'evidence/PROTECTION_VERIFICATION.json', dict(files=len(old), missing=missing,
            changed=changed, passed=not missing and not changed, utc=datetime.now(timezone.utc).isoformat()))
        print(f'Protection: {len(old)} files; {len(changed)} changed; {len(missing)} missing', flush=True)
        if missing or changed:
            raise RuntimeError('Protected assets changed')
    else:
        if baseline.exists():
            raise FileExistsError('Existing baseline is retained')
        values = {str(p):sha256(p) for p in paths()}
        put(baseline, dict(utc=datetime.now(timezone.utc).isoformat(), sha256=values))
        print(f'Protection baseline: {len(values)} files', flush=True)

if __name__ == '__main__':
    main()

