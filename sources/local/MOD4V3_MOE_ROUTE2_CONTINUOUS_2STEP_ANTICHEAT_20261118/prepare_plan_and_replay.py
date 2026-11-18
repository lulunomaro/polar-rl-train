from pathlib import Path
import hashlib
import json
import shutil
import sys
import numpy as np
import torch

T = Path(__file__).resolve().parent
sys.path[:0] = [str(T), str(T / 'support')]
import evaluate_student200
from mod4v3_ppo_v1.route2_common import HistoryQueue

mpath = T / 'weights/model_step000.pt'
sha = hashlib.sha256(mpath.read_bytes()).hexdigest()
assert sha == '1c072fc4f1055aee0384520e0588c8ca8168010c996744e74baaa535f2f1e2e2', sha

cdir = T / 'bootstrap_replay/elegant_r2_clean'
saved = len(list(cdir.glob('episode_*.npz')))
print('Total clean episodes:', saved)
assert saved >= 6

# Update PLAN.json for 0-PPO precheck first (probe requires PPO_training_authorized=False, authorized_PPO_seconds=0, human_restart_authorized=False)
remote_root = '/home/egde/rl_candidates/mod4v3_moe_route2_elegant_gated_ppo_20261118_r1'
plan = json.loads((T / 'PLAN.json').read_text(encoding='utf8'))
plan['experiment'] = 'MOD4V3_MOE_ROUTE2_ELEGANT_GATED_PPO_20261118'
plan['root'] = remote_root
plan['support'] = remote_root + '/support'
plan['parent'] = remote_root + '/model_step000.pt'
plan['parent_sha256'] = sha
plan['locked_v1_sha256'] = sha
plan['local_skill_preflight_passed'] = True
plan['training_job'] = 'train_elegant_gated_40m'
plan['training_round'] = 'elegant_gated_lqr_top_park_40m'
plan['native_probe']['job'] = 'native_elegant_gated_probe_r1'
plan['route2']['E1_initial_std'] = [0.012, 0.012, 0.012, 0.012, 0.025, 0.025]
plan['route2']['E1_trainable'] = [
    'encoder (16D history latent)',
    'climb head (51->256->128->64->6)',
    'top_park head (51->256->128->64->6)',
    'independent6D logSTD',
    'independent78D critic',
]
plan['route2']['v1_anchor']['source_sha256'] = sha
plan['bootstrap_replay_dirs'] = [remote_root + '/bootstrap_replay/elegant_r2_clean']
plan['PPO_training_authorized'] = False
plan['authorized_PPO_seconds'] = 0
plan['human_restart_authorized'] = False
plan['zero_update_precheck_passed'] = False
(T / 'PLAN.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print('Updated PLAN.json for 0-PPO native precheck.')
