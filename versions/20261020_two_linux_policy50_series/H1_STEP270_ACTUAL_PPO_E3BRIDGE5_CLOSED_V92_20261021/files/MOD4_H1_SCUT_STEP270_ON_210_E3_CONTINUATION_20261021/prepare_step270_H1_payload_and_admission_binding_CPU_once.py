"""Prepare H1 only before E3 closes; no new remote root, GPU or GO."""
from pathlib import Path
import ast, hashlib, importlib.util, json, os, shutil, time, traceback

T=Path(__file__).resolve().parent
W=T.parent
R=T/'reports'
N=T/'H1_STEP270_E3_PAIR_V1_20261021'
OLD=W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())

def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def linkcopy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    try:os.link(src,dst)
    except OSError:shutil.copy2(src,dst)

def main():
    report=read(R/'STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_ACTUAL.json')
    assert report['passed_independent_whole_production_source_and_RSL_CPU'] and not N.exists()
    (N/'reports').mkdir(parents=True)
    put(N/'reports/H1_PAYLOAD_PREPARE_STARTED_ACTUAL.json',dict(epoch=time.time(),no_GPU_or_GO=True))
    dest=N/'payloads/h1';dest.mkdir(parents=True)
    m=read(OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');rows=[]
    for row in m['files']:
        rel=row['relative']
        if rel.startswith(('job0/runtime/','job0/assets/','lib/')):
            src=OLD/rel
            assert src.stat().st_size==row['bytes']
            linkcopy(src,dest/rel)
            rows.append(dict(row))
    assert len(rows)==433
    source=read(R/'STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json')['source']
    assert source['SHA']==report['source_SHA'] and source['Adam']==674740
    source_filename='H1_hour16_model_update42.pt'
    linkcopy(Path(source['path']),dest/'job0/source'/source_filename)
    shutil.copy2(OLD/'job0/original_run_manifest.json',dest/'job0/original_run_manifest.json')
    for path in (T/'production_candidate_V1_UNINSTALLED').glob('*.py'):shutil.copy2(path,dest/path.name)
    shutil.copy2(T/'admitted_step270_existing_native_query_CPU_v1.py',dest/'admitted_existing_same_source_native_CPU_v1.py')
    shutil.copy2(T/'target_H1_step270_source_sdk_cpu_review_v1.py',dest/'target_H1_step270_source_sdk_cpu_review_v1.py')
    controllers=N/'controllers'
    shutil.copytree(T/'controllers_candidate_v2_uninstalled',controllers)
    path=controllers/'three_real_gpu_resource_v1.py';text=path.read_text('utf8')
    old=" elif kind=='observation':"
    addition=""" elif kind=='step270_completed':
  e=json.loads((old/'PARENT_EXIT_ACTUAL.json').read_bytes());p=json.loads((old/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert e['all_own_children_waited'] and e['own_eval_lease_released'] and p['actual_child_waited'] and p['returncode']==0 and not p['own_timeout'] and p['passed'] and not p['errors']
 elif kind=='observation':"""
    assert text.count(old)==1;text=text.replace(old,addition);path.write_text(text,encoding='utf8',newline='\n')
    for path in controllers.glob('*.py'):shutil.copy2(path,dest/path.name)
    names=[
        'STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json',
        'STEP270_FULL20K_NATIVE180_V3_ORIGINAL_ACTOR_MEAN_CPU_ACTUAL.json',
        'STEP270_FULL20K_NATIVE180_V3_EVENTS_SCUT_REFERENCE_CPU_ACTUAL.json',
        'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_V2_ACTUAL.json',
        'STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_ACTUAL.json',
    ]
    proofs=[]
    for name in names:
        relative='admission_proofs/'+name
        (dest/relative).parent.mkdir(exist_ok=True)
        shutil.copy2(R/name,dest/relative)
        proofs.append(dict(relative=relative,SHA=H(dest/relative)))
    binding=dict(key='h1',source_SHA=source['SHA'],source_Adam=674740,
                 GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',
                 native_root='/mnt/mod4_linux_durable_20261013/H1step270_full20k_native180_2110v3',
                 query_root='/mnt/mod4_linux_durable_20261013/H1step270_cookedquery_full20k_2110v9',
                 reports=proofs,not_another_native_or_query_launch=True)
    put(dest/'STEP270_NATIVE_QUERY_PRODUCTION_ADMISSION_BINDING.json',binding)
    task=read(OLD/'job0/TASK.json')
    task.update(id='H1_STEP270_SCUT_PAIR_V1_20261021',kind='H1_STEP270_SCUT_100HZ',source_SHA=source['SHA'],
                source_filename=source_filename,source_Adamstep=674740,source_policy_hz=100,policy_hz=100,
                explicit_step270_task_migration=True,old_prelaunch_scope_not_admitted=True)
    put(dest/'job0/TASK.json',task)
    # Do not carry old target72 source identity or old native authorization into this new task.
    manifest=dict(key='h1',source_SHA=source['SHA'],source_filename=source_filename,source_Adamstep=674740,
                  execution_backend='source210',policy_hz=100,
                  expected_actual_RSL_sources=m['expected_actual_RSL_sources'],
                  expected_actual_SDK_math_SHA=m['expected_actual_SDK_math_SHA'],
                  new_step270_scope_only=True,actual_native3_and_query9_reuse_binding=binding)
    prior={x['relative']:x for x in rows}
    files=[]
    for p in sorted(dest.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(dest).as_posix()
        if p.suffix=='.py':ast.parse(p.read_text('utf8'))
        sha=prior[rel]['SHA'] if rel in prior else source['SHA'] if rel=='job0/source/'+source_filename else H(p)
        files.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
    manifest['files']=files
    put(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',manifest)
    spec=dict(key='h1',GPU_UUID=binding['GPU_UUID'],execution_backend='source210',
              python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',
              source_SHA=source['SHA'],source_filename=source_filename,source_Adamstep=674740,
              policy_hz=100,source_policy_hz=100,native_controls=180,
              production_script='h1_step270_production_worker_v1.py',
              native_script='UNUSED_NO_NATIVE_REPLAY.py',native_CPU_script='UNUSED_NO_NATIVE_REPLAY_CPU.py',
              reuse_completed_native=True,max_parent_seconds=3900,exit_headroom_seconds=300,
              private_lock='/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock',
              previous_runtime_root=binding['native_root'],previous_exit_kind='step270_completed',
              manifest_SHA=H(dest/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
    module=importlib.util.spec_from_file_location('loader',T/'admitted_step270_existing_native_query_CPU_v1.py')
    loader=importlib.util.module_from_spec(module);module.loader.exec_module(loader)
    assert loader.validate(binding,spec,manifest,[read(R/n) for n in names])
    cfg=dict(sequence=1,cohort_id='H1_STEP270_E3_PAIR_V1_20261021',
             previous_stage_dir=str(T/'E3_bridge_continuation_V5'),
             previous_actual_run_id='RECOVERY_WHILE_H1_NATIVE210_ORIGINAL_1792593208045571700',
             owner_root='/mnt/mod4_linux_durable_20261013/H1step270_joint_2110v1/owner',
             roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_joint_2110v1/h1',
                        recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_joint_2110v1/recovery'))
    put(N/'PAIR_RESERVED_SOURCE_CONFIG_NO_TOKEN.json',cfg)
    result=dict(epoch=time.time(),passed_H1_payload_source_and_reuse_binding_CPU_only=True,
                payload=str(dest),spec=spec,source=source,controllers=str(controllers),
                manifest_SHA=spec['manifest_SHA'],files=len(files),native_GPU_not_replayed=True,
                current_E3_bridge5_not_claimed_closed=True,no_remote_root_or_Task_or_GO=True,
                E3_latest_source_not_prepared_until_actual_closed=True)
    put(N/'reports/H1_STEP270_PAYLOAD_AND_EXISTING_NATIVE_QUERY_BINDING_CPU_ACTUAL.json',result)
    print(json.dumps(dict(prepared=True,H1_files=len(files),H1_GO=False,E3_source_pending_actual_closure=True)))

if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('STEP270_H1_PAYLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_GO_or_retry=True))
        raise
