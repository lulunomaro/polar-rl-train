"""Training-only persistent teacher guidance inside the native RSL5 PPO update."""
from pathlib import Path
import ast,copy,hashlib,inspect,json,textwrap,types
import torch
from tensordict import TensorDict

class TeacherRetention:
    def __init__(self,algorithm,plan):
        self.spec=dict(plan['teacher_retention']);self.device=algorithm.device
        teacher_path=Path(self.spec['keep_teacher']);assert hashlib.sha256(teacher_path.read_bytes()).hexdigest()==self.spec['keep_teacher_sha256']
        teacher=torch.load(teacher_path,map_location=self.device,weights_only=False)
        self.keep_teacher=copy.deepcopy(algorithm.actor.mlp).to(self.device).eval()
        self.keep_teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in teacher['actor_state_dict'].items() if k.startswith('mlp.')},strict=True)
        self.keep_teacher.requires_grad_(False)
        assert all(not p.requires_grad for p in self.keep_teacher.parameters())
        dataset_path=Path(self.spec['dataset']);self.dataset_sha256=hashlib.sha256(dataset_path.read_bytes()).hexdigest()
        data=torch.load(dataset_path,map_location='cpu',weights_only=False)
        assert data['metadata']['teacher_sha256']==self.spec['stair_teacher_sha256']
        assert data['policy'].ndim==2 and data['policy'].shape[1]==35 and data['actions'].shape==(len(data['policy']),6)
        assert len(data['policy'])>0,'No successful native demonstration states collected'
        self.demo_obs=data['policy'].float().to(self.device);self.demo_actions=data['actions'].float().to(self.device)
        assert bool(torch.isfinite(self.demo_obs).all()) and bool(torch.isfinite(self.demo_actions).all())
        self.dataset_metadata=data['metadata'];self.teacher_initial={k:v.detach().clone() for k,v in self.keep_teacher.state_dict().items()}
        self.window=[];self.last={};self.total_updates=0;self.success_replay=None

    def compute(self,algorithm,observations):
        mask=observations['teacher_keep'].reshape(-1)>.5
        zero=observations['policy'].sum()*0.
        keep=zero
        if bool(mask.any()):
            x=observations['policy'][mask]
            predicted=algorithm.actor(TensorDict({'policy':x},batch_size=[len(x)]),stochastic_output=False).clamp(-6,6)
            with torch.no_grad():target=self.keep_teacher(x).clamp(-6,6)
            keep=(predicted-target).square().sum(-1).mean()
        count=min(int(self.spec['demo_minibatch']),len(self.demo_obs))
        online=self.success_replay
        new_count=int(round(count*float(online.spec['new_fraction']))) if online is not None and sum(online.counts)>0 else 0
        seed_count=count-new_count
        chosen=torch.randint(len(self.demo_obs),(seed_count,),device=self.device)
        x=self.demo_obs[chosen]
        predicted=algorithm.actor(TensorDict({'policy':x},batch_size=[seed_count]),stochastic_output=False).clamp(-6,6)
        seed_loss=(predicted-self.demo_actions[chosen]).square().sum(-1).mean()
        new_loss=zero
        if new_count:
            x,target=online.sample(new_count)
            predicted=algorithm.actor(TensorDict({'policy':x},batch_size=[new_count]),stochastic_output=False).clamp(-6,6)
            new_loss=(predicted-target).square().sum(-1).mean()
        stair=(seed_loss*seed_count+new_loss*new_count)/count
        auxiliary=float(self.spec['lambda_bc'])*(float(self.spec['keep_fraction'])*keep+float(self.spec['stair_fraction'])*stair)
        if not bool(torch.isfinite(auxiliary)):raise ValueError('Nonfinite teacher retention loss')
        self.window.append((float(keep.detach()),float(stair.detach()),float(auxiliary.detach()),int(mask.sum()),count,float(seed_loss.detach()),float(new_loss.detach()),new_count))
        return auxiliary

    def finish_update(self):
        assert self.window
        n=len(self.window);self.total_updates+=1
        self.last={
            'teacher_keep_mse':sum(x[0] for x in self.window)/n,
            'teacher_stair_mse':sum(x[1] for x in self.window)/n,
            'teacher_aux_loss':sum(x[2] for x in self.window)/n,
            'teacher_keep_samples':sum(x[3] for x in self.window),
            'teacher_stair_samples':sum(x[4] for x in self.window),
            'teacher_minibatches':n,
            'teacher_seed_mse':sum(x[5] for x in self.window)/n,
            'teacher_new_success_mse':sum(x[6] for x in self.window)/n,
            'teacher_new_success_samples':sum(x[7] for x in self.window),
        }
        self.window=[]
        return dict(self.last)

    def summary(self):
        change=max(float((v-self.teacher_initial[k]).abs().max()) for k,v in self.keep_teacher.state_dict().items())
        assert change==0. and all(p.grad is None for p in self.keep_teacher.parameters())
        return dict(online_success_replay=self.success_replay.summary() if self.success_replay is not None else None,spec=self.spec,dataset_sha256=self.dataset_sha256,dataset_metadata=self.dataset_metadata,last=self.last,updates=self.total_updates,keep_teacher_max_parameter_change=change,keep_teacher_no_grad=True,algorithm='Native PPO backward plus persistent teacher action-MSE',external_policy_dims=[35,6],critic_input_dim=78)

def install_teacher_retention(algorithm,plan,job):
    assert algorithm.symmetry is None and algorithm.rnd is None
    retention=TeacherRetention(algorithm,plan);original=algorithm.update.__func__;source=textwrap.dedent(inspect.getsource(original));tree=ast.parse(source);fn=tree.body[0]
    losses=returns=0
    for i,n in reversed(list(enumerate(fn.body))):
        if isinstance(n,ast.For):
            for j,item in reversed(list(enumerate(n.body))):
                if isinstance(item,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='loss' for t in item.targets):
                    n.body[j+1:j+1]=ast.parse('loss = loss + self._teacher_retention.compute(self, batch.observations)').body;losses+=1
        if isinstance(n,ast.Return) and isinstance(n.value,ast.Name) and n.value.id=='loss_dict':
            fn.body[i:i]=ast.parse('loss_dict.update(self._teacher_retention.finish_update())').body;returns+=1
    assert(losses,returns)==(1,1),(losses,returns)
    ast.fix_missing_locations(tree);namespace=dict(original.__globals__);exec(compile(tree,'<native-rsl5-ppo-with-teacher-retention>','exec'),namespace)
    algorithm._teacher_retention=retention;algorithm.update=types.MethodType(namespace['update'],algorithm)
    (Path(job)/'PPO_UPDATE_WITH_TEACHER.py').write_text(ast.unparse(tree)+'\n',encoding='utf8')
    return retention
