"""One original-resource frozen FDN E3 N80 parent and an actual outer p.wait().
Derived from dispatch_e3_frozen_once.py; no training-root/model access or parent edits.
"""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import shlex
import sys
import time

PREFIX = "FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_"
TASKS = "/home/lc01/Zonglin Li/zonglin2/tasks"
EVAL_KIND = "E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    D = Path(__file__).resolve().parent
    T = D.parent / "mod4v1_experts_fulldr_rm70_20261101"
    stage = json.loads((D / (PREFIX + "STAGE_RESULT.json")).read_bytes())
    need(type(stage["returncode"]) is int and stage["returncode"] == 0 and stage["roles"] == ['E3_LOW80_20261002', 'E3_LOW80_20261003', 'E3_LOW80_20261004'] and
         stage["num_envs"] == 80 and stage["controls"] == 400 and stage["seeds"] == [20261002,20261003,20261004] and
         stage["source_training_num_envs"] == 20000 and stage["assessment_dispatched"] is False,
         "Successful unused one-E3 original N80/160 N20000-source stage required")
    root = stage["root"]
    plan = json.loads((D / (PREFIX + "GROUP_PLAN_SOURCE.json")).read_bytes())
    p = PurePosixPath(root)
    need(p.parent == PurePosixPath(TASKS) and ".." not in p.parts and
         p.name == plan["group_id"] and p.name.startswith(PREFIX + "THREE_SEED_N80_") and
         plan["GPU_UUID"] == stage["GPU_UUID"] == "GPU-16828f91-2b45-b646-8dc0-9481138e2842" and
         len(plan["roles"]) == 3 and [r["role"]for r in plan["roles"]] == ['E3_LOW80_20261002', 'E3_LOW80_20261003', 'E3_LOW80_20261004'], "Own new frozen group binding differs")
    for role in plan["roles"]:
        need(role["controls"]==400 and role["seed"]in(20261002,20261003,20261004)and role["role"]=="E3_LOW80_"+str(role["seed"])and role["runtime_root"]==root+"/runtimes/"+role["role"]and role["kind"]==role["purpose"]==EVAL_KIND and role["evaluation_scope"]=="LOW80_FIVE_POSE16_8S_FULLDR_HOLDOUT_FIRSTEPISODE_CONFIRM"and role["source_training_execution_qualified"]is True and dict(path=role["source_path"],bytes=role["source_bytes"],sha256=role["source_SHA"],run=role["source_run"])==stage["source"],"Each independent low80 case must bind the retained candidate and original closure")
    out = D / (PREFIX + "DISPATCH_RESULT.json")
    mark = D / (PREFIX + "DISPATCH_STARTED_ONCE.json")
    resource_path = D / (PREFIX + "RESOURCE_PRELAUNCH.json")
    need(not any(path.exists() for path in (out, mark, resource_path)), "Unused dispatch once namespace required")
    source = T.parent / "mod4v1_supermimic_bptt_20261102/observe_bound_probe_resources_after_zero_admission_timeout_once.py"
    tree = ast.parse(source.read_bytes())
    query = ast.literal_eval(next(node.value for node in tree.body if isinstance(node, ast.Assign) and
        any(isinstance(target, ast.Name) and target.id == "code" for target in node.targets)))
    need("lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0" in query,
         "Original read-only resource observation changed")
    # Identical original observation and parent resource/cleanup policy; a snapshot is not a lease.
    sys.path.insert(0, str(T))
    from project_connector import connect72
    c = s = None
    try:
        c = connect72()
        s = c.open_sftp()
        B = "/home/lc01/Zonglin Li/zonglin2"
        i, o, e = c.exec_command(shlex.quote(B + "/run-python.sh") + " -B -c " + shlex.quote(query), timeout=60)
        i.close()
        stdout, stderr = o.read().decode("utf8", "replace"), e.read().decode("utf8", "replace")
        rc = o.channel.recv_exit_status()
        need(rc == 0, stderr)
        resource = json.loads(stdout)
        with resource_path.open("x", encoding="utf8") as stream:
            json.dump(resource, stream, indent=2)
        need(float(resource["canonical_summary"]["remaining_training_seconds"]) >
             float(resource["canonical_summary"]["finite_minimum_remaining_seconds"]), "Original finite-resource floor")
        controller = r'''from pathlib import Path
import subprocess,json,os,time,hashlib,traceback
B=Path(ROOT);OWN=Path('/home/lc01/Zonglin Li/zonglin2');assert B.parent==OWN/'tasks'and B.name.startswith('FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_THREE_SEED_N80_')and not(B/'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_OUTER_DISPATCH.json').exists()and not(B/'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_PARENT_WAITED_ACTUAL.json').exists()and not(B/'PARENT_STARTED.json').exists()
def put(name,value):
 p=B/name;q=p.with_suffix('.partial');q.write_text(json.dumps(value,indent=2));q.replace(p)
def identity(pid):
 t=Path('/proc',str(pid),'stat').read_text();v=t[t.rfind(')')+2:].split();return dict(pid=pid,linux_start_ticks=int(v[19]))
plan=json.loads((B/'GROUP_PLAN.json').read_bytes());assert plan['group_id']==B.name and len(plan['roles'])==3 and all(r['role']=='E3_LOW80_'+str(r['seed'])and r['controls']==400 and r['worker']=='worker_sources/parent/worker_fudan_original_n80.py'for r in plan['roles']);pin=next(x for x in plan['worker_files']if x['relative']=='single_gpu_group_supervisor.py');raw=(B/pin['relative']).read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(pin['bytes'],pin['SHA']);child=None;parent=None;errors=[];start=time.time();controller=identity(os.getpid())
try:
 log=(B/'GROUP_SUPERVISOR_STDOUT_STDERR.log').open('xb');child=subprocess.Popen([str(OWN/'run-python.sh'),'-u','-B',str(B/'single_gpu_group_supervisor.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();parent=identity(child.pid);put('FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_OUTER_DISPATCH.json',dict(kind='FDN_N20000_ONE_E3_ORIGINAL_SCOPE_PARENT_NOT_SKILL_ADMISSION',epoch=time.time(),root=str(B),roles=[r['role']for r in plan['roles']],controller=controller,parent=parent,original_parent_SHA256=pin['SHA'],original_parent_Popen_calls=1))
 rc=child.wait()
except BaseException:
 errors.append(traceback.format_exc());rc=child.wait()if child is not None else None
finally:
 put('FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_PARENT_WAITED_ACTUAL.json',dict(kind='FDN_N20000_E3_ACTUAL_EXTERNAL_POPEN_WAIT_V1',epoch=time.time(),root=str(B),roles=[r['role']for r in plan['roles']],controller=controller,parent=parent if child is not None else None,actual_parent_p_wait_returned=child is not None and child.poll()is not None,original_parent_reaped=child is not None and child.poll()is not None,returncode=rc,errors=errors,wall_seconds=time.time()-start,original_parent_Popen_calls=1 if child is not None else 0,controller_Cwrites_model_or_lock_operations=0))
'''.replace("ROOT", repr(root))
        ast.parse(controller)
        with_marker = dict(epoch=time.time(), root=root, GPU_UUID=stage["GPU_UUID"], roles=stage["roles"],
            controller_SHA256=hashlib.sha256(controller.encode()).hexdigest(), source=stage["source"],
            planned_num_envs=80, planned_controls=400, planned_seeds=[20261002,20261003,20261004],
            resource_snapshot_not_lease=True, original_resource_and_close_wait_logic_unchanged=True,
            three_independent_case_cardinality_variant=True)
        with mark.open("x", encoding="utf8") as stream:
            json.dump(with_marker, stream, indent=2)
        with s.open(root + "/fdn_low80_confirm_outer_wait.py", "wx") as stream:
            stream.write(controller.encode())
        start = r'''from pathlib import Path
import subprocess,json,time
B=Path(ROOT);assert B.name.startswith('FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_THREE_SEED_N80_');log=(B/'OUTER_STDOUT_STDERR.log').open('xb');p=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(B/'fdn_low80_confirm_outer_wait.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close()
for _ in range(120):
 q=B/'FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_OUTER_DISPATCH.json'
 if q.exists():print(q.read_text());break
 if p.poll()is not None:raise RuntimeError('Outer exited before dispatch; inspect own log, do not replay')
 time.sleep(.25)
else:raise RuntimeError('No dispatch publication; inspect own process, do not replay')
'''.replace("ROOT", repr(root))
        i, o, e = c.exec_command(shlex.quote(B + "/run-python.sh") + " -B -c " + shlex.quote(start), timeout=60)
        i.close()
        stdout, stderr = o.read().decode("utf8", "replace"), e.read().decode("utf8", "replace")
        rc = o.channel.recv_exit_status()
        value = dict(with_marker, returncode=rc, stdout=stdout, stderr=stderr)
        if rc == 0:
            value["dispatch"] = json.loads(stdout)
        with out.open("x", encoding="utf8") as stream:
            json.dump(value, stream, indent=2)
        print(json.dumps(value, indent=2))
        need(rc == 0, stderr)
    finally:
        if s is not None:
            s.close()
        if c is not None:
            c.close()


if __name__ == "__main__":
    main()
