"""One bounded CPU source/API readback before any new GPU action."""
from pathlib import Path
import json,os,time
from read_linux_resume_boundary_actual import connect_linux_only
D=Path(__file__).resolve().parent
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
code=r'''
import inspect,json,psutil,subprocess,shutil,torch
from rsl_rl.runners import OnPolicyRunner
from rsl_rl.modules import MLPModel
print(json.dumps(dict(CUDA_not_initialized=not torch.cuda.is_initialized(),available_RAM=psutil.virtual_memory().available,durable_free=shutil.disk_usage('/mnt/mod4_linux_durable_20261013').free,gpu_compute_processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True),actor_forward=inspect.getsource(MLPModel.forward),runner_logger_type_source=inspect.getsource(OnPolicyRunner.__init__)[-3000:],runner_public_observation_interface=inspect.getsource(OnPolicyRunner.get_inference_policy))))
'''
c=connect_linux_only()
try:
 si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+PY+' -',timeout=45);si.write(code);si.flush();si.channel.shutdown_write();out=so.read();err=se.read();rc=so.channel.recv_exit_status()
 p=D/'reports'/('LEFT_ADMISSION_API_CPU_READBACK_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(code=rc,stdout=out.decode(),stderr=err.decode()),indent=2),encoding='utf8');assert rc==0,str(p)
 v=json.loads(out);print(json.dumps(v))
finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
