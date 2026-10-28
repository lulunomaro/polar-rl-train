"""Preserve fetched original text and extract reviewed Torch-only reward definitions; no imports from upstream project."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def main():
 dest=B/'pinned_exact';assert not dest.exists();dest.mkdir();rows=[];by_path={}
 for p in sorted((B/'source_receipts').glob('*.json')):
  v=json.loads(p.read_bytes());raw=v['content'].encode('utf8');blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==v['sha'],p
  path=v['display_url'].split('/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/',1)[1];target=dest/path;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write(raw)
  rows.append(dict(path=path,local_path=str(target),bytes=len(raw),SHA=digest(raw),Git_blob_SHA=blob,source_url=v['display_url'],commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c'));by_path[path]=raw.decode('utf8')
 profiles={'jump':'jump/wheel_legged_gym/envs/base/legged_robot_config.py','stair':'plane/logs/wheel_legged/上台阶3_angz+/legged_robot_config.py'};result={};oracles=[]
 for name,path in profiles.items():
  tree=ast.parse(by_path[path]);cfg=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobotCfg');rewards=next(x for x in cfg.body if isinstance(x,ast.ClassDef) and x.name=='rewards');scales=next(x for x in rewards.body if isinstance(x,ast.ClassDef) and x.name=='scales');weights={a.targets[0].id:ast.literal_eval(a.value) for a in scales.body if isinstance(a,ast.Assign)}
  root=path.rsplit('/',1)[0];robot=root+'/legged_robot.py';source=by_path[robot];klass=next(x for x in ast.parse(source).body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobot');fn={x.name:x for x in klass.body if isinstance(x,ast.FunctionDef)}
  missing=[k for k,w in weights.items() if w and '_reward_'+k not in fn];assert not missing,missing
  selected={k:ast.get_source_segment(source,fn['_reward_'+k]) for k,w in weights.items() if w};result[name]=dict(config_path=path,robot_path=robot,enabled_weights=weights,enabled_functions=list(selected),clip_single_reward=next(ast.literal_eval(a.value) for a in rewards.body if isinstance(a,ast.Assign) and a.targets[0].id=='clip_single_reward'))
  header=source[:source.index('import ')];body=header+'\nimport torch\n\nclass Upstream'+name.title()+'RewardOracle:\n'
  for key,code in selected.items():body+='\n'+'\n'.join('    '+line for line in code.splitlines())+'\n'
  ast.parse(body);oracle=B/('upstream_'+name+'_enabled_reward_oracle.py')
  with oracle.open('x',encoding='utf8') as f:f.write(body)
  oracles.append(dict(path=str(oracle),SHA=digest(oracle.read_bytes()),only_selected_reviewed_reward_functions=True,no_upstream_project_import_or_execution=True))
 put('PINNED_UPSTREAM_EXACT_TEXT_AND_ENABLED_REWARD_AUDIT_ACTUAL.json',dict(epoch=time.time(),pinned_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',latest_commit_date_UTC='2026-08-22T05:23:25Z',latest_commit_did_not_modify_reward_functions=True,exact_texts=rows,enabled=result,oracles=oracles,first_display_copies_extra_terminal_newline_retained=True,source_api_JSON_preserves_exact_original_UTF8=True,source_only_no_GPU_SDK_model_or_training=True))
 print(json.dumps(dict(exact_texts=len(rows),enabled_profiles=result,oracles=len(oracles),source_only=True),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:put('UPSTREAM_TEXT_OR_REWARD_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_upstream_code_executed=True));raise
