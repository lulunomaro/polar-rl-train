"""One finite read-only capability check through the existing H1 transport.

No controller starts, GPU enumeration, lease change, model read or physics call.
"""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
N = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102/runs/h1_target_limit_cont_20261103')


def main():
    report = HERE/'EXISTING_REMOTE_RUNTIME_CAPABILITIES.json'
    if report.exists():
        raise FileExistsError('Existing capability receipt must not be replayed')
    spec = importlib.util.spec_from_file_location('existing_h1_read_transport', N/'run.py')
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    # Include this newly named reader in the same fresh local exact-CIM gate.
    # The first call preserved a rejection because the old pattern omitted it.
    def local_rows():
        pattern = original.PATTERN+'|mod4v1_scut|mod4v1-scut-adaptation'
        query = ('Get-CimInstance Win32_Process -Filter "Name=\'python.exe\' OR Name=\'ssh.exe\'" '
                 '| Where-Object { $_.CommandLine -match \''+pattern+'\' } '
                 '| Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress')
        process = subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,
                                 text=True,encoding='utf8',check=True)
        if process.stderr.strip():
            raise RuntimeError(process.stderr)
        value = json.loads(process.stdout) if process.stdout.strip() else []
        return value if isinstance(value,list) else [value]
    original.local_rows = local_rows
    # gate() includes this exact Python process and rejects another known local
    # controller before connection/once. No old training stage is invoked.
    code = '''from pathlib import Path
import json,importlib.metadata as m,importlib.util as u
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
c=json.loads(p.read_bytes())
versions={}
for k in ('rsl-rl-lib','isaaclab','torch','tensordict','pyyaml'):
 try:versions[k]=m.version(k)
 except m.PackageNotFoundError:versions[k]=None
modules={k:u.find_spec(k) is not None for k in ('isaaclab','isaaclab_physx','isaacsim')}
active=c.get('active_segment')
print(json.dumps(dict(epoch=__import__('time').time(),versions=versions,modules=modules,
 canonical_active=active is not None,owner_pid=(active or {}).get('owner_parent_pid'),read_only=True,GPU_scans=0,
 SDK_imports=0,PT_reads=0,physics=0,new_workers=0,canonical_writes=0)))'''
    with original.connection('MOD4V1_SCUT_READONLY_CAPABILITIES_V2') as (client, deploy):
        result = deploy.code(client, deploy.PY72, code, {}, timeout=45)
    report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
