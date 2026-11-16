"""Offline supervised fitting probe only; 0 PPO, copied actor, no promotion.
The user message truncates before the keep ablation specification, so only
keep=1 is run. Candidate is clearly marked diagnostic and non-resumable.
"""
from common import *
import time,argparse

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fit-steps',type=int,default=0);args=ap.parse_args();assert 0<=args.fit_steps<=64
 guard();torch.manual_seed(17);rng=np.random.default_rng(17)
 actor,ck=actor_load(P/'weights/model_010m.pt');source={k:v.detach().clone()for k,v in actor.state_dict().items()};params=list(actor.parameters())
 new=np.load(T/'evidence/qualified_prewall_pool.npz');old=np.load(P/'skill_dataset/qualified_mod4_skills.npz');bank=np.load(S/'normal_bank.npz')
 nx=torch.from_numpy(new['obs'][new['prewall_mask']]);ny=torch.from_numpy(new['actions'][new['prewall_mask']]);fx=torch.from_numpy(new['obs'][new['focus_low_wheel_mask']]);fy=torch.from_numpy(new['actions'][new['focus_low_wheel_mask']]);ox=torch.from_numpy(old['obs']);oy=torch.from_numpy(old['actions']);ow=torch.from_numpy(old['sampling_weight']).float();ow/=ow.sum();bx=torch.from_numpy(bank['obs']);by=torch.from_numpy(bank['target_actions']);sem=old['semantic_id']
 def loss(x,y,w=None):
  a=(actor(x).clamp(-6,6)-y).square().sum(-1)
  return (a*w).sum()if w is not None else a.mean()
 def vector(z):return torch.cat([g.reshape(-1)for g in torch.autograd.grad(z,params)])
 def cos(a,b):
  d=float(a.norm()*b.norm());return float(a@b)/d if d else None
 batches={'new_prewall':(nx,ny,None),'new_low_wheel':(fx,fy,None),'old_skill_weighted':(ox,oy,ow),'old_contact_lift':(ox[np.isin(sem,[3,4])],oy[np.isin(sem,[3,4])],None),'old_cruise':(ox[sem==1],oy[sem==1],None),'keep_normal':(bx,by,None)}
 g={};initial={}
 for name,(x,y,w)in batches.items():
  z=loss(x,y,w);g[name]=vector(z);initial[name]=dict(samples=len(x),sum6_MSE=float(z.detach()),gradient_L2=float(g[name].norm()))
 pairs={a+'__'+b:cos(g[a],g[b])for a in g for b in g if a<b}
 combined=.4*g['new_prewall']+.6*g['old_skill_weighted'];audit=dict(model='repair10m28360ac4',initial=initial,cosines=pairs,diagnostic_combined_skill_gradient_L2=float(combined.norm()),diagnostic_combined_vs_keep_cos=cos(combined,g['keep_normal']),losses_unweighted_by_keep_lambda=True,not_actual_PPO_gradients=True,optimizer_updates=0,PPO_updates=0,source_weights_unchanged=all(torch.equal(v,source[k])for k,v in actor.state_dict().items()))
 put(T/'evidence/OFFLINE_GRADIENTS.json',audit)
 print('GRADIENTS',json.dumps(audit,ensure_ascii=False),flush=True)
 if not args.fit_steps:guard();return
 # Explicit bounded capacity/fit experiment; no PPO state or optimizer is restored.
 opt=torch.optim.Adam(params,lr=5e-5);log=[];start=time.perf_counter()
 def measure():
  with torch.no_grad():return {n:float(loss(x,y,w))for n,(x,y,w)in batches.items()}
 before=measure()
 for step in range(args.fit_steps):
  ni=torch.from_numpy(rng.integers(0,len(nx),192));oi=torch.multinomial(ow,192,replacement=True);bi=torch.from_numpy(rng.integers(0,len(bx),256))
  opt.zero_grad(set_to_none=True);ln=loss(nx[ni],ny[ni]);lo=loss(ox[oi],oy[oi]);lk=loss(bx[bi],by[bi]);total=.4*ln+.6*lo+lk;total.backward();norm=torch.nn.utils.clip_grad_norm_(params,1.);opt.step()
  if step in [0,15,31,63]or step==args.fit_steps-1:log.append(dict(optimizer_step=step+1,total_loss=float(total.detach()),new_loss=float(ln.detach()),old_loss=float(lo.detach()),keep_loss=float(lk.detach()),gradient_norm_before_clip=float(norm),fixed_bank_metrics=measure()))
 after=measure();out=T/'offline_probe_keep1';out.mkdir(exist_ok=False);torch.save(dict(actor_state_dict=actor.state_dict(),iter=ck['iter'],diagnostic_actor_only=True,PPO_updates=0,offline_optimizer_steps=args.fit_steps,source_sha256=sha(P/'weights/model_010m.pt'),optimizer_state_restored=False,approved_for_promotion=False),out/'actor_probe.pt')
 put(out/'FIT.json',dict(optimizer='fresh Adam',lr=5e-5,gradient_clip_L2=1.,optimizer_steps=args.fit_steps,PPO_updates=0,keep_lambda=1.,new_prewall_mass=.4,old_skill_mass=.6,old_pool_sha256=sha(P/'skill_dataset/qualified_mod4_skills.npz'),new_pool_sha256=sha(T/'evidence/qualified_prewall_pool.npz'),source_checkpoint_sha256=sha(P/'weights/model_010m.pt'),before=before,after=after,log=log,wall_seconds=time.perf_counter()-start,weight_path=str(out/'actor_probe.pt'),weight_sha256=sha(out/'actor_probe.pt'),only_fit_bank_not_closed_loop_success=True,keep0_ablation_not_run='Human message truncated before comparison specification'))
 print('OFFLINE_FIT',args.fit_steps,'steps','seconds',round(time.perf_counter()-start,2),'before',before,'after',after,flush=True);guard()
if __name__=='__main__':main()
