"""Distinct427 CPU fixture keeps savedCUDA RNGopaque; no replay426once."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

P=Path(__file__).resolve().parent
T=P.parent
O=T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V426_20261102'
C=T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V427_20261102'
assert not C.exists()
assert list((O/'reports').glob('CPU426_ORIGINAL_ERROR_*.json'))
C.mkdir()
(C/'reports').mkdir()
shutil.copytree(O/'source',C/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in ('feedforward389.json','reference389.npz'):
    shutil.copyfile(O/name,C/name)
learner=(O/'source/actual_transition_learner426.py').read_text('utf8')
learner=learner.replace('ActualTransitionLearner426','ActualTransitionLearner427').replace('ACTUAL426_FULL_RESTORE','ACTUAL427_FULL_RESTORE')
ast.parse(learner)
(C/'source/actual_transition_learner427.py').write_bytes(learner.encode('utf8'))
test=(O/'test426_actual_saved_rollout_trust_step_CPU_once.py').read_text('utf8')
test=test.replace('426','427')
test=test.replace("    wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())",
    "    preserved_WM_CUDA_RNG=carrier['world_model']['dedicated_sampling_rng'].clone()\n    assert preserved_WM_CUDA_RNG.numel()==16\n    # CPU fixture samples noWM transitions; CUDAstate is preserved opaque, notloadedintoCPUgenerator.")
test=test.replace('    learner = ActualTransitionLearner427(wm,carrier,reference,env,binding,H(proofpath),put)',
    "    preserved_actor_CUDA_RNG=carrier['student']['residual_sampling_rng'].clone()\n    assert preserved_actor_CUDA_RNG.numel()==16\n    fixturecarrier=dict(carrier,student=dict(carrier['student'],residual_sampling_rng=torch.Generator(device='cpu').manual_seed(427).get_state()))\n    learner = ActualTransitionLearner427(wm,fixturecarrier,reference,env,binding,H(proofpath),put)")
test=test.replace("        source_offsets=[56304,13364,25556],sourcefullrestore_exact=True,",
    "        source_offsets=[56304,13364,25556],source_network_Adam_EMA_origin_restore_exact=True,\n        CUDA_RNG_preserved_opaque_not_CPUloaded=True,CPU_fixture_rng_explicit=True,production_GPU_RNG_restore_code_unchanged=True,")
ast.parse(test)
(C/'test427_actual_saved_rollout_trust_step_CPU_once.py').write_bytes(test.encode('utf8'))
task=json.loads((O/'TASK426_CANDIDATE.json').read_bytes())
task.update(epoch=time.time(),independent427_devicecorrectfixture=True,
    original426errorpreserved=True,CUDA_RNG_CPU_fixture='Opaque savedGPUstates retained; no CPUformatreinterpretation; explicit new CPUfixturegenerator only; production sameGPUrestoresoriginalGPUstate',
    learnerSHA=hashlib.sha256((C/'source/actual_transition_learner427.py').read_bytes()).hexdigest())
with(C/'TASK427_CANDIDATE.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2,ensure_ascii=False)
print(json.dumps(dict(passed=True,root=str(C),learnerSHA=task['learnerSHA'],network=0,SDK=0,modelreads=0)))
