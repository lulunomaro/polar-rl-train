"""Generate NEW isolated core copy + unified diff; never modify baseline bytes."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / 'source_core_review' / 'ctx_reward_learner.py'
TARGET = HERE / 'ctx_reward_candidate_v1.py'


def emit(path, text):
    if path.parent != HERE:
        raise ValueError('writes restricted to new candidate directory')
    if path.exists():
        if path.read_text(encoding='utf-8') != text:
            raise FileExistsError(str(path))
    else:
        path.write_text(text, encoding='utf-8', newline='\n')


def build():
    before = BASE.read_text(encoding='utf-8')
    source_sha = hashlib.sha256(BASE.read_bytes()).hexdigest()
    out = before
    edits = [
        ("SOURCE_ONLY: task-reward/context SuperMimic extension; never launches an env.",
         "OFFLINE_CANDIDATE: raw35/transition/reward hooks; never launches an env."),
        ("'schema': 'mod4v1.ctx_task_reward.v1'",
         "'schema': 'mod4v1.ctx_task_reward.command_candidate.v1'"),
        ("        loss, parts = self.aux.supervised_loss(features, sample['r'], sample['xi1'] - sample['xi'],\n",
         "        reward_target = sample['r']\n"
         "        target_hook = getattr(self.mdp, 'aux_reward_target', None)\n"
         "        if callable(target_hook):\n"
         "            reward_target = target_hook(sample, state, state1)\n"
         "        loss, parts = self.aux.supervised_loss(features, reward_target, sample['xi1'] - sample['xi'],\n"),
        ("        actions, rewards, dones = [], [], []\n",
         "        actions, rewards, dones = [], [], []\n        policy_penalties = []\n"),
        ("                reward, delta_context, done_logit = self.aux(features)\n"
         "                next_context = context + self.context_predict_mask * delta_context\n"
         "                project = getattr(self.mdp, 'project_predicted_context', None)\n"
         "                if callable(project):\n"
         "                    next_context = project(next_context, state1, action, next_frames)\n",
         "                reward, delta_context, done_logit = self.aux(features)\n"
         "                reward_hook = getattr(self.mdp, 'project_imagined_reward', None)\n"
         "                if callable(reward_hook):\n"
         "                    reward = reward_hook(reward, state, state1, action, previous_action, context, frames)\n"
         "                regularize = getattr(self.pi, 'policy_regularizer', None)\n"
         "                if callable(regularize):\n"
         "                    policy_penalties.append(regularize(obs_hist, goal, action))\n"
         "                transition_project = getattr(self.mdp, 'project_transition_context', None)\n"
         "                if callable(transition_project):\n"
         "                    next_context = transition_project(context, state, state1, action, frames,\n"
         "                                                      next_frames, delta_context, self.context_predict_mask)\n"
         "                else:\n"
         "                    next_context = context + self.context_predict_mask * delta_context\n"
         "                    project = getattr(self.mdp, 'project_predicted_context', None)\n"
         "                    if callable(project):\n"
         "                        next_context = project(next_context, state1, action, next_frames)\n"),
        ("            loss = -objective.mean()\n",
         "            loss = -objective.mean()\n"
         "            if policy_penalties:\n"
         "                loss = loss + torch.stack(policy_penalties).mean()\n"),
        ("imagined_reward_source='original_real_reward_supervised_head'",
         "imagined_reward_source='original_reward_head_or_explicit_component_decomposition'")
    ]
    for old, new in edits:
        if out.count(old) != 1:
            raise ValueError('baseline anchor must occur once: ' + repr(old[:110]))
        out = out.replace(old, new, 1)
    ast.parse(out)
    # These methods must remain AST-identical: masks, history, replay and resume.
    base_tree, out_tree = ast.parse(before), ast.parse(out)
    def methods(tree, class_name):
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
        return {n.name: ast.dump(n, include_attributes=False) for n in cls.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for cls in ('ContextReplayBuffer', 'TaskAuxiliaryModel'):
        if methods(base_tree, cls) != methods(out_tree, cls):
            raise AssertionError('protected replay/aux class changed: ' + cls)
    a, b = methods(base_tree, 'ContextRewardLearner'), methods(out_tree, 'ContextRewardLearner')
    changed = sorted(k for k in a if a[k] != b[k])
    if changed != ['__init__', 'aux_update', 'policy_update']:
        raise AssertionError(('unexpected changed methods', changed))
    # __init__ changes ONLY the checkpoint schema literal above.
    emit(TARGET, out)
    diff = ''.join(difflib.unified_diff(before.splitlines(True), out.splitlines(True),
                    fromfile=str(BASE), tofile=str(TARGET)))
    emit(HERE / 'SOURCE_TO_CANDIDATE_DIFF_V1.patch', diff)
    result = dict(kind='SOURCE_ONLY_ISOLATED_COPY', baseline_path=str(BASE),
                  baseline_SHA256=source_sha, candidate_path=str(TARGET),
                  candidate_SHA256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),
                  replacements=len(edits), changed_methods=changed,
                  protected_replay_aux_classes_ast_identical=True,
                  collect_resume_history_and_bptt_receipt_methods_ast_identical=True,
                  original_file_unchanged=source_sha == hashlib.sha256(BASE.read_bytes()).hexdigest(),
                  executed_training=False, SDK_imported=False, Torch_imported=False)
    emit(HERE / 'BUILD_CANDIDATE_RECEIPT_V1.json', json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    build()
