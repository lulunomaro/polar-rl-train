"""Frozen normal86 RSL witness only; own native R5 restoration happens separately."""
from pathlib import Path
import hashlib,json,time
import torch
from fresh_policy_only_bootstrap87_v1 import BOOTSTRAP_SHA,BOOTSTRAP_ADAM,verify_loaded_policy_only_fresh_environment
def resume_RSL_witness_fresh400N(runner,env,path,log_dir):
 path=Path(path);digest=hashlib.sha256(path.read_bytes()).hexdigest()
 if digest!=BOOTSTRAP_SHA:raise ValueError('separate normal86 RSL witness source SHA differs')
 source=torch.load(path,map_location='cpu',weights_only=False)
 row=verify_loaded_policy_only_fresh_environment(runner,env,source)
 del source
 # Original equality/freshness assertions above remain unchanged. Correct only
 # the receipt's old native-fresh label; no native model exists at this stage.
 row.update(epoch=time.time(),source_SHA=digest,source_Adam=BOOTSTRAP_ADAM,
  native_architecture_and_optimizers_fresh=False,native_fullstate_restore_pending=True,
  native_state_restore_has_not_run_yet=True,
  source_role='frozen_normal86_RSL_core_witness_only_before_native_R5_restore',
  old700N_native_environment_state_not_restored=True,
  configured_nominal400_parameter_actual_GPU_readback_pending=True)
 out=Path(log_dir)/'NATIVE88_FROZEN_RSL_ONLY_FRESH_PHYSICAL_EPISODE_BOOTSTRAP_ACTUAL.json'
 with out.open('x',encoding='utf8') as f:json.dump(row,f,indent=2,allow_nan=False)
 return row
