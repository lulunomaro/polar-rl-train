from pathlib import Path
from urllib.parse import unquote
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 sources={};rows=[]
 for p in sorted((B/'source_receipts').glob('*.json')):
  v=json.loads(p.read_bytes());raw=v['content'].encode();path=unquote(v['display_url'].split('/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/',1)[1]);local=B/'pinned_exact_v2'/path
  assert local.read_bytes()==raw and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==v['sha']
  rows.append(dict(path=path,local_path=str(local),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),Git_blob_SHA=v['sha'],source_url=v['display_url']));sources[path]=raw.decode()
 result={};oracles=[]
 for name,path in [('jump','jump/wheel_legged_gym/envs/base/legged_robot_config.py'),('stair','plane/logs/wheel_legged/上台阶3_angz+/legged_robot_config.py')]:
  cfg=next(x for x in ast.parse(sources[path]).body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobotCfg');reward=next(x for x in cfg.body if isinstance(x,ast.ClassDef) and x.name=='rewards');scales=next(x for x in reward.body if isinstance(x,ast.ClassDef) and x.name=='scales');weights={a.targets[0].id:ast.literal_eval(a.value) for a in scales.body if isinstance(a,ast.Assign)}
  robot=path.rsplit('/',1)[0]+'/legged_robot.py';text=sources[robot];tree=ast.parse(text);klass=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='LeggedRobot');functions={x.name:x for x in klass.body if isinstance(x,ast.FunctionDef)}
  header='\n'.join(text.splitlines()[:tree.body[0].lineno-1])+'\n';body=header+'\nimport torch\n\nclass Upstream'+name.title()+'RewardOracleV3:\n'
  for key,weight in weights.items():
   if not weight:continue
   function=functions['_reward_'+key];body+='\n'+'\n'.join('    '+line for line in ast.get_source_segment(text,function).splitlines())+'\n'
  ast.parse(body);target=B/('upstream_'+name+'_enabled_reward_oracle_v3.py')
  with target.open('x',encoding='utf8') as f:f.write(body)
  result[name]=dict(config_path=path,robot_path=robot,enabled_weights=weights,clip_single_reward=next(ast.literal_eval(a.value) for a in reward.body if isinstance(a,ast.Assign) and a.targets[0].id=='clip_single_reward'))
  oracles.append(dict(path=str(target),SHA=hashlib.sha256(target.read_bytes()).hexdigest(),no_project_import_or_execution=True))
 put('PINNED_UPSTREAM_EXACT_TEXT_AND_ENABLED_REWARD_AUDIT_V3_ACTUAL.json',dict(epoch=time.time(),pinned_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',exact_texts=rows,enabled=result,oracles=oracles,URI_failure_and_header_AST_failure_retained=True,exact_v2_files_reused_not_overwritten=True,no_model_GPU_SDK_or_network=True));print(json.dumps(dict(enabled=result,exact_texts=len(rows),oracles=len(oracles)),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:put('EXACT_TEXT_ORACLE_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_upstream_execution=True));raise
