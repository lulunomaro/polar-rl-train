"""Explicit user closure2mm->10mm and mimic.01 before Mod4Env construction."""
from pathlib import Path
import json,time

def project(value,path,unknown):
 if value is None or isinstance(value,(str,bool,int,float)):return value
 if isinstance(value,dict):return {str(k):project(v,path+'.'+str(k),unknown) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [project(v,path+'.'+str(i),unknown) for i,v in enumerate(value)]
 if isinstance(value,slice):return dict(slice=[value.start,value.stop,value.step])
 if callable(value):return dict(callable_module=getattr(value,'__module__',None),callable_name=getattr(value,'__qualname__',None))
 if hasattr(value,'__dict__'):
  return dict(type=type(value).__module__+'.'+type(value).__qualname__,fields={k:project(v,path+'.'+k,unknown) for k,v in vars(value).items() if not k.startswith('__')})
 unknown.append(path);return dict(unsupported_type=type(value).__module__+'.'+type(value).__qualname__)

def term_projection(cfg):
 unknown=[];out={}
 for name,term in vars(cfg.terminations).items():
  if name.startswith('_'):continue
  if term is None:out[name]=None;continue
  if hasattr(term,'params'):
   out[name]=dict(params=project(term.params,name+'.params',unknown),func=project(getattr(term,'func',None),name+'.func',unknown),time_out=getattr(term,'time_out',None))
 return out,unknown

def enforce_before_constructor(cfg,receipt_path):
 before,unknown_before=term_projection(cfg)
 assert cfg.terminations.closure.params['threshold']==.002,'Expected original frozen2mm before new user10mm override'
 assert cfg.terminations.mimic.params['threshold']==.05,'Expected original W35 authored mimic.05 before planned.01'
 cfg.terminations.closure.params['threshold']=.01
 cfg.terminations.mimic.params['threshold']=.01
 after,unknown_after=term_projection(cfg)
 expected=json.loads(json.dumps(before));expected['mimic']['params']['threshold']=.01;expected['closure']['params']['threshold']=.01
 assert after==expected and unknown_before==unknown_after,'Only user closure10mm and planned mimic01 may differ'
 row=dict(epoch=time.time(),kind='W35_LATEST32481_USER_CLOSURE10MM_MIMIC01_BEFORE_ENV_CONSTRUCTOR',passed=True,
  original_mimic_radians=.05,planned_effective_mimic_radians=.01,previous_closure_m=.002,closure_m=.01,user_authorized_closure10mm=True,
  explicit_termination_threshold_change_entity_constraints_and_solver_unchanged=True,constructor_not_yet_called=True,
  before_termination_projection=before,after_termination_projection=after,
  all_other_termination_params_unchanged_in_JSON_supported_projection=True,
  all_other_termination_params_unchanged=(not unknown_before),unsupported_projection_paths=unknown_before,
  assignments=['cfg.terminations.closure.params.threshold=.01','cfg.terminations.mimic.params.threshold=.01'],reward_commands_motors_unchanged=True)
 with Path(receipt_path).open('x',encoding='utf8') as f:json.dump(row,f,indent=2,allow_nan=False)
 return row



def install_before_main(namespace,receipt_path):
 build=namespace['build_env'];glob=build.__globals__;old=glob['configure_intro']
 assert old.__module__=='config214_training' and old.__name__=='configure208'
 def configured(cfg):
  recipe=old(cfg)
  enforce_before_constructor(cfg,receipt_path)
  return recipe
 glob['configure_intro']=configured
 def uninstall():glob['configure_intro']=old
 return uninstall
