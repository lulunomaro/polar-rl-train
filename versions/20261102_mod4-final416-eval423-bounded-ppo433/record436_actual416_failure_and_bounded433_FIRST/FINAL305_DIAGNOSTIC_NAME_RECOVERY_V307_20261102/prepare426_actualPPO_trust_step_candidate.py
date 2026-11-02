"""KeepactualPPO/reward, bound actual post-Adam policy change after416earlyfailure."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

P = Path(__file__).resolve().parent
T = P.parent
N = T / 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
C = T / 'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V426_20261102'
assert not C.exists()
C.mkdir()
(C / 'reports').mkdir()
shutil.copytree(N / 'source', C / 'source', ignore=shutil.ignore_patterns('__pycache__'))
for name in ('feedforward389.json','reference389.npz'):
    shutil.copyfile(N / name, C / name)
text = (N / 'source/actual_transition_learner409.py').read_text('utf8')
text = text.replace('class ActualTransitionLearner409:', 'class ActualTransitionLearner426:')
text = text.replace('(56144, 13204, 20419)', '(56304, 13364, 25556)')
text = text.replace("self.generator = torch.Generator(device=wm.device).manual_seed(409)",
    "self.generator = torch.Generator(device=wm.device)\n        self.generator.set_state(saved['residual_sampling_rng'].cpu())")
text = text.replace("ACTUAL409_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json", 'ACTUAL426_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json')
old = '''        if apply_step:
            self.actor_optimizer.step()
            self.critic_optimizer.step()'''
new = '''        trust = dict(applied=False, nominal_lr=1e-4, KL_limit=.01, max_action_delta_limit=.05)
        if apply_step:
            # With oneepoch the PPO ratio is1 before Adam. Measure the proposed
            # policy after Adam, not just the pre-update surrogate clipping.
            before_weights = [parameter.detach().clone() for parameter in self.actor.parameters()]
            before_optimizer = deepcopy(self.actor_optimizer.state_dict())
            old_mean = mean.detach().clone()
            with torch.no_grad():
                # baseline cancels in the action delta; no changed command table.
                old_residual = torch.tanh(old_mean)
            accepted = False
            for exponent in range(13):
                with torch.no_grad():
                    for parameter,before in zip(self.actor.parameters(),before_weights):parameter.copy_(before)
                self.actor_optimizer.load_state_dict(deepcopy(before_optimizer))
                factor = .5**exponent
                for group in self.actor_optimizer.param_groups:group['lr']=1e-4*factor
                self.actor_optimizer.step()
                with torch.no_grad():
                    updated = forward(self.actor,x)-forward(self.residual_origin_actor,x)
                    actual_KL = .5*((updated-old_mean)/self.latent_std).square().sum(-1).mean()
                    action_delta = (torch.tanh(updated)-old_residual).abs().amax()
                if torch.isfinite(actual_KL) and torch.isfinite(action_delta) and actual_KL<=.01 and action_delta<=.05:
                    accepted = True
                    trust = dict(applied=True, nominal_lr=1e-4, accepted_lr=1e-4*factor, factor=factor,
                        KL_limit=.01, actual_KL=float(actual_KL), max_action_delta_limit=.05,
                        actual_max_action_delta=float(action_delta), proposals=exponent+1,
                        rejected_candidate_weights_and_Adam_fully_restored=True, one_committed_Adam_step=True)
                    break
            assert accepted, 'No finite policytruststep; preserveerrorcheckpoint withoutunboundedactorstep'
            self.critic_optimizer.step()'''
assert text.count(old) == 1
text = text.replace(old, new)
text = text.replace('            source=\'actual own onpolicy rewards/done/latentlogprob; no WM imaginedreturns\',',
    "            actor_trust_step=trust,\n            source='actual own onpolicy rewards/done/latentlogprob; no WM imaginedreturns',")
text = text.replace("            origin_frozen_from389=True,goal_dim=59", "            actor_trust_protocol=dict(kind='POST_ADAM_ACTUAL_KL_AND_RESIDUAL_DELTA',KL_limit=.01,max_action_delta=.05,max_backtracks=12),\n            origin_frozen_from389=True,goal_dim=59")
ast.parse(text)
(C / 'source/actual_transition_learner426.py').write_bytes(text.encode('utf8'))
task = dict(epoch=time.time(), source_fullCPU_receipt=str(N / 'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
    source_offsets=[56304,13364,25556], sourceSHA='8365d243006ef5ed6818d01298003107808f918347ad929f4ea936544f96e01a',
    concrete_basis='Actual423all80orientation/.812smean, earlyresidualbiasat.22s. OneepochPPOratiois1beforeAdam; pre-stepclipdoesnotboundactualpostAdamchange. Thisisnotproofthatstepsizeissolecause.',
    repair='SameactualPPOrollout32/rewarddoneGAE/actorandorigin/fullAdam; boundpostAdammeanKL.01andmaxnormalizedresidualdelta.05byrestoringrejectedcandidateweightsandallAdamstate, commitoneacceptedstep',
    unchanged_reward_physics_horizon=True, actor_WM_gradient=False, no_reset_network_origin_Adam=True,
    necessary_final416_CPU_reads_max=1, no_physics=True, productionGO=False)
with (C / 'TASK426_CANDIDATE.json').open('x', encoding='utf8') as stream:
    json.dump(task, stream, indent=2, ensure_ascii=False)
print(json.dumps(dict(passed=True, root=str(C), learnerSHA=hashlib.sha256((C / 'source/actual_transition_learner426.py').read_bytes()).hexdigest(),productionGO=False)))
