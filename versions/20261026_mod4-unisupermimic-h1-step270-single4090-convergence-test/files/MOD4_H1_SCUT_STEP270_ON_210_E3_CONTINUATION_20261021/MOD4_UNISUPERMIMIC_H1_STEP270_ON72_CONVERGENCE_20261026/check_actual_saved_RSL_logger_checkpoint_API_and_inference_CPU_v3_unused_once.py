"""Execute the saved actual72 RSL save methods, not a guessed logger API."""
from pathlib import Path
import ast
import hashlib
import json
import sys
import time
import types
import torch

H=Path(__file__).resolve().parent;T=H.parent
report=T/'MOD4_MIXED_PRECISION_STEP_THROUGHPUT_AFTER67_20261025/reports/ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_72_ACTUAL.json'
rows=json.loads(report.read_bytes())['sources'];scope={'torch':torch}
methods={}
for row in rows:
    tree=ast.parse(row['text']);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
    name='save_model' if row['path'].endswith('logger.py') else 'save'
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),row['path'],'exec'),scope)
    methods[name]=scope[name]
out=H/'reports/ACTUAL_RSL_CHECKPOINT_API_CPU_V3_FIXTURE';assert not out.exists();out.mkdir()
logger=types.SimpleNamespace()
logger.save_model=types.MethodType(methods['save_model'],logger)
base=dict(actor_state_dict={'one':torch.arange(3.)},critic_state_dict={'one':torch.ones(2)},optimizer_state_dict={'one':torch.tensor(1.)})
runner=types.SimpleNamespace(alg=types.SimpleNamespace(save=lambda:dict(base)),logger=logger,current_learning_iteration=0)
runner.save=types.MethodType(methods['save'],runner)
negative=out/'original_missing_writer_saved_base_then_error.pt'
try:runner.save(str(negative))
except AttributeError as error:expected=str(error)
else:raise AssertionError('Actual missing-writer regression not reproduced')
assert 'writer' in expected and negative.exists()
runner.logger.writer=None
positive=out/'actual_RSL_writer_none_save_pass.pt';runner.save(str(positive));saved=torch.load(positive,map_location='cpu',weights_only=False)
assert torch.equal(saved['actor_state_dict']['one'],base['actor_state_dict']['one'])
candidate=H/'candidate_source_v3/h1_supermimic_bridge_v1.py';tree=ast.parse(candidate.read_text('utf8'));run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
assignment=next(n for n in run.body if isinstance(n,ast.Assign) and ast.unparse(n).startswith('runner.logger.writer = None'))
oldsave_index=next(i for i,n in enumerate(run.body) if isinstance(n,ast.Assign) and ast.unparse(n).startswith('oldsave = runner.save'))
assert run.body.index(assignment)<oldsave_index
save=next(n for n in run.body if isinstance(n,ast.FunctionDef) and n.name=='save')
scope=dict(torch=torch,oldsave=runner.save,learner=types.SimpleNamespace(_checkpoint=lambda include:dict(wm={'w':torch.ones(2)},pi={'p':torch.zeros(6)},critic={'v':torch.ones(1)},opt_wm={'step':torch.tensor(1)},opt_pi={'step':torch.tensor(1)},opt_v={'step':torch.tensor(1)}),obs_hist=torch.zeros(2,10,128)),bridge=types.SimpleNamespace(ep_step=torch.zeros(2,dtype=torch.int32)))
exec(compile(ast.Module(body=[save],type_ignores=[]),str(candidate),'exec'),scope)
full=out/'actual_RSL_plus_native_full_save_pass.pt';scope['save'](str(full));value=torch.load(full,map_location='cpu',weights_only=False)
assert 'UniSuperMimic_H1_test' in value and value['UniSuperMimic_obs_history'].shape==(2,10,128)
assert torch.equal(value['actor_state_dict']['one'],base['actor_state_dict']['one'])
with torch.inference_mode():buffer=torch.zeros(2)
try:buffer.add_(1)
except RuntimeError as error:inference_error=str(error)
else:raise AssertionError('Expected inference compatibility regression not reproduced')
with torch.inference_mode():buffer.add_(1)
assert torch.equal(buffer,torch.full((2,),2.)) # failed forbidden update changes value before raising in torch
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1Bridge')
for name in ('pack','current','before_action','step'):
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    assert [ast.unparse(d) for d in fn.decorator_list]==['torch.inference_mode()']
assert not torch.cuda.is_initialized()
artifacts=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (negative,positive,full)]
result=dict(epoch=time.time(),passed=True,saved_actual_RSL_sources=[{k:r[k] for k in ('path','bytes','SHA')} for r in rows],observed_missing_writer_negative=expected,actual_RSL_writer_none_save_passed=True,actual_bridge_fullsave_wrapper_saved_original_and_native_optimizer_groups=True,prospective_inference_tensor_error=inference_error,physical_hooks_original_inference_context=True,small_CPU_artifacts=artifacts,no_model_source_or_GPU_or_physics_or_budget_action=True,candidate_uninstalled=True)
with (H/'reports/ACTUAL_RSL_CHECKPOINT_API_AND_INFERENCE_CONTEXT_CPU_V3_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(actual_saved_RSL_save_API_passed=True,native_fullsave_wrapper_passed=True,CPU_only=True)))
