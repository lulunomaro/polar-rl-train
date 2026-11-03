"""One new CPU contract purpose: actual original two sensor classes, own synthetic inputs."""
from pathlib import Path
import sys,json,hashlib,ast,time,shlex
R=Path(__file__).resolve().parent;marker=R/'PAPER_ALIGNED_REBUILD_20261103/SENSOR_REFERENCE_CPU_V1_STARTED_ONCE.json';out=R/'reports/PHASE1_SENSOR_REFERENCE_CPU_V1.json';assert not marker.exists()and not out.exists();src=R/'discovery/reward_command_audit_v1/E3/runtime/isaac/mod4';payload={};pins={}
for name,sha in {'sensor_mild_math.py':'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8','feedback_delay_mild.py':'90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'}.items():
 raw=(src/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;ast.parse(raw);payload[name]=raw;pins[name]=dict(bytes=len(raw),SHA256=sha)
script_name='phase1_sensor_reference_cpu_v1.py';raw=(R/'PAPER_ALIGNED_REBUILD_20261103'/script_name).read_bytes();ast.parse(raw);payload[script_name]=raw;pins[script_name]=dict(bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest());B='/home/lc01/Zonglin Li/zonglin2';job=B+'/tasks/PHASE1_SENSOR_REFERENCE_CPU_V1_'+str(time.time_ns());result=job+'/REFERENCE_RESULT_V1.json';script=job+'/'+script_name
marker.write_text(json.dumps(dict(kind='NEW_PHASE1_SOURCE_TORCH_CPU_REFERENCE',epoch=time.time(),remote_root=job,source_pins=pins,SDK_model_GPU_canonical_operations=0,passive_tap_tested=False),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 try:s.lstat(job)
 except FileNotFoundError:pass
 else:raise AssertionError('New CPU reference root already exists')
 s.mkdir(job)
 for name,data in payload.items():
  with s.open(job+'/'+name,'wb')as f:f.write(data)
 code="import os,sys,runpy;os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1';sys.path.insert(0,%r);sys.argv=%r;runpy.run_path(%r,run_name='__main__')"%(job,[script,'--source-dir',job,'--output',result],script)
 i,o,e=c.exec_command("CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "+shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();text=o.read().decode('utf-8','replace');err=e.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_PHASE1_TORCH_CPU_ORIGINAL_SENSOR_REFERENCE_V1',remote_root=job,source_pins=pins,returncode=rc,stdout=text,stderr=err,native_updates=0,selected_model_raw_or_SDK_GPU_canonical_operations=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err
 with s.open(result,'rb')as f:value['receipt']=json.loads(f.read())
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');v=value['receipt'];assert v['status']=='PASS'and v['passive_tap_installed_or_tested']is False and v['global_RNG_unchanged']is True
 print(json.dumps(dict(report=str(out),status=v['status'],checks=v['checks'],draw_counts=v['per_channel_actual_draw_counts'],actual_age_us=v['observed_age_us_counts'],real_source_classes=True,synthetic_input_not_native_interface_pass=True),indent=2))
finally:s.close();c.close()
