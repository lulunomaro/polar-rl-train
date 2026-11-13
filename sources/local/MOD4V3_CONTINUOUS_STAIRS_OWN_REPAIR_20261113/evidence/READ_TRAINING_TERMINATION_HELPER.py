from pathlib import Path
import sys,json,shlex
T=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113');sys.path.insert(0,str(T));from remote_run import P,connect,execute
code='import os,sys,json,importlib.util,inspect;os.environ["MOD4_SCUT_SOURCE_PATHS"]='+repr(P['source_paths'])+';sys.path[:0]='+repr([P['shared_package'],P['support']])+';spec=importlib.util.spec_from_file_location("own_reward_cfg",'+repr(P['support']+'/mod4v3_ppo_v1/scut_flat_rewards.py')+');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);cfg=mod.configuration_v2();print(json.dumps({k:getattr(cfg,k,None) for k in ["termination_duration_enabled","termination_duration_steps","termination_roll_deg","termination_pitch_deg","termination_contact_force","termination_min_height"]}));print(inspect.getsource(mod.Base._get_dones));print(inspect.getsource(mod.Base._apply_termination_duration))'
c=connect()
try:out=execute(c,shlex.quote(P['python'])+' -B -c '+shlex.quote(code))
finally:c.close()
print(out);(T/'evidence/TRAINING_TERMINATION_READBACK_20261113.txt').write_text(out,encoding='utf8')
