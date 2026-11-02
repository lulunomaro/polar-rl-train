"""Explicit frozenvariant fullstate wrapper; original lowerhelper ONEreset retained."""
from pathlib import Path
import copy,importlib,json
from e1_pinned_source_v1 import cached_load,cached_H,cached_source_owns
from variant_extra_state_runtime_v1 import restore_extra_before_original_reset,finish_extra_after_original_reset,merge_extra_into_own_save

def metadata():return json.loads((Path(__file__).resolve().parents[3]/'VARIANT_SOURCE_METADATA.json').read_bytes())
def resume_e1_new_episode(runner,env,path,log_dir):
 import torch
 from spring_pressure_checkpoint import exact
 meta=metadata();ck=cached_load(path,map_location='cpu',weights_only=False,purpose='variant.OWN_complete_extra_state_BEFORE_original_one_reset')
 before=restore_extra_before_original_reset(env,ck,variant=meta['variant'],torch_module=torch)
 original=importlib.import_module(meta['original_helper']);row=original.resume_e1_new_episode(runner,env,path,log_dir)
 after=finish_extra_after_original_reset(env,ck,variant=meta['variant'],torch_module=torch,exact=exact)
 report=dict(source_SHA=cached_H(path,purpose='variant.OWN_extra_identity'),variant=meta['variant'],before_original_reset=before,after_original_reset=after,all_complete_saved_extras_exact=True,original_lower_helper=meta['original_helper'],extra_reset_physics_RNG_calls=0,unknown_root_fields_retained_in_future_cache=True,not_actual_skill_or_birthinertia_gate=True)
 Path(log_dir,'VARIANT_EXTRA_FULLSTATE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(report,indent=2));return row

def install_e1_save_contract(runner,env):
 import torch
 meta=metadata();original=importlib.import_module(meta['original_helper']);original.install_e1_save_contract(runner,env);old=runner.save
 def save(path,*args,**kwargs):
  if cached_source_owns(path):raise ValueError('Frozen selectedsource cannot be outputpath')
  old(path,*args,**kwargs);complete=cached_load(path,map_location='cpu',weights_only=False,purpose='variant.OWN_new_save_real_disk_roundtrip');merged=merge_extra_into_own_save(complete,env,variant=meta['variant']);torch.save(merged,path)
 runner.save=save
