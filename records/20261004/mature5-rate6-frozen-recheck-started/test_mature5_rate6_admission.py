"""CPU tests for the frozen diagnostic admission, with no simulator imports."""
import ast,copy
from pathlib import Path
code=Path(__file__).with_name('run_mature5_rate6_recheck.py').read_text()
tree=ast.parse(code);fn=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name=='validate_admission')
sha='253ed8effd5fe8580859bce1b7731006ae62a5e7bf1c63a9f8825de2c74bc73e'
ctx={'SOURCE_SHA':sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<isolated_admission>','exec'),ctx)
source={'path':'formal17039','sha256':sha}
state={'mature':{'checkpoint':'formal17039','cap':5.,'profile':'white_v2'},'chosen_checkpoint':'formal17039','profile':'white_v2','consecutive':2,'active_training':None,'rate_rejected':[5.,6.]}
p={'pass':True,'fixed_cap':5.,'profiles':['nominal','white_v2'],'checkpoint':source,'pairs':[dict(seed=s,kind=k,initial_root_q_exact=True,original_plus_individual_safety_gates=[True,True],actual_parameter_readbacks=[True,True]) for s in (20261002,20261003) for k in ('flat','spin')]}
ctx['validate_admission'](p,state,source)
for bad in range(8):
 a,b,c=copy.deepcopy(p),copy.deepcopy(state),copy.deepcopy(source)
 if bad==0:a['pass']=False
 elif bad==1:a['fixed_cap']=4.
 elif bad==2:a['pairs'][0]['initial_root_q_exact']=False
 elif bad==3:a['pairs'][0]['actual_parameter_readbacks']=[True,False]
 elif bad==4:b['active_training']={'pid':123}
 elif bad==5:b['consecutive']=1
 elif bad==6:c['sha256']='wrong_source'
 elif bad==7:a['pairs']=a['pairs'][:3]
 try:ctx['validate_admission'](a,b,c)
 except AssertionError:pass
 else:raise AssertionError(bad)
print('Nine CPU admission checks passed: complete mature5 evidence accepted; failed, incomplete, wrong-source, active-PPO, or nonpaired evidence rejected.')
