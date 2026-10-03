"""Prepare candidate from exact current source; no production writes or budget ownership."""
import ast
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
sha = lambda text: hashlib.sha256(text.encode()).hexdigest()
before = (D / "current_source/mod4_task.py").read_text(encoding="utf8")
anchor = "import scut_flat_rescue as scut_rescue\n"
assert before.count(anchor) == 1
after = before.replace(anchor, anchor + "from rolling_consistency import spin_contact_consistency as rolling_cost\n")
anchor = "    # --- skills: 小陀螺 / 过洞 / 飞坡"
assert after.count(anchor) == 1
after = after.replace(anchor, """    # Isolated loaded_rolling_v1: only this additional pure-spin reward changes.
    if os.environ.get('RM_SPIN_ROLLING_PROFILE', 'off') == 'v1':
        spin_contact_consistency = RewTerm(func=rolling_cost, weight=-.3,
            params={'speed_scale': .15, 'yaw_min': 3.5, 'support_weight': .25})

""" + anchor)
a, b = ast.parse(before), ast.parse(after)
removed = False
for node in b.body:
    if isinstance(node, ast.ClassDef) and node.name == "RewardsCfg":
        node.body = [x for x in node.body if not (
            isinstance(x, ast.If) and any(isinstance(t, ast.Constant) and t.value == 'RM_SPIN_ROLLING_PROFILE' for t in ast.walk(x)))]
        removed = True
b.body = [n for n in b.body if not (isinstance(n, ast.ImportFrom) and n.module == 'rolling_consistency')]
assert removed and ast.dump(a) == ast.dump(b), "Only one reward addition is authorized"
(D / "mod4_task_candidate.py").write_text(after, encoding="utf8")
probe = (D / "current_source/spin_rate_probe.py").read_text(encoding="utf8")
probe = probe.replace("p.add_argument('--seed'", "p.add_argument('--rolling-profile', choices=['off','v1'], default='v1');p.add_argument('--seed'", 1)
probe = probe.replace("os.environ['RM_MILD_DR_PROFILE']=args.dr_profile", "os.environ['RM_MILD_DR_PROFILE']=args.dr_profile;os.environ['RM_SPIN_ROLLING_PROFILE']=args.rolling_profile", 1)
probe = probe.replace("    start=time.time()", "    rolling_samples=[]\n    start=time.time()", 1)
probe = probe.replace("_,_,done,_=vec.step(action)", "_,reward,done,_=vec.step(action)\n        if step in (0,49,50,100,299):\n            from rolling_consistency import spin_contact_consistency\n            _=spin_contact_consistency(env)\n            snapshot=env._spin_rolling_consistency.last\n            rolling_samples.append(dict(step=step,total_reward=reward.cpu().tolist(), **{k:v.cpu().tolist() for k,v in snapshot.items()}))", 1)
probe = probe.replace("    Path(args.output).write_text", "    result['rolling_input_readback']=dict(profile=args.rolling_profile,metadata=env._spin_rolling_consistency.metadata,samples=rolling_samples,weight=-.3,original_gates_unchanged=True)\n    Path(args.output).write_text", 1)
(D / "rolling_readback_probe.py").write_text(probe, encoding="utf8")
(D / "CANDIDATE_DIFFERENCE_AUDIT.json").write_text(json.dumps(dict(
    original_task_sha=hashlib.sha256((D / 'current_source/mod4_task.py').read_bytes()).hexdigest(),
    candidate_task_sha=hashlib.sha256((D / 'mod4_task_candidate.py').read_bytes()).hexdigest(),
    normalized_original_task_sha=sha(before), normalized_candidate_task_sha=sha(after),
    task_AST_except_one_import_and_reward_exact=True, reward_weight=-.3,
    cost_cap=4.25, max_new_reward_magnitude_per_second=1.275,
    speed_scale_m_s=.15, yaw_min_rad_s=3.5, support_weight=.25,
    fixed_first_cap=5, fixed_profile='white_v2', observation_action_reset_physics_PPO_unchanged=True,
    no_claim_of_behavior_fix_yet=True), indent=2), encoding="utf8")
print("Isolated one-reward candidate built; other task AST exact.")
