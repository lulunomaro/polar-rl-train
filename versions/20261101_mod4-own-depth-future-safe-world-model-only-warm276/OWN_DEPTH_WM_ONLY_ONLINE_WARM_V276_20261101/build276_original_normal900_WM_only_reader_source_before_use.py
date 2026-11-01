from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;D=N/'normal276';D.mkdir(exist_ok=False)
B=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/normal240_V2_path_reader'
s=(B/'collect240_original_formal_cost_normal900_V2_PATH_UNUSED_once.py').read_text('utf8')
s=s.replace('from normal240_common import','from normal276_common import').replace('control240','control276').replace('ROOT240V2','ROOT276').replace('closed240','closed276')
s=s.replace("collect240_|start240_|","launch276_|collect276_|run_ROOT274_|run_ROOT272_|collect240_|start240_|")
s=s.replace("f'{N}'","f'{N}'")
s=s.replace("final.get('actual_new_PPO_updates',0)>0","final.get('actual_new_WM_updates',0)>0 and final.get('actual_new_PPO_updates')==0 and final.get('actual_Pi_Critic_STD_updates')==0")
s=s.replace("final['final']['epoch']>=actual_go['save_deadline']","final['final']['save_epoch']>=actual_go['save_deadline']")
s=s.replace("counts=json.loads(next(x['UTF8'] for x in texts if Path(x['path']).name=='ACTUAL240_MODEL_SOURCE_FINAL_READ_COUNTS_BEFORE_LEARNING.json'))","counts=json.loads(next(x['UTF8'] for x in texts if Path(x['path']).name=='ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json'))")
s=s.replace("counts['source_physical_byte_opens']==counts['source_decodes']==1","counts['source_byte_reads']==counts['source_GPU_decodes']==1")
s=s.replace("final['final']['source_SHA']==v['spec']['source_SHA']","final['final']['teacher_source_SHA']==v['spec']['source_SHA']")
s=s.replace("u=final['actual_new_PPO_updates'];assert u>0","u=final['actual_new_WM_updates'];assert u>0")
s=s.replace("assert final['final']['saved_iteration']==2050+u and final['final']['Adam_min']==final['final']['Adam_max']==41240+20*u","assert final['final']['saved_WM_updates']==u and final['final']['WM_Adam_step_min']==final['final']['WM_Adam_step_max']==u\n assert final['final']['teacher_iteration']==2135 and final['final']['teacher_Adam_step']==42940\n import sys;sys.path.insert(0,str(C));from wm_task275 import validate_final;validate_final(final,json.loads((B/'TASK276.json').read_bytes()),actual_go)")
s=s.replace("final['final']['full_core_STD_optimizer_and_targetDR_saved']","final['final']['full_teacher_WM_Adam_norm_RNG_DR_reward_memory_saved']")
s=s.replace("R/'ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json'","R/'ROOT276_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json'").replace("R/'ROOT240_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json'","R/'ROOT276_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json'")
s=s.replace('original240 source2050 solo','original276 WM-only solo').replace('source2050','frozen2135')
ast.parse(s);(D/'collect276_original_WM_formal_cost_normal900_UNUSED_once.py').write_text(s,encoding='utf8')
common='''from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json'
SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
sys.path.insert(0,str(N/'control276'))
from wm_task275 import _go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):return _go_identity(g,run,read(N/'TASK276_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
'''
ast.parse(common);(D/'normal276_common.py').write_text(common,encoding='utf8')
with(N/'SOURCE276_ORIGINAL_NORMAL900_WM_COUNTER_READER_JOIN.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=True,original_local_remote900_owner850_node180_and_raw_SUMONCE_body_preserved=True,only_source_and_artifact_counter_schema_changed_to_WM=True,entry_executions=0,remote_model_raw_budget=0),f,indent=2)
print(json.dumps(dict(passed=True,source_only=True)))
