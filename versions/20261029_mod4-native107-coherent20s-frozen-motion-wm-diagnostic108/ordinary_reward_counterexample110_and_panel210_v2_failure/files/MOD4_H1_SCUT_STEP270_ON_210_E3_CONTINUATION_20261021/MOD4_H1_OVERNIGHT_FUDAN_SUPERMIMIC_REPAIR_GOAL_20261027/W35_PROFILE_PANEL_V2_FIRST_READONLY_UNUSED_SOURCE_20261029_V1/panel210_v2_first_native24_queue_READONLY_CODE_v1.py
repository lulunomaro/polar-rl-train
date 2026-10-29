from pathlib import Path
import hashlib,json,os,time

J=Path(v['job']);assert J.resolve()==J
expected=v['supervisor'];F=J/'frozen_regression'
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def state(row):
    p=Path('/proc')/str(row['pid'])
    try:
        raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
        boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
        creation=boot+int(fields[19])/os.sysconf('SC_CLK_TCK')
    except FileNotFoundError:return dict(original_out=True,expected=row,reason='known original PID absent')
    if creation!=row['creation']:return dict(original_out=True,expected=row,reason='PID reused; no new exe/argv inspected')
    return dict(original_out=fields[0]=='Z',expected=row,state=fields[0],creation=creation)

restore=F/'ACTUAL_ORIGINAL_N20K_W35_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json'
native=F/'ACTUAL_NATIVE24_W35_40050_MEAN.json'
panel=F/'ACTUAL_NATIVE24_W35_PROFILE_PANEL_CLOCK_QUEUE_ACTUAL.json'
terminal=J/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json'
deadline=time.monotonic()+270
while True:
    errors=list(F.glob('*ORIGINAL_ERROR*.json')) if F.exists() else []
    errors+=list(J.glob('*SUPERVISOR_ORIGINAL_ERROR*.json'))
    preclose=F/'FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json'
    if preclose.is_file():errors.append(preclose)
    errors=sorted(set(errors))
    if (restore.is_file() and native.is_file() and panel.is_file()) or errors or terminal.is_file() or time.monotonic()>=deadline:break
    time.sleep(1)

integrity=[]
sup_receipt=read(J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json')
if sup_receipt!=expected:integrity.append(dict(reason='supervisor identity receipt missing or differs',actual=sup_receipt,expected=expected))
worker=read(J/'OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json')
worker_valid=False
if worker:
    expected_argv=[expected['argv'][0],'-u','-B',str(J/v['worker_basename']),'--job-root',str(J)]
    worker_valid=bool(worker['root']==str(J) and worker['exe']==expected['exe'] and worker['argv']==expected_argv and expected['creation']<=worker['creation']<=expected['creation']+1800)
    if not worker_valid:integrity.append(dict(reason='worker receipt differs from exact bound source/argv/root; no PID queried',worker=worker))
rr=read(restore);nn=read(native);pp=read(panel);tt=read(terminal)
checks={
 'original_CUDA_fullrestore':bool(rr and rr.get('passed') and rr.get('source_SHA')==v['model_SHA'] and rr.get('Adam_step')==648360),
 'original_native24':bool(nn and nn.get('passed') and nn.get('controls')==24 and nn.get('physics_callbacks')==192 and nn.get('feedback_samples')==48 and nn.get('policy_hz')==50 and nn.get('nominal_force_N_each')==400),
 'panel_native24_queue':bool(pp and pp.get('passed') and pp.get('controls')==24 and pp.get('physics_callbacks')==192 and pp.get('feedback_samples')==48 and pp.get('queue_apply_calls_per_group')=={'legs':192,'wheels':192} and pp.get('actual_first24_trace_controls')==list(range(1,25))),
 'panel_source_binding':bool(pp and pp.get('source_SHA')==v['model_SHA'] and pp.get('panel_worker_SHA')==v['worker_SHA'] and pp.get('panel_component_SHA')==v['component_SHA']),
 'panel_clock_and_frozen_state':bool(pp and pp.get('policy_hz')==50 and pp.get('physics_us')==2500 and pp.get('control_us')==20000 and pp.get('original_D1_D7_fullrestore_before_mean') and pp.get('Adam648360_unchanged') and pp.get('no_optimizer_norm_or_extra_actor_call')),
 'panel_actual_queue_counter_difference':bool(pp and all(pp.get('queue_calls_after24',{}).get(k,-999999)-pp.get('queue_calls_at_start',{}).get(k,999999)==192 for k in ('legs','wheels'))),
 'worker_identity_bound':worker_valid,
}
if tt and (tt.get('supervisor')!=expected or (worker and tt.get('worker')!=worker)):
    integrity.append(dict(reason='terminal identities differ from bound own receipts'))
paths=[J/'ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',J/'FROZEN_CASE_TASK.json',
       J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json',J/'OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json',
       J/'OWN_PRIVATE210_EX_ACQUIRED_FOR_FROZEN_EVAL.json',J/'FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json',
       J/'FROZEN_W35_SUPERVISOR_COMPLETE_STDOUT_STDERR.log',J/'FROZEN_W35_WORKER_COMPLETE_STDOUT_STDERR.log',restore,native,panel,terminal]+errors
texts=[]
for p in sorted(set(paths)):
    if not p.is_file():continue
    assert p.resolve().is_relative_to(J) and not p.is_symlink()
    before=p.stat();raw=p.read_bytes();after=p.stat()
    texts.append(dict(path=str(p),relative=p.relative_to(J).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf-8'),stable_during_read=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),first_snapshot_not_final_index=True))
passed=bool(all(checks.values()) and not errors and not integrity)
print(json.dumps(dict(epoch=time.time(),passed_profile_panel_GPU_fullrestore_native24_and_group_queue192=passed,
    source_SHA=v['model_SHA'],worker_source_SHA=v['worker_SHA'],component_source_SHA=v['component_SHA'],proof_checks=checks,
    supervisor_state=state(expected),worker_state=state(worker) if worker_valid else None,
    restore=rr,native24=nn,panel_native24_queue=pp,original_terminal_if_present=tt,
    original_errors=[dict(path=str(p),value=read(p)) for p in errors],integrity_errors=integrity,
    complete_original_read_texts=texts,full600_profile_coverage_not_determined_by_first=True,
    no_GPU_query_lock_model_NPZ_actor_optimizer_or_Cwrite=True,no_launcher_retry_or_stop=True,
    firstreader_not_skill_graduation=True)))
