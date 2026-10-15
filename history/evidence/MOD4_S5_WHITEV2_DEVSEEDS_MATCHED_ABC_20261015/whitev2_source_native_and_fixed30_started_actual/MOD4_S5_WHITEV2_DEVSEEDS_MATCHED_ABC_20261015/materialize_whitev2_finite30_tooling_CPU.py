"""Fresh source-bound profile scopes. Never invokes old entry points."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;W=D.parent;P=W/'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015'
def write(n,s):
 p=D/n;assert not p.exists();ast.parse(s,filename=str(p));p.write_text(s,encoding='utf8')
def convert(s):return s.replace(P.name,D.name).replace('transport_devseed03_ABC_actual','transport_whitev2_ABC_actual').replace('DEVSEED03_ABC','WHITEV2_ABC').replace('DEVSEED03_FIXED15','WHITEV2_FIXED30')
def main():
 write('transport_whitev2_ABC_actual.py',convert((P/'transport_devseed03_ABC_actual.py').read_text(encoding='utf8')))
 s=convert((P/'upload_devseed03_ABC_target_CPU_once.py').read_text(encoding='utf8'));s=s.replace("m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());assert", "m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());assert m['DR_profile']=='white_v2' and m['declared_development_seeds']==[20261002,20261003];assert");write('upload_whitev2_ABC_target_CPU_once.py',s)
 s=convert((P/'dispatch_devseed03_ABC_new_case_actual.py').read_text(encoding='utf8'));s=s.replace("p=argparse.ArgumentParser();p.add_argument('--kind'", "p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True,choices=(20261002,20261003));p.add_argument('--kind'")
 s=s.replace("s5_dev03_{a.mode}","s5_wv2_s{a.seed}_{a.mode}").replace('MOD4_S5_DevSeed03ABC_20261015_','MOD4_S5_WhiteV2ABC_20261015_').replace('seed=20261003,headless','seed=a.seed,headless')
 before="v=proof['result'];assert v['kind']==a.kind";after="v=proof['result'];assert v['seed']==a.seed and v['profile']=='white_v2';assert v['kind']==a.kind";assert before in s;s=s.replace(before,after);write('dispatch_whitev2_ABC_new_case_actual.py',s)
 write('collect_whitev2_ABC_actual_boundary.py',convert((P/'collect_devseed03_ABC_actual_boundary.py').read_text(encoding='utf8')))
 s=(P/'review_devseed03_original_physical_and_metrics_CPU.py').read_text(encoding='utf8');s=s.replace("assert p['seed']==20261003 and p['steps']==S", "assert p['seed'] in (20261002,20261003) and p['steps']==S\n assert p['native_readonly_witness']['DR_profile']=='white_v2'\n if kind=='flat':\n  assert p['mild_initial_parameters']['profile']==p['mild_final_parameters']['profile']=='white_v2'\n else:\n  assert p['profile']==p['initial_parameter_audit']['profile']==p['final_parameter_audit']['profile']=='white_v2'")
 s=s.replace('out=dict(kind=kind,num_envs=N,',"out=dict(seed=p['seed'],profile='white_v2',kind=kind,num_envs=N,")
 s=s.replace("assert baseline['kind']==result['kind'] and baseline['steps']==result['steps']", "assert baseline['kind']==result['kind'] and baseline['steps']==result['steps'] and baseline['seed']==result['seed'] and baseline['profile']==result['profile']=='white_v2'")
 s=s.replace('S5_DEVSEED03_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW','S5_WHITEV2_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW');write('review_whitev2_original_physical_and_metrics_CPU.py',s)
 s=(P/'review_devseed03_single_source_history_CPU.py').read_text(encoding='utf8');s=s.replace("tuple(f's5_dev03_single_eval_{k}_{n}_v1' for k in ('flat','spin','world') for n in (120,1500))", "tuple(f's5_wv2_s{seed}_single_eval_{k}_{n}_v1' for seed in (20261002,20261003) for k in ('flat','spin','world') for n in (120,1500))");write('review_whitev2_single_source_history_CPU.py',s)
 write('review_whitev2_pair_routing_CPU.py',(P/'review_devseed03_pair_routing_CPU.py').read_text(encoding='utf8'))
 s=convert((P/'run_devseed03_ABC_fixed15_case_batch_once.py').read_text(encoding='utf8'));s=s.replace('DEVSEED03','WHITEV2').replace('FIXED15','FIXED30').replace('FINITE15','FINITE30').replace('fixed15','fixed30').replace('execute_root_fixed15','execute_root_fixed30').replace('devseed03','whitev2').replace('devseed','whitev2').replace('seed=20261003,profile=\'white_v3\'',"seeds=[20261002,20261003],profile='white_v2'").replace('Fixed 15 new development-seed cases','Fixed 30 new white_v2 development-seed cases')
 s=s.replace('def consume(mode,kind,steps,native=None):','def consume(seed,mode,kind,steps,native=None):').replace("case=f's5_dev03_{mode}_{kind}_{steps}_v1'", "case=f's5_wv2_s{seed}_{mode}_{kind}_{steps}_v1'")
 s=s.replace("'--execute-root-dispatch','--kind',kind", "'--execute-root-dispatch','--seed',str(seed),'--kind',kind")
 begin=s.index(' completed=[];pairs=[]\n');end=s.index(" put('WHITEV2_ABC_FIXED30_COMPLETE.json'",begin)
 block=''' completed=[];pairs=[]
 for seed in (20261002,20261003):
  for kind in ('flat','spin','world'):
   an=consume(seed,'single_eval',kind,120);completed.append(an);single=consume(seed,'single_eval',kind,1500,an);completed.append(single)
   cn=consume(seed,'gate_eval',kind,120);completed.append(cn);rule=consume(seed,'rule_eval',kind,1500,cn);completed.append(rule);gate=consume(seed,'gate_eval',kind,1500,cn);completed.append(gate)
   for name,cand,base in [('A_VS_B',single,rule),('C_VS_B',gate,rule),('A_VS_C',single,gate)]:
    out=R/(str(seed)+'_'+kind+'_'+name+'_COMPLETE_ORIGINAL_PAIR_CPU_REVIEW.json');run([CPU,'-X','utf8',str(D/'review_whitev2_original_physical_and_metrics_CPU.py'),'--attempt',cand['attempt'],'--boundary',cand['boundary'],'--baseline-attempt',base['attempt'],'--baseline-boundary',base['boundary'],'--output',str(out)]);pairs.append(dict(seed=seed,kind=kind,pair=name,path=str(out),sha256=H(out)))
   put('WHITEV2_ABC_FIXED30_CURRENT.json',dict(epoch=time.time(),pid=os.getpid(),phase='seed_kind_complete_3way_initialpairs_CPU',completed=completed,pairs=pairs))
'''
 s=s[:begin]+block+s[end:];s=s.replace('all15_closed_and_CPU_admitted=True','all30_closed_and_CPU_admitted=True').replace('return dict(case=case,mode=mode,kind=kind,steps=steps,',"return dict(case=case,seed=seed,profile='white_v2',mode=mode,kind=kind,steps=steps,")
 s=s.replace('15newcases total','30newcases total').replace('no_PPO_budget_or_oldcase_replay=True','no_PPO_budget_or_oldcase_replay=True,nominal_not_dispatched=True');write('run_whitev2_ABC_fixed30_case_batch_once.py',s)
 s=convert((P/'launch_devseed03_ABC_fixed15_hidden_once.py').read_text(encoding='utf8')).replace('DEVSEED03','WHITEV2').replace('FIXED15','FIXED30').replace('FINITE15','FINITE30').replace('fixed15','fixed30').replace('devseed03','whitev2').replace('devseed','whitev2').replace('fixed_native6_full9_only=True','fixed_native12_full18_only=True').replace('started_finite15','started_finite30').replace('new_finite15','new_finite30');write('launch_whitev2_ABC_fixed30_hidden_once.py',s)
 for p in D.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
 out=D/'reports/WHITEV2_FIXED30_TOOLING_CPU_MATERIALIZED.json';assert not out.exists();out.write_text(json.dumps(dict(epoch=time.time(),CPU_only_no_GPU_transport=True,fixed30_new_scopes=True,seed_profile_native_full_admission_binding_added=True,all_numeric_contracts_kept=True,no_nominal_or_second_PPO_scope=True),indent=2),encoding='utf8');print(json.dumps(dict(materialized=True,no_GPU=True)))
if __name__=='__main__':main()
