"""Memory-path parity for real replay schema, no model read or physics."""
from pathlib import Path
import json,sys,time,torch
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
N=Path(__file__).resolve().parent
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.supermimic_newton import load_sources,valid_replay
load_sources(G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json')
from ctx_reward_learner import ContextReplayBuffer
base=ContextReplayBuffer(16,8,'cpu',30,139,6)
host=valid_replay(base,'cuda:0')
for i in range(24):
    value={k:torch.full(v.shape[1:],i,dtype=v.dtype,device='cuda:0')for k,v in host.data.items()}
    for key in ('done','term','trunc','sample_valid'):value[key].fill_(False)
    value['sample_valid'].fill_(True);value['sample_valid'][i%8]=False
    value['xi1_valid'].fill_(True)
    host.add(value)
assert host.size==16 and host.ptr==8
copy=valid_replay(ContextReplayBuffer(16,8,'cpu',30,139,6),'cpu')
copy.import_state(host.export_state())
for method,args in [('sample_transitions',(128,)),('sample_windows',(128,8)),('sample_starts',(128,10))]:
    torch.manual_seed(7);a=getattr(host,method)(*args)
    torch.manual_seed(7);b=getattr(copy,method)(*args)
    for left,right in (zip(a,b)if isinstance(a,tuple)else[(a,b)]):
        for key in left:
            assert left[key].device.type=='cuda'and torch.equal(left[key].cpu(),right[key])
assert all(v.device.type=='cpu'for v in host.data.values())
out=dict(epoch=time.time(),passed=True,ring_wrap=True,all_sample_modes_GPU=True,
    CPU_backing=True,full_precision_export_import=True,seeded_sample_values_equal=True,
    invalid_transition_and_window_masks_preserved=True,production_PT_reads=0,physics=0)
with(N/'reports/HOST_REPLAY_PARITY.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
