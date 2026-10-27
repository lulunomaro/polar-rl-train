"""Finite read-only existing pinned249 metadata. Never launch SDK/GPU or inspect unknown PID."""
from pathlib import Path
import base64, hashlib, importlib.util, json, os, subprocess, sys, time, traceback

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
REPORT = HERE / "reports/EXISTING249_GPU_UUID_SDK_METADATA_ACTUAL_V1.json"
PY = "D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe"
CODE = r'''
from pathlib import Path
import importlib.util, importlib.metadata as md, json, os, shutil, subprocess, sys, time
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=20)
 return dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
mods={}
for name in ('torch','isaaclab','isaacsim','rsl_rl','numpy','mujoco','psutil'):
 try:
  found=importlib.util.find_spec(name);mods[name]=None if found is None else found.origin
 except Exception as e:mods[name]=dict(error=repr(e))
versions={}
for name in ('torch','isaacsim','rsl-rl-lib','numpy','mujoco','isaaclab'):
 try:versions[name]=md.version(name)
 except md.PackageNotFoundError:versions[name]=None
print(json.dumps(dict(epoch=time.time(),executable=sys.executable,version=sys.version,
 gpu=run(['nvidia-smi','--query-gpu=uuid,name,memory.total,memory.free,utilization.gpu','--format=csv,noheader']),
 compute_UUID_only=run(['nvidia-smi','--query-compute-apps=gpu_uuid,used_gpu_memory','--format=csv,noheader']),
 modules=mods,versions=versions,D_disk=dict(zip(('total','used','free'),shutil.disk_usage('D:/'))),
 old_shared_lock_exists=Path('D:/MOD4_async_eval/worker.lock').exists(),
 no_GPU_SDK_import_or_unknown_PID_inspection_or_mutation=True)))
'''

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def main():
    assert not REPORT.exists()
    cim = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
        f"Get-CimInstance Win32_Process -Filter 'ProcessId = {os.getpid()}' | Select-Object ProcessId,ExecutablePath,CommandLine,CreationDate | ConvertTo-Json -Compress"],
        capture_output=True, text=True, timeout=15)
    assert cim.returncode == 0
    self_cim = json.loads(cim.stdout)
    assert str(Path(sys.executable)).lower() == str(Path(self_cim["ExecutablePath"])).lower()
    assert str(HERE) in self_cim["CommandLine"]
    save(HERE / "reports/EXACT_LOCAL_FINITE249_SELF_CIM_V1.json", self_cim)
    sys.path.insert(0, str(W / "RM2026_TERRAIN_AUDIT_20261009"))
    from reuse_authorized_session_transport import recover
    secret, _ = recover("MOD4_EVAL_SSH_PASSWORD")
    assert secret
    os.environ["MOD4_EVAL_SSH_PASSWORD"] = secret
    sys.path.insert(0, str(W / "MOD4_MOE_PLAN_EXECUTION_20261007"))
    from eval_remote_io import connect_eval, HOST_SHA
    assert HOST_SHA == "95b8067b17fc5331aac5e2d46acd6a087c46719dc853658b14bfa0e29e69242e"
    client = None
    try:
        client = connect_eval()
        encoded = base64.b64encode(CODE.encode()).decode()
        command = '"' + PY + '" -X utf8 -c "import base64;exec(base64.b64decode(\'' + encoded + '\'))"'
        _, out, err = client.exec_command(command, timeout=90)
        raw, error = out.read(), err.read()
        rc = out.channel.recv_exit_status()
        assert rc == 0, (rc, error.decode("utf8", "replace"))
        value = json.loads(raw)
        value.update(attempt_id="FROZEN_EXPERTS249_READONLY_METADATA_20261027_V1", host="10.24.4.249",
                     pin=HOST_SHA, Git_status="pending_root_ordinary_supplement", no_budget_or_training=True)
        save(REPORT, value)
        print(json.dumps({"report": str(REPORT), "gpu": value["gpu"], "SDK_imported": False}))
    finally:
        if client:
            client.close()
        os.environ.pop("MOD4_EVAL_SSH_PASSWORD", None)
        secret = None

if __name__ == "__main__":
    try:
        main()
    except Exception:
        save(HERE / ("reports/READ249_ORIGINAL_ERROR_" + str(time.time_ns()) + ".json"),
             {"epoch": time.time(), "traceback": traceback.format_exc(), "no_training": True})
        raise
