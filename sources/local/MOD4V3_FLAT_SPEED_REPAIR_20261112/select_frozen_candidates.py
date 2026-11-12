"""Provisional candidate selection after all checkpoints and consumers close."""
from pathlib import Path
import json,hashlib,torch,subprocess,sys
T=Path(__file__).resolve().parent;R=T.parents[2]
assert (T/'training_round_full_actor/SAFE_CLOSED.json').exists()
assert (T/'training_round_full_actor/model_final.pt').exists()
subprocess.run([sys.executable,'-X','utf8','-B',str(T/'score_replays.py')],check=True)
rows=json.loads((T/'evidence/REPLAY_SCOREBOARD.json').read_text())['rows'];choices=[r for r in rows if r['label'].startswith('full_') and r['resets']==0];complete=[r for r in choices if r['retention_passed']==r['retention_requested']];pool=complete or choices
best=min(pool,key=lambda r:(r['forward_requested']-r['forward_passed'],r['forward_max_error'],r['forward_mean_error']));latest=T/'training_round_full_actor/model_final.pt';parent=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt';models={'parent':str(parent),'candidate':str(Path(best['model']).resolve())}
def fingerprint(p):
 d=torch.load(p,map_location='cpu',weights_only=False)['actor_state_dict'];h=hashlib.sha256()
 for k in sorted(d):
  if k.startswith('mlp.'):h.update(k.encode());h.update(d[k].contiguous().numpy().tobytes())
 return h.hexdigest()
if fingerprint(latest)!=fingerprint(best['model']):models['latest']=str(latest)
(T/'NATIVE_MODELS.json').write_text(json.dumps(models,indent=2));selection=dict(provisional=True,selected=best,original_mature_parent_retained=True,selection='fixed nominal MuJoCo forward pass count,worsterror,meanerror after retention filter; native+stair+dense checks still required',native_models=models,latest_actor_same_as_candidate=(len(models)==2))
(T/'evidence/PROVISIONAL_SELECTION.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2));print(json.dumps(selection,ensure_ascii=False),flush=True)
