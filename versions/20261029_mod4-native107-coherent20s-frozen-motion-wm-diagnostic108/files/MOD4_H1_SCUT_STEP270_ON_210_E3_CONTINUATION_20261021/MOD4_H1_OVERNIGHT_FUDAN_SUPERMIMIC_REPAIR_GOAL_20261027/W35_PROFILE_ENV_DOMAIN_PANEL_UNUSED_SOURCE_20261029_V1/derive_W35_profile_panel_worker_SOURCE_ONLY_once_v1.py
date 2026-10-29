"""Read exact old Python worker only; create NEW candidate and inverse proof.

No model/NPZ/USD/SDK import or runtime invocation. No modification of old bytes.
"""
import ast
import hashlib
import json
from pathlib import Path
import time
import traceback

D = Path(__file__).resolve().parent
BASE = D.parent / 'W35_210_FULL_PROFILE_OWN_STORAGE_METADATA_EXTENSION_SOURCE_V1/evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py'
TARGET = D / 'evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v1.py'


def write_json(name, value):
    with (D / name).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    raw = BASE.read_bytes()
    text = raw.decode('utf-8')
    changes = [
        ("MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1", "MOD4_W35_ADAPTED92_PROFILE_ENV_DOMAIN_PANEL_V1"),
        ("task['controls']==1200", "task['controls']==600"),
        ("import torch,numpy as np,rescue_training", "import torch,numpy as np,rescue_training\n from w35_profile_env_domain_panel_v1 import W35DomainPanel\n panel_state=[None]"),
        ("  ids=torch.arange(32,device=real.device);", "  panel=W35DomainPanel(real,torch,OUT,task);panel_state[0]=panel\n  ids=torch.arange(32,device=real.device);"),
        ("   age[~live]=0;turn[~live]=0;previous_key=", "   panel.terminal(ctx)\n   age[~live]=0;turn[~live]=0;previous_key="),
        ("for i in range(1200):", "for i in range(600):"),
        ("heading=tensor(robot.data.heading_w).clone());root=", "heading=tensor(robot.data.heading_w).clone());panel.begin(i,ctx);root="),
        ("requested=action[ids].clone();terminal[0]=None;", "requested=action[ids].clone();panel.requested(action,obs);terminal[0]=None;"),
        ("    row=dict(before_root13=", "    panel.after_step(done,info)\n    row=dict(before_root13="),
        ("  path=OUT/'selected32_full_motion_before_and_terminal.npz'", "  panel.finish()\n  path=OUT/'selected32_full_motion_before_and_terminal.npz'"),
        ("requested_controls=1200", "requested_controls=600"),
        ("wall_time_limited=completed<1200", "wall_time_limited=completed<600"),
        (" finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()", " finally:\n  try:\n   if panel_state[0] is not None:panel_state[0].uninstall()\n  finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()"),
    ]
    for old, new in changes:
        assert text.count(old) == 1, (old, text.count(old))
        text = text.replace(old, new, 1)
    candidate = text.encode('utf-8')
    ast.parse(candidate)
    inverse = text
    for old, new in reversed(changes):
        assert inverse.count(new) == 1, (new, inverse.count(new))
        inverse = inverse.replace(new, old, 1)
    assert inverse.encode('utf-8') == raw
    tree = ast.parse(candidate)
    forbidden = {'torch.load', 'torch.save', 'optimizer.step', 'alg.update', 'runner.learn'}
    original_tree = ast.parse(raw)
    def calls(t):
        return [ast.unparse(n.func) for n in ast.walk(t) if isinstance(n, ast.Call)]
    assert all(calls(tree).count(name) == calls(original_tree).count(name) for name in forbidden)
    with TARGET.open('xb') as f:
        f.write(candidate)
    # No old binary path in the worker is opened by this builder.
    write_json('WORKER_EXACT_SOURCE_OVERLAY_AND_INVERSE_ACTUAL.json', dict(
        epoch=time.time(), base_path=str(BASE), base_bytes=len(raw), base_SHA256=hashlib.sha256(raw).hexdigest(),
        target_path=str(TARGET), target_bytes=len(candidate), target_SHA256=hashlib.sha256(candidate).hexdigest(),
        exact_changes=[dict(old=old,new=new) for old,new in changes], inverse_bytes_exact=True,
        AST_parse_passed=True, new_model_load_save_optimizer_calls=0,
        preserved='Original SDK/fullrestore/norm/17Adam/LR/40050/N20K/G3/nearest250/physics/actions/commands/reset criteria/integrity checks; no old worker edit',
        new_scope='600 controls 100 warmup 500 steady; profile x env counters and selected domain diagnostics; not an identical1200 rerun',
        no_model_NPZ_USD_or_remote_read=True, actual_target_admission_pending=True))
    print(json.dumps(dict(passed=True, worker=str(TARGET), SHA256=hashlib.sha256(candidate).hexdigest(), inverse_bytes_exact=True)))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        write_json('ORIGINAL_SOURCE_DERIVATION_ERROR_' + str(time.time_ns()) + '.json',dict(passed=False,traceback=traceback.format_exc()))
        raise
