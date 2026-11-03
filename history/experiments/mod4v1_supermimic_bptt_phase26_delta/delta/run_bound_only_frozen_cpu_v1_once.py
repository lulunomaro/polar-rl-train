"""New CPU-only ZERO_UPDATE bound formula/freeze/whole-cache software purpose.
Only NEW own synthetic PT fixtures; no selected models/SDK/GPU/C/native.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;marker=R/'BOUND_ONLY_FROZEN_CPU_V1_STARTED_ONCE.json';out=R/'reports/BOUND_ONLY_FROZEN_CPU_V1.json';assert not marker.exists()and not out.exists();src=R/'source_bound_only_frozen_probe_v1';pins={'bound_only_frozen_probe_v1.py':(19125,'4a47700a046d6c7d496223f551745c956d3ff693cd0f02c559354a9627bf61a6'),'remote_cpu_bound_only_synthetic_v1.py':(10730,'54c6852638a52504cda5de9c8e03baab5c3c258cb60d9359f1238a2c248ceb7e')};payload={}
for name,(size,sha)in pins.items():
 raw=(src/name).read_bytes();assert len(raw)==size and hashlib.sha256(raw).hexdigest()==sha;payload[name]=raw
evalroot=json.loads((R/'FROZEN_E3_W35_BATCH_V2_SOURCE_INPUT_ONCE.json').read_bytes())['root'];cpuroot='/home/lc01/Zonglin Li/zonglin2/tasks/BOUND_ONLY_ZERO_UPDATE_SOFTWARE_CPU_V1_'+str(time.time_ns());script=cpuroot+'/remote_cpu_bound_only_synthetic_v1.py';result=cpuroot+'/NEW_SYNTHETIC_RESULT';marker.write_text(json.dumps(dict(epoch=time.time(),CPU_software_only=True,root=cpuroot,old_models_opened=0,native_BPTT_steps=0,probe_training_updates=0),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(cpuroot)
 except FileNotFoundError:pass
 else:raise AssertionError('New CPU purpose root exists')
 s.mkdir(cpuroot)
 for name,raw in payload.items():
  with s.open(cpuroot+'/'+name,'wb')as f:f.write(raw)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path[:0]=%r;sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%([cpuroot,evalroot],[script,'--new-output',result],script);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_SOFTWARE_CPU_ZERO_UPDATE_BOUND_ONLY_PROBE_V1',remote_root=cpuroot,eval_static_dependencies=evalroot,source_pins={k:dict(bytes=v[0],SHA=v[1])for k,v in pins.items()},returncode=rc,stdout=text,stderr=err,native_steps=0,original_model_reads=0,probe_training_updates=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err
 with s.open(result+'/REMOTE_CPU_BOUND_ONLY_RESULTS_V1.json','rb')as f:receipt=json.loads(f.read())
 value['receipt']=receipt;out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert receipt['passed']is True;print(json.dumps(dict(report=str(out),CPU_controls=receipt['controls'],formula_error=receipt['maximum_independent_bound_formula_error'],max_component_vs_clipped_teacher=receipt['maximum_action_component_difference_vs_clipped_teacher'],max_component_vs_legacy_unbounded=receipt['maximum_action_component_difference_vs_legacy_unbounded_mean'],RNG_unchanged=receipt['caller_RNG_unchanged'],strict_state_norm_teacher=receipt['full_strict_state_norm_and_teacher_values_match'],constructor_zeroing_safe=receipt['constructor_zeroing_did_not_erase_loaded_weights'],source_cache_io=receipt['receipt_before_negative']['physical_byte_opens'],std_guard=receipt['teacher_STD_guard_detected'],residual_norm_guard=receipt['isolated_residual_norm_guard_detected'],no_original_PT_native_or_training_updates=True),indent=2))
finally:s.close();c.close()
