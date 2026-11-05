"""New purpose after A2 actual all-own wait/settle/release; diagnose shared D0 before eight more families."""
from pathlib import Path
import json,ast
D=Path(__file__).resolve().parent
closed=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=closed['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert closed['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert all(row.get('V2_NATIVE_INITIALIZED.json')is None and row.get('V2_LEARNER_LOADED.json')is None for row in closed['cases'].values())
orig=(D/'source_owner_v1/migration_nine_original_owner_v1.py').read_text(encoding='utf8');s=orig
x="pending=list(plan['entries']);c=None";assert s.count(x)==1;s=s.replace(x,x+";native_gate_role=plan.get('native_asset_gate_role');native_gate_ready=not bool(native_gate_role)")
x='   for u in UUIDS:\n    if u in slots:continue';assert s.count(x)==1
block='''   if not native_gate_ready:
    gate_entry=next(e for e in plan['entries']if e['role']==native_gate_role);gate_job=Path(gate_entry['job_root']);native=b.read(gate_job/'production/V2_NATIVE_INITIALIZED.json')
    if native is not None:
     require(native['role']==native_gate_role and native['run_id']==run and native['owner_pid']==os.getpid()and native['num_envs']==20000 and native['source_weights_opens']==native['source_decodes']==0 and native['pretraining_validation_controls']==1 and native['pretraining_validation_physics_steps']==8 and native['pretraining_validation_feedback_ticks']==2 and native['source_env_state_applied']is False,'Shared native D0 gate must be actual fresh V2 before source PT')
     native_gate_ready=True;put(B/'SHARED_V2_NATIVE_GATE_PASSED.json',dict(epoch=time.time(),role=native_gate_role,run_id=run,native_receipt_SHA=b.H(gate_job/'production/V2_NATIVE_INITIALIZED.json'),worker_pid=native['pid'],no_skill_claim=True))
    elif gate_entry['role_key']in rows:
     blocked_families.update(e['source_family']for e in pending);put(B/'SHARED_V2_NATIVE_GATE_FAILED.json',dict(epoch=time.time(),role=native_gate_role,all_following_roles_not_started=True,pending_roles=[e['role']for e in pending],no_unchanged_shared_asset_failure_replay=True));errors.append(dict(shared_native_gate_failed=native_gate_role,remaining_roles_not_started=True))
'''
s=s.replace(x,block+x)
x="eligible=next((e for e in pending if e['source_family']not in blocked_families),None)";assert s.count(x)==1;s=s.replace(x,"eligible=next((e for e in pending if e['source_family']not in blocked_families and(native_gate_ready or e['role']==native_gate_role)),None)")
out=D/'source_owner_v2_native_gate/migration_nine_original_owner_v1.py';assert not out.exists();ast.parse(s);compile(s,str(out),'exec')
a=ast.parse(orig);b=ast.parse(s)
for name in('gpu','account','environment','verify_sources','task_and_go','qualify_v2_waited'):
 before=next(n for n in a.body if isinstance(n,ast.FunctionDef)and n.name==name);after=next(n for n in b.body if isinstance(n,ast.FunctionDef)and n.name==name);assert ast.dump(before,include_attributes=False)==ast.dump(after,include_attributes=False),name
out.parent.mkdir(parents=True);out.write_text(s,encoding='utf8',newline='\n')
st=(D/'stage_nine_nonpt_runtime_v1.py').read_text(encoding='utf8').replace('worker_mod4v2_expert_migration_v1.py','worker_mod4v2_expert_migration_v2.py').replace('stage_nine_nonpt_runtime_v1.py','stage_nine_nonpt_runtime_v2.py');sp=D/'stage_nine_nonpt_runtime_v2.py';assert not sp.exists();ast.parse(st);compile(st,str(sp),'exec');sp.write_text(st,encoding='utf8',newline='\n')
for old,new in [('stage_nine_migration_admission2_once.py','stage_nine_migration_admission3_once.py'),('dispatch_nine_migration_admission2_once.py','dispatch_nine_migration_admission3_once.py'),('collect_nine_migration_admission2_once.py','collect_nine_migration_admission3_once.py')]:
 t=(D/old).read_text(encoding='utf8').replace('ADMISSION2','ADMISSION3').replace('admission2','admission3');target=D/new;assert not target.exists()
 if old.startswith('stage_'):
  t=t.replace("z=json.loads((D/'ADMISSION1_PREIMPORT_FAILURE_TRUTH.json').read_bytes());assert z['all9_GO_SDK_source_input_or_PPO']==0 and z['failed_before_original_main_or_locks']is True;", "truth=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());end=truth['metadata']['OWNER_EXIT_ACTUAL.json'];assert truth['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released')) and all(v.get('V2_LEARNER_LOADED.json')is None for v in truth['cases'].values());")
  t=t.replace('source_owner_v1/migration_nine_original_owner_v1.py','source_owner_v2_native_gate/migration_nine_original_owner_v1.py').replace('worker_mod4v2_expert_migration_v1.py','worker_mod4v2_expert_migration_v2.py').replace('stage_nine_nonpt_runtime_v1.py','stage_nine_nonpt_runtime_v2.py')
  t=t.replace("order=['E0','H1_normal'", "order=['H1_normal','E0'")
  t=t.replace("host86_excluded=True,native0PT_status=", "host86_excluded=True,native_asset_gate_role='H1_normal',native0PT_status=")
  start=t.index("  archive=D/'attempts/admission1_executed_owner.py'");finish=t.index('  mkdirs(remote)',start);t=t[:start]+t[finish:]
  # Import-only preflight of original common + authority + new owner functions;
  # deliberately not __main__, no resource/SDK/model calls.
  anchor="r=dict(epoch=time.time(),run_id=run,root=remote,returncode=rc,stdout=stdout,stderr=stderr,uploaded_nonPT_files=len(payload)"
  assert anchor in t
  t=t.replace(";r=dict(epoch=time.time(),run_id=run,root=remote,returncode=rc", ";assert rc==0;precode='import sys,runpy;sys.path.insert(0,'+repr(remote)+');runpy.run_path('+repr(remote+'/migration_nine_original_owner_v1.py')+\",run_name='source_dependency_preflight_not_main');print('owner_import_only_passed_no_GO_SDK_models_or_locks')\";pi,po,pe=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(precode),timeout=60);pi.close();preout=po.read().decode();preerr=pe.read().decode();prc=po.channel.recv_exit_status();assert prc==0,(preout,preerr);r=dict(owner_import_only_preflight_rc=prc,owner_import_only_preflight_stdout=preout,epoch=time.time(),run_id=run,root=remote,returncode=rc")
 if old.startswith('collect_'):
  t=t.replace("'V2_NATIVE_INITIALIZED.json'", "'V2_NATIVE_LIMIT_READBACK.json','V2_NATIVE_INITIALIZED.json'",1)
 ast.parse(t);compile(t,str(target),'exec');target.write_text(t,encoding='utf8',newline='\n')
(D/'ADMISSION2_CLOSED_FAILURE_TRUTH.json').write_text(json.dumps(dict(root=closed['root'],actual_outer_wait=outer,actual_owner_exit=end,all_learners_loaded=False,new_PPO_updates=0,shared_native_failure='H1 actual left_rocker_pin limit mismatch, observed values absent in v1; readback added only in new worker',legacy_launcher_job_storage_error_fixed_only_in_new_worker=True,newpurpose_first_H1_native_gate_then_other_families=True,old_sources_assets_Registry_canonical_not_modified=True),indent=2),encoding='utf8')
print('A3 sources prepared; original budget/resources/account/wait functions exact; H1 actual native gate protects other families; no SDK/PT/SSH/GO execution')
