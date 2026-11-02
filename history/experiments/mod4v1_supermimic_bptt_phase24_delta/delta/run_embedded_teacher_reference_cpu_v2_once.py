"""NEW V2 CPU fixture purpose; preserve failed V1 and original adapter bytes.
Only NEW own synthetic checkpoints; no original models/SDK/GPU/C/native.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;prior=json.loads((R/'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V1.json').read_bytes());assert prior['returncode']==1 and 'original teacher norm/std state missing'in prior['stderr'];marker=R/'EMBEDDED_TEACHER_REFERENCE_CPU_V2_STARTED_ONCE.json';out=R/'reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json';assert not marker.exists()and not out.exists();src=R/'source_frozen_embedded_teacher_reference_v1';pins={'embedded_teacher_reference_v1.py':(16333,'400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407'),'remote_cpu_embedded_teacher_synthetic_v2.py':(16128,'246f8a305d0fed032da964c92b899d731bc81cab61804d901558d1be01dd8a2c')};payload={}
for name,(size,sha)in pins.items():
 raw=(src/name).read_bytes();assert len(raw)==size and hashlib.sha256(raw).hexdigest()==sha;payload[name]=raw
evalroot=json.loads((R/'FROZEN_E3_W35_BATCH_V2_SOURCE_INPUT_ONCE.json').read_bytes())['root'];cpuroot='/home/lc01/Zonglin Li/zonglin2/tasks/EMBEDDED_TEACHER_REFERENCE_SOFTWARE_CPU_V2_'+str(time.time_ns());script=cpuroot+'/remote_cpu_embedded_teacher_synthetic_v2.py';result=cpuroot+'/NEW_SYNTHETIC_RESULT';marker.write_text(json.dumps(dict(epoch=time.time(),CPU_software_only=True,root=cpuroot,old_models_opened=0,native_BPTT_steps=0,prior_fixture_failure_preserved=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(cpuroot)
 except FileNotFoundError:pass
 else:raise AssertionError('New CPU purpose root exists')
 s.mkdir(cpuroot)
 for name,raw in payload.items():
  with s.open(cpuroot+'/'+name,'wb')as f:f.write(raw)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path[:0]=%r;sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%([cpuroot,evalroot],[script,'--new-output',result],script);i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_CPU_SOFTWARE_EMBEDDED_TEACHER_REFERENCE_ONLY_V2',remote_root=cpuroot,eval_static_dependencies=evalroot,source_pins={k:dict(bytes=v[0],SHA=v[1])for k,v in pins.items()},returncode=rc,stdout=text,stderr=err,native_steps=0,original_model_reads=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err
 with s.open(result+'/REMOTE_CPU_EMBEDDED_TEACHER_RESULTS_V2.json','rb')as f:receipt=json.loads(f.read())
 value['receipt']=receipt;out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert receipt['passed']is True;print(json.dumps(dict(report=str(out),CPU_controls=receipt['CPU_reference_controls'],original_RSL_mean_error=receipt['maximum_original_RSL_teacher_error'],candidate_residual_difference=receipt['maximum_candidate_math_teacher_difference'],teacher_norm_status=receipt['teacher_normalization'],teacher_buffer_case=receipt['teacher_buffer_case'],std_value_mutation_detected=receipt['teacher_std_value_mutation_detected'],residual_buffer_case=receipt['residual_buffer_case'],RNG_unchanged=receipt['caller_RNG_unchanged'],old_PT_native_GPU_C=0),indent=2))
finally:s.close();c.close()
