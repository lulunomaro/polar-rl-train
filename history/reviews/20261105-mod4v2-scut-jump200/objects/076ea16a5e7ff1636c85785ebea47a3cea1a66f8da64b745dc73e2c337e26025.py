"""CPU rejection of a history-crossing hypothesis under actual endpoint reset."""
from pathlib import Path
import importlib.util
import json
import sys
import time

import torch


N = Path(__file__).resolve().parent
sys.path.insert(0, 'F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/source')
from ctx_reward_learner import ContextReplayBuffer

P = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut/supermimic_newton.py')
spec = importlib.util.spec_from_file_location('mod4_history_boundary_review', P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
buf = mod.valid_replay(ContextReplayBuffer(4, 1, 'cpu', 30, 139, 6), 'cpu')
for row, (frame, valid) in enumerate(((50,True), (51,True), (52,False), (1,True))):
    item = {key:torch.zeros_like(value[0]) for key,value in buf.data.items()}
    item['s'][:,3] = 1.
    item['s1'][:,3] = 1.
    item['xi'][:,0] = 100. + row if row < 3 else .6
    item['f'].fill_(frame);item['ep_step'].fill_(frame)
    item['sample_valid'].fill_(valid)
    item['done'].fill_(not valid);item['term'].fill_(not valid)
    item['xi1_valid'].fill_(valid)
    buf.add(item)
# Sample deterministically from the valid first endpoint after a mid-control
# numerical reset. Current step() increments the reset episode counter to1.
buf._valid_draw = lambda B, max_age=None: (torch.full((B,),3), torch.zeros(B,dtype=torch.long))
start, history = buf.sample_starts(1, 3)
assert start['f'].item() == 1 and history['f'].tolist() == [[52,52,1]]
assert not buf.data['sample_valid'][2,0] and buf.data['stream_cut'][2,0]
synthetic_crossing = history['f'].tolist()
# Actual Newton step forces hard termination and a SECOND reset at endpoint,
# so the public next observation is frame0, not the frame1 hypothesis above.
buf.data['f'][3,0] = 0
buf.data['ep_step'][3,0] = 0
actual_start, actual_history = buf.sample_starts(1, 3)
assert actual_history['f'].tolist() == [[0,0,0]]
out=N/'supermimic_abstraction_audit_cpu/HISTORY_BOUNDARY_CORRECTED.json'
out.write_text(json.dumps(dict(epoch=time.time(),
    scope='CPU synthetic replay rows, forced deterministic sampler. Compare rejected frame1 hypothesis with actual returned frame0 reset semantics.',
    row_frames=[50,51,52,1], row_sample_valid=[True,True,False,True],
    unreachable_frame1_hypothesis_history=synthetic_crossing,
    actual_returned_start_frame=int(actual_start['f']), actual_returned_history_frames=actual_history['f'].tolist(),
    invalid_previous_row_has_stream_cut=True,
    finding='Generic sampler does not inspect history cut flags, but current Newton hard-termination endpoint reset returns ep_step0, pads correctly and blocks this hypothesized crossing. Not an additional demonstrated current bug.',
    initial_hypothesis_rejected=True,
    standard_endpoint_reset_ep_step0_is_padded_correctly=True,
    production_PT_reads=0, real_physics_steps=0, optimizer_updates=0,
    production_source_changes=0, SSH=0),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(report=str(out),history_frames=actual_history['f'].tolist(),initial_hypothesis_rejected=True,
    production_PT_reads=0,real_physics_steps=0),ensure_ascii=False))
