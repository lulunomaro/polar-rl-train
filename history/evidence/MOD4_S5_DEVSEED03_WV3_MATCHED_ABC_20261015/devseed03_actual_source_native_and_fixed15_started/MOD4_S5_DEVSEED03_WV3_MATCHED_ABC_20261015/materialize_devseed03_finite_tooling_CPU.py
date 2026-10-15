"""Materialize fresh once identities; do not import or execute old once helpers."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_S4_FIRST_GATE_RETENTION_PAIR_20261015';A=W/'MOD4_S5_SINGLE_W35_RETENTION_A_20261015'
def write(n,s):
 p=D/n;assert not p.exists();ast.parse(s,filename=str(p));p.write_text(s,encoding='utf8')
def main():
 s=(OLD/'transport_s4_retention_pair_actual.py').read_text(encoding='utf8').replace(OLD.name,D.name);write('transport_devseed03_ABC_actual.py',s)
 s=(OLD/'upload_first_gate_retention_pair_target_CPU_once.py').read_text(encoding='utf8').replace('transport_s4_retention_pair_actual','transport_devseed03_ABC_actual').replace('FIRST_GATE_RETENTION_PAIR_CPU_PREPARED_ACTUAL','DEVSEED03_ABC_CPU_PREPARED_ACTUAL').replace('FIRST_GATE_RETENTION_PAIR_UPLOAD','DEVSEED03_ABC_UPLOAD')
 before="walk(source);assert len(tensors)==194 and sum(v.is_floating_point() for v in tensors)==113 and not torch.cuda.is_initialized()"
 after="""walk(source);assert len(tensors)==194 and sum(v.is_floating_point() for v in tensors)==113 and not torch.cuda.is_initialized()
for ref,expected in zip(pair['sources'],(94,102)):
 assert H(ref['local_path'])==ref['sha256'];tensors.clear();walk(torch.load(ref['local_path'],map_location='cpu',weights_only=False));assert sum(v.is_floating_point() for v in tensors)==expected
from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone();single=Single35(pair['sources'][1]['local_path'],88,'cpu');assert single.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
"""
 assert before in s;s=s.replace(before,after);write('upload_devseed03_ABC_target_CPU_once.py',s)
 s=(OLD/'dispatch_first_gate_retention_new_case_actual.py').read_text(encoding='utf8').replace('transport_s4_retention_pair_actual','transport_devseed03_ABC_actual').replace(OLD.name,D.name).replace('20261002','20261003').replace('s4_retention_{a.mode}','s5_dev03_{a.mode}').replace('MOD4_S4_RetentionPair_20261015_','MOD4_S5_DevSeed03ABC_20261015_').replace("choices=('rule_eval','gate_eval')","choices=('single_eval','rule_eval','gate_eval')").replace('FIRST_GATE_RETENTION_PAIR_CPU_PREPARED_ACTUAL','DEVSEED03_ABC_CPU_PREPARED_ACTUAL').replace('FIRST_GATE_RETENTION_PAIR_UPLOAD_TARGET_CPU_ACTUAL','DEVSEED03_ABC_UPLOAD_TARGET_CPU_ACTUAL')
 before="assert routing['passed'] and routing['steps']==120 and routing['kind']==a.kind and routing['all24_initial_final_source_exact']"
 after="assert routing['passed'];assert (routing['controls']==120 and routing['source9_STD_initial_final_exact']) if a.mode=='single_eval' else (routing['steps']==120 and routing['kind']==a.kind and routing['all24_initial_final_source_exact'])"
 assert before in s;s=s.replace(before,after);write('dispatch_devseed03_ABC_new_case_actual.py',s)
 s=(A/'collect_s5_single_A_actual_boundary.py').read_text(encoding='utf8').replace('transport_s5_single_retention_A_actual','transport_devseed03_ABC_actual');write('collect_devseed03_ABC_actual_boundary.py',s)
 s=(A/'review_s5_single_A_original_physical_and_metrics_CPU.py').read_text(encoding='utf8').replace('20261002','20261003').replace('S5_SINGLE_W35_A_ORIGINAL_V8_COMPLETE_DATA_AND_MATCHED_OLD_B_C_PAIR_CPU_REVIEW','S5_DEVSEED03_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW');write('review_devseed03_original_physical_and_metrics_CPU.py',s)
 s=(A/'review_s5_single_A_actual_source_history_CPU.py').read_text(encoding='utf8').replace("f's5_single_W35_{k}_{n}_v1'","f's5_dev03_single_eval_{k}_{n}_v1'");write('review_devseed03_single_source_history_CPU.py',s)
 s=(OLD/'review_s4_retention_pair_routing_CPU.py').read_text(encoding='utf8');write('review_devseed03_pair_routing_CPU.py',s)
 # Reuse only pure bounded readback mechanics; no old entry point is invoked.
 src=(A/'run_s5_single_A_fixed_six_case_batch_once.py').read_text(encoding='utf8');start=src.index('def wait_closed(case):');end=src.index('\ndef consume(',start);waitfn=src[start:end]
 header='''"""Fixed 15 new development-seed cases; frozen only, exclusive finite transport."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';PY=sys.executable;CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
