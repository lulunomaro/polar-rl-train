"""Verify public SCUT archive bytes against the fixed upstream commit, no token."""
import concurrent.futures
import hashlib
import json
import time
import urllib.request
from pathlib import Path

COMMIT = 'b8ff79f3df855faf9dc92f4a282bd80c42649466'
REF = Path('/home/egde/fangzhen_linux/refs/wheeled-legged_RL-main')
OUT = Path('/home/egde/rl_candidates/MOD4_SCUT_ROUGH_V1_PREPARE_20261001')
FILES = [
    'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py',
    'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py',
    'source/agent_tasks/agent_tasks/manager/mdp/__init__.py',
    'source/agent_tasks/agent_tasks/manager/mdp/isaaclab/__init__.py',
    'source/agent_tasks/agent_tasks/manager/mdp/isaaclab/terrains.py',
    'source/agent_tasks/agent_tasks/manager/mdp/isaaclab/terrains_ref.py',
    'source/agent_world/agent_world/terrains/__init__.py',
    'source/agent_world/agent_world/terrains/height_field.py',
]


def verify(name):
    url = f'https://raw.githubusercontent.com/scutrobotlab/wheeled-legged_RL/{COMMIT}/{name}'
    item = {'file': name, 'url': url}
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MOD4-source-audit'})
        with urllib.request.urlopen(req, timeout=25) as response:
            data = response.read()
        dest = OUT / 'pinned_source' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        item.update(upstream_sha256=hashlib.sha256(data).hexdigest(), upstream_bytes=len(data))
        local = REF / name
        item['archive_sha256'] = hashlib.sha256(local.read_bytes()).hexdigest() if local.exists() else None
        item['archive_exact_match'] = item['upstream_sha256'] == item['archive_sha256']
    except Exception as error:
        item['error'] = str(error)
        item['archive_exact_match'] = False
    return item


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        entries = list(pool.map(verify, FILES))
    result = {'created_epoch': time.time(), 'commit': COMMIT, 'files': entries,
              'all_listed_archive_bytes_match': all(x['archive_exact_match'] for x in entries),
              'scope': 'Listed source bytes only; archive has no Git HEAD and unlisted dependencies are not certified.',
              'production_modified': False, 'probe_launched': False}
    (OUT/'PINNED_SOURCE_VERIFICATION.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
