from pathlib import Path
import ast,hashlib,json,runpy,time,traceback,sys
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(value)+'\n'+''.join(lines[x.end_lineno:])
def main():
 prep=read(R/'TWO106_COHERENT_20S_PAYLOADS_PREPARED_ACTUAL.json')
 for mode,spec in prep['payloads'].items():
  B=Path(spec['payload']);p=B/'source/fresh_policy_only_bootstrap87_v1.py';old=p.read_text('utf8');new=rep(old,'float(env.cfg.episode_length_s)!=5.','float(env.cfg.episode_length_s)!=20.').replace('explicit five-second practice episodes required','explicit user20second practice episodes required');write(p,new)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c['explicit_user20s_protected_source_delta'].append(dict(relative=p.relative_to(B).as_posix(),old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(p),authorized_delta='same whole frozenRSL/freshness assertions, expected20s only'))
  for rel in c['small_evidence_pins']:
   if (B/rel).is_file():c['small_evidence_pins'][rel]=H(B/rel)
  if p.relative_to(B).as_posix() in c['protected_current88C_files']:c['protected_current88C_files'][p.relative_to(B).as_posix()]=H(p)
  c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
  task=spec['task'];task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2));m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  for row in m['files']:
   p=B/row['relative']
   if p.suffix.lower() not in ('.pt','.pth','.npz','.usd','.usdc','.zip'):row.update(bytes=p.stat().st_size,SHA=H(p))
  write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2));spec.update(manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
 put(R/'TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json',prep)
 # New exact finite installer. Reuse the original full SDK/model CPU waiter,
 # never its old once/main. The remote source copy is the closed104 actual root.
 old=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/install_two103_bank_reader_repaired_CPU_only_v3_once.py';s=old.read_text('utf8')
 pre=next(ast.literal_eval(x.value) for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in x.targets))
 pre=pre.replace('MOD4_H1_FLAT20_NATIVE_2610v101/seed27','MOD4_H1_FUDAN270_BANK_READER_2610v103CPUv3/seed27').replace('MOD4_TWO101_PRODUCER_FIXED_FLAT20_2610v101','MOD4_TWO104_FUDAN270_LIGHT_2610v104')
 pre=pre.replace('611142','622439').replace('1793191826.62','1793203678.15').replace('7225.441126346588','7222.6497621536255').replace('3612.8719108104706','3611.5380840301514').replace('3612.5692155361176','3611.111678123474').replace('(611158,1793191827.27),(611178,1793191827.91)','(622455,1793203678.84),(622473,1793203679.49)')
 ast.parse(pre);s=assign(s,'PRE',pre)
 s=s.replace('TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json','TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json')
 s=rep(s," assert json.loads((R/'TWO103_TYPED_SOURCE_AND_SIGNED_GO_NEGATIVE_CPU_ACTUAL.json').read_bytes())['passed_source_CPU_only']"," assert json.loads((R/'SOURCE106_COHERENT20S_CLOCK_AND_INVERSE_DELTAS_CPU_ACTUAL.json').read_bytes())['passed']")
 s=s.replace('TWO103','TWO106').replace('NATIVE103','NATIVE106');ast.parse(s);write(N/'install_TWO106_new20s_source_SDK_fullstate_CPU_UNUSED_once.py',s)
 put(R/'TWO106_SOURCE_PREINSTALL_REVIEW_ACTUAL.json',dict(passed_source_only=True,epoch=time.time(),remaining5s_bootstrap_guard_caught_and_changed_before_install=True,old_runtime_solver_reset_PD_action_reward_acceptance_unchanged=True,prior_original_preparer_KeyError_preserved=True,additional_local_source_lookup_errors=['original guessed h1_public_phase_runtime.py absent; actual h1_public_request_phase_v1.py read','original guessed h1_goal_state_machine.py absent; actual phase state was read'],fullstate_CPU_and_GO_pending=True,installer_SHA=H(N/'install_TWO106_new20s_source_SDK_fullstate_CPU_UNUSED_once.py')))
 print(json.dumps(dict(sealed_source=True,remote_install_unused=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('SEAL106_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote=True));raise
