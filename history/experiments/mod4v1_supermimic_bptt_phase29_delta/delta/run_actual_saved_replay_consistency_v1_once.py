"""One new actual own-checkpoint CPU posthoc diagnostic per role, no training or SDK.
Requires actual synthetic+predecode PASS and a parent-read independent source review.
"""
from pathlib import Path
import argparse,json,hashlib,time,shlex,sys
R=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--role',choices=('E3','W35'),required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--review-sha',required=True);args=p.parse_args();role=args.role
review=args.review.resolve();assert review.is_relative_to(R/'source_replay_diagnostic_parent_review_v1');reviewraw=review.read_bytes();assert hashlib.sha256(reviewraw).hexdigest()==args.review_sha
marker=R/('ACTUAL_SAVED_REPLAY_CONSISTENCY_'+role+'_V1_STARTED_ONCE.json');out=R/'reports'/('ACTUAL_SAVED_REPLAY_CONSISTENCY_'+role+'_V1.json');assert not marker.exists()and not out.exists()
smoke=json.loads((R/'reports/REPLAY_CONSISTENCY_TORCH_SMOKE_V1.json').read_bytes());assert smoke['returncode']==0 and smoke['receipt']['status']=='PASS'
pre=json.loads((R/'reports/REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_V1.json').read_bytes());assert pre['returncode']==0 and pre['receipt']['Python_RNG_unchanged_across_exact_source_runtime']is True and pre['receipt']['CUDA_initialized']is False
pins=json.loads((R/'reports/REPLAY_DIAGNOSTIC_ACTUAL_FINAL_TASK_PINS_V1.json').read_bytes());assert pins['all_four_actual_JSON_pins_and_predecode_contracts_passed']is True;meta=pins['roles'][role];assert meta['actual_final_contract_passed']is True and meta['actual_task_identity_passed']is True
source=smoke['remote_root'];B='/home/lc01/Zonglin Li/zonglin2';assert source.startswith(B+'/tasks/REPLAY_CONSISTENCY_TORCH_SMOKE_V1_');base=B+'/tasks/MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100/roles/E0/worker_sources';job=B+'/tasks/ACTUAL_POSTHOC_REPLAY_CONSISTENCY_'+role+'_V1_'+str(time.time_ns());script=source+'/replay_consistency_diagnostic_v1.py';result=job+'/'+role+'_posthoc_replay_consistency_v1.json'
argv=[script,'--role',role,'--final',meta['files']['FINAL']['path'],'--final-bytes',str(meta['files']['FINAL']['bytes']),'--final-sha',meta['files']['FINAL']['SHA256'],'--task-bytes',str(meta['files']['TASK']['bytes']),'--task-sha',meta['files']['TASK']['SHA256'],'--bridge-source',source+'/native_supermimic_bridge.py','--core-source',source+'/ctx_reward_full_resume_candidate_v3.py','--raw35-source',source+'/command_tracking_torch_candidate_v1.py','--cache-source',source+'/frozen_a1_raw35_v1.py','--vendor-parent',base,'--dependency-path',base+'/sm_deps','--batch','64','--windows','32','--sample-seed','20261103','--cpu-threads','1','--full-context-openloop','--output',result]
marker.write_text(json.dumps(dict(epoch=time.time(),kind='NEW_ACTUAL_OWN_CHECKPOINT_POSTHOC_REPLAY_CONSISTENCY_V1',role=role,remote_root=job,actual_original_JSON_pins=meta['files'],checkpoint_producer_metadata=meta['checkpoint_producer_metadata'],source_review=dict(path=str(review),SHA256=args.review_sha,parent_read_before_actual_call=True),training_or_SDK_or_GPU_or_canonical_operations=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('Actual new diagnostic purpose root already exists')
 s.mkdir(job)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path[:0]=%r;sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%([source,base+'/sm_deps'],argv,script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=600);i.close();text=o.read().decode('utf-8','replace');err=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status()
 value=dict(kind='ACTUAL_OWN_SAVED_REPLAY_POSTHOC_DIAGNOSTIC_V1',role=role,remote_root=job,returncode=rc,stdout=text,stderr=err,actual_own_model_open_decode_receipt=None,native_BPTT_or_skill_updates=0,interpretation='POSTHOC_REPLAY_RESUBSTITUTION_NOT_HELDOUT_OR_CAUSAL_OR_SKILL')
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err
 with s.open(result,'rb')as f:receipt=json.loads(f.read())
 value['receipt']=receipt;value['actual_own_model_open_decode_receipt']=receipt['execution'];out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 assert receipt['role']==role and receipt['execution']['physical_checkpoint_reads']==1 and receipt['execution']['weights_only_CPU_decodes']==1 and receipt['execution']['mother_checkpoint_reads']==0 and receipt['execution']['native_BPTT_updates_this_diagnostic']==0
 print(json.dumps(dict(report=str(out),role=role,status='DIAGNOSTIC_COMPLETED_NOT_SKILL_PASS',one_step=receipt['one_step']['n'],actor=receipt['actor']['n'],H16_modes=list(receipt['H16']),whole_root_unchanged=receipt['execution']['whole_root_tensor_identity_version_values_unchanged'],native_updates=0),indent=2))
finally:s.close();c.close()
