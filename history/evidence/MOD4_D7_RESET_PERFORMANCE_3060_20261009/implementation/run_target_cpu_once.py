"""CPU-only tests in evaluation host's actual Torch runtime; no CUDA context."""
from pathlib import Path
import sys,json,base64,time
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();dest='D:/MOD4_async_eval/d7_reset_performance_cpu'
try:
 with c.open_sftp() as f:
  try:f.mkdir(dest)
  except OSError:f.stat(dest)
  names={'selected_com_readback.py':D/'selected_com_readback.py','test_selected_com.py':D/'test_selected_com.py',
       'test_chassis_pose_roundtrip_cpu.py':D.parent/'MOD4_D7_COM_PD_PREPARE_20261009/test_chassis_pose_roundtrip_cpu.py'}
  for name,p in names.items():
   target=dest+'/'+name
   try:f.stat(target)
   except FileNotFoundError:pass
   else:raise AssertionError('CPU fixture already exists')
   with f.open(target,'wb') as out:out.write(p.read_bytes())
  runtime='D:/MOD4_async_eval/closure_episode_clock2500_v15/runtimes/8e72690e21a414e39cad6295fcae8444b01e9bc4a37d13f7d09676583dd6ae70/runtime/isaac/mod4'
  code="import sys,json,torch;sys.path.insert(0,"+repr(runtime)+");sys.path.insert(0,"+repr(dest)+");import test_selected_com;v=test_selected_com.main();v.update(Torch=torch.__version__,actual_target_runtime=True);print(json.dumps(v))"
  encoded=base64.b64encode(code.encode()).decode()
  ps="$env:PYTHONIOENCODING='utf-8'; & 'D:\claude2\fangzhen\.venv-isaaclab\Scripts\python.exe' -c \"import base64;exec(base64.b64decode('"+encoded+"'))\""
  _,o,e=c.exec_command('powershell -NoProfile -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45)
  raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  v=json.loads(raw);assert not v['CUDA_initialized'] and len(v['passed'])==9
  (R/'TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