import transport_devseed03_ABC_actual as t
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v,unique=False):
 p=R/n
 if unique:assert not p.exists()
 q=p.with_name(p.name+'.partial');q.write_text(json.dumps(v,indent=2),encoding='utf8');os.replace(q,p)
def run(argv):
 p=subprocess.run(argv,cwd=D,capture_output=True,text=True,encoding='utf8',errors='replace');put('FINITE15_COMMAND_'+str(time.time_ns())+'.json',dict(argv=argv,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),True);assert p.returncode==0,argv
'''
 tail='''
def consume(mode,kind,steps,native=None):
 case=f's5_dev03_{mode}_{kind}_{steps}_v1';put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='dispatch_own_unused',case=case))
 argv=[PY,'-X','utf8',str(D/'dispatch_devseed03_ABC_new_case_actual.py'),'--execute-root-dispatch','--kind',kind,'--steps',str(steps),'--source','pair_anchor','--mode',mode]
 if steps==1500:argv+=['--native-proof',native['data'],'--routing-proof',native['routing']]
 run(argv);put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='bounded_wait_own_scope_exclusive_transport',case=case));wait_closed(case)
 run([PY,'-X','utf8',str(D/'collect_devseed03_ABC_actual_boundary.py'),'--case',case,'--execute-root-readonly-collection'])
 c=json.loads(sorted(R.glob(case+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes());assert c['outputs']['COMPLETE_ACTUAL.json'] and c['shared_OS_lock_free']
 attempt=Path(next(x['local_path'] for x in c['collected_files'] if x['relative']=='attempts/'+case+'/PARENT_EXIT_RECEIPT.json')).parent;boundary=R/(case+'_INDEPENDENT_BOUNDARY.json');data=R/(case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json')
 run([CPU,'-X','utf8',str(D/'review_devseed03_original_physical_and_metrics_CPU.py'),'--attempt',str(attempt),'--boundary',str(boundary),'--output',str(data)])
 reader='review_devseed03_single_source_history_CPU.py' if mode=='single_eval' else 'review_devseed03_pair_routing_CPU.py';run([CPU,'-X','utf8',str(D/reader),'--case',case]);routing=R/(case+('_S5_SINGLE_CONTROL_CPU_ADMITTED.json' if mode=='single_eval' else '_S4_ROUTING_CPU_ADMITTED.json'))
 return dict(case=case,mode=mode,kind=kind,steps=steps,attempt=str(attempt),boundary=str(boundary),data=str(data),routing=str(routing))
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute-root-fixed15-new-devseed-cases',action='store_true');a=p.parse_args();assert a.execute_root_fixed15_new_devseed_cases
 assert json.loads((R/'DEVSEED03_ABC_UPLOAD_TARGET_CPU_ACTUAL.json').read_bytes())['actual_targetCPU'] and not (R/'DEVSEED03_ABC_FIXED15_STARTED.json').exists()
 ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
 put('DEVSEED03_ABC_FIXED15_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM=json.loads(ci.stdout),argv=sys.argv,scriptSHA=H(__file__),seed=20261003,profile='white_v3',plan='perkind single native120+full1500, gate native120, rulefull1500+gatefull1500, actual3way initialpairs; 15newcases total',sole_sequential210_249_transport_owner_while_actual_alive=True,no_PPO_budget_or_oldcase_replay=True),True)
 completed=[];pairs=[]
 for kind in ('flat','spin','world'):
  an=consume('single_eval',kind,120);completed.append(an);single=consume('single_eval',kind,1500,an);completed.append(single)
  cn=consume('gate_eval',kind,120);completed.append(cn);rule=consume('rule_eval',kind,1500,cn);completed.append(rule);gate=consume('gate_eval',kind,1500,cn);completed.append(gate)
  for name,cand,base in [('A_VS_B',single,rule),('C_VS_B',gate,rule),('A_VS_C',single,gate)]:
   out=R/(kind+'_'+name+'_COMPLETE_ORIGINAL_PAIR_CPU_REVIEW.json');run([CPU,'-X','utf8',str(D/'review_devseed03_original_physical_and_metrics_CPU.py'),'--attempt',cand['attempt'],'--boundary',cand['boundary'],'--baseline-attempt',base['attempt'],'--baseline-boundary',base['boundary'],'--output',str(out)]);pairs.append(dict(kind=kind,pair=name,path=str(out),sha256=H(out)))
  put('DEVSEED03_ABC_FIXED15_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='kind_complete_3way_initialpairs_CPU',completed=completed,pairs=pairs))
 put('DEVSEED03_ABC_FIXED15_COMPLETE.json',dict(epoch=time.time(),pid=os.getpid(),completed=completed,pairs=pairs,all15_closed_and_CPU_admitted=True,actual_three_initial_pairs_per_kind=True,no_extra_case_learning_or_budget=True,handoff_requires_actual_local_CIM_absence=True),True)
if __name__=='__main__':
 try:main()
 except BaseException:put('DEVSEED03_ABC_FIXED15_ORIGINAL_ERROR.json',dict(epoch=time.time(),pid=os.getpid(),error=traceback.format_exc(),no_retry_replay_signal_or_GPU_restart=True),True);raise
'''
 write('run_devseed03_ABC_fixed15_case_batch_once.py',header+waitfn+tail)
 s=(A/'launch_s5_single_A_fixed_six_hidden_once.py').read_text(encoding='utf8').replace('S5_SINGLE_A_UPLOAD_TARGET_CPU_ACTUAL','DEVSEED03_ABC_UPLOAD_TARGET_CPU_ACTUAL').replace('S5_SINGLE_A_FIXED_SIX_ROOT_DISPATCH','DEVSEED03_ABC_FIXED15_ROOT_DISPATCH').replace('run_s5_single_A_fixed_six_case_batch_once.py','run_devseed03_ABC_fixed15_case_batch_once.py').replace('--execute-root-six-new-A-cases','--execute-root-fixed15-new-devseed-cases').replace('FINITE_SIX','FINITE15').replace('fixed_native3_full3_only=True','fixed_native6_full9_only=True').replace('started_finite6','started_finite15').replace('new_finite6','new_finite15');write('launch_devseed03_ABC_fixed15_hidden_once.py',s)
 for p in D.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
 out=D/'reports/DEVSEED03_FIXED15_TOOLING_CPU_MATERIALIZED.json';assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),CPU_only_no_remote_GPU=True,fixed_new_cases15=True,physical_reader_only_declared_seed_changed=True,single_and_pair_source_CPU_readers_original_numeric_checks_unchanged=True,new_once_paths_not_consumed=True),indent=2),encoding='utf8')
 print(json.dumps(dict(materialized=True,no_remote_or_GPU=True)))
if __name__=='__main__':main()
