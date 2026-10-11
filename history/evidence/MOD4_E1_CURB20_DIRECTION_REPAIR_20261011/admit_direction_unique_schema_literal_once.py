from direction_io import *
import traceback
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_SCHEMA_REVIEWED_20261011'
def main():
 n,w=io.connect_both()
 try:
  v=run(n,'''from pathlib import Path
import sys,json,time,torch,hashlib,ast
D=Path(NEWROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
schema=json.loads(SCHEMA_JSON_LITERAL)
assert schema['actor']==['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']
assert schema['critic']==['mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']
p=C/'curb20_direction_schema_reviewed_target_cpu.py';raw=p.read_bytes();t=raw.decode();assert t.count('assert len(tensors)==16')==1
t=t.replace('assert len(tensors)==16','assert len(tensors)==17').replace('DIRECTION_COMPONENT_CPU_ROUNDTRIP.pt','DIRECTION_COMPONENT_CPU_ACTUAL_SCHEMA_ROUNDTRIP.pt')
ns={};exec(compile(t,str(p)+'_actual_schema_reader','exec'),ns);v=ns['verify'](D)
v.update(epoch=time.time(),actual_actor_critic_std_tensors=17,actual_separate_actor_critic_schema=schema,original_reader_SHA=hashlib.sha256(raw).hexdigest(),reviewed_reader_SHA=hashlib.sha256(t.encode()).hexdigest(),reader_schema_only_no_runtime_code_change=True)
assert not (D/'reports/DIRECTION_TARGET_CPU_PASSED.json').exists()
(D/'reports/DIRECTION_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
import supervise_curb20_direction_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D and own.inherited.R==D/'reports'
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,root=str(D),source_freeze=json.loads((D/'reports/SOURCE_FREEZE.json').read_bytes()),component=v,correct_import_main_Popen_paths=True,no_GPU_launch=True)))
'''.replace('NEWROOT',repr(NEW)).replace('SCHEMA_JSON_LITERAL',repr((R/'DIRECTION_ACTUAL_ACTOR_CRITIC_SCHEMA_READ.json').read_text())))
  save('DIRECTION_ACTUAL_SCHEMA_TARGET_CPU_PASSED.json',v);save('DIRECTION_ACTIVE_ROOT.json',dict(root=NEW,source_count=len(v['source_freeze']['sha256']),CPU_passed=True,old_CPU_only_root_not_launched=True));print(json.dumps(dict(root=NEW,CPU_passed=True,no_GPU_launch=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_ACTUAL_SCHEMA_UNIQUE_READER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
