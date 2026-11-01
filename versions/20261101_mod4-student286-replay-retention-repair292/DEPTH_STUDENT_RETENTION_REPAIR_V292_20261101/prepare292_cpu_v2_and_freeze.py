from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=N/'test292_bounded_update_source.py'
text=old.read_text('utf8').replace('import json,time,torch','import json,time,torch\nfrom copy import deepcopy').replace('state=opt.state_dict();','state=deepcopy(opt.state_dict());')
p=N/'test292v2_bounded_update_source.py';p.write_bytes(text.encode());ast.parse(text)
with (R/'CPU292_V1_TEST_READER_ALIAS_FALSE.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original_error='AssertionError comparing restored optimizer to shallow state_dict; expected snapshot shared live tensors mutated by attempted step.',repair='Independent v2 test uses deepcopy snapshot. Production bounded step already deepcopies.',model_reads=0,CUDA=False,production_not_launched=True,old_test_preserved=True),f,indent=2)
task=json.loads((N/'TASK292_FROZEN.json').read_bytes());task['source_CPU_report_SHA']=H(p);task['actual_learning_GO_pending']=True
(N/'TASK292_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
print(json.dumps(dict(passed_AST=True,test=str(p))))
