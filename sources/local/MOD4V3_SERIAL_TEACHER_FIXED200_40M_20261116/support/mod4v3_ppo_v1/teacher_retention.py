"""Same native PPO optimizer; frozen adopted c874 teacher on non-course environments."""
import ast,inspect,textwrap,types,hashlib
from pathlib import Path
import torch
from tensordict import TensorDict

class TeacherRetention:
    def __init__(self,algorithm,plan):
        self.spec=plan['teacher_retention'];path=Path(self.spec['keep_teacher'])
        self.sha=hashlib.sha256(path.read_bytes()).hexdigest()
        assert self.sha==self.spec['keep_teacher_sha256']==plan['parent_sha256']
        import copy
        self.keep_teacher=copy.deepcopy(algorithm.actor.mlp).eval()
        data=torch.load(path,map_location=next(algorithm.actor.parameters()).device,weights_only=False)
        self.keep_teacher.load_state_dict({k.removeprefix('mlp.'):v for k,v in data['actor_state_dict'].items()if k.startswith('mlp.')},strict=True)
        self.keep_teacher.requires_grad_(False)
        self.teacher_initial={k:v.detach().clone()for k,v in self.keep_teacher.state_dict().items()}
        from .native_skill_bc import NativeSkillBC
        self.skill_bc=NativeSkillBC(algorithm,plan['skill_supervision'])
        self.success_replay=None;self.window=[];self.last={};self.updates=0;self.last_sample_counts={}
    def compute(self,algorithm,observations):
        mask=observations['teacher_keep'].reshape(-1)>.5
        x=observations['policy'][mask]
        with torch.no_grad():target=self.keep_teacher(x).clamp(-6.,6.)
        loss=(algorithm.actor(TensorDict({'policy':x},batch_size=[len(x)]),stochastic_output=False).clamp(-6.,6.)-target).square().sum(-1).mean()if len(x)else next(algorithm.actor.parameters()).sum()*0.
        value=float(self.spec['lambda_bc'])*loss+self.skill_bc.compute(algorithm)
        if not bool(torch.isfinite(value)):raise ValueError('Nonfinite retention loss')
        self.window.append((float(loss.detach()),int(mask.sum())))
        self.last_sample_counts=dict(keep=int(mask.sum()),curriculum_teacher_samples=0,old_stair_anchors=0,old_high_stance_anchors=0)
        return value
    def finish_update(self):
        self.updates+=1;n=max(1,len(self.window))
        self.last=dict(teacher_keep_mse=sum(x[0]for x in self.window)/n,teacher_keep_samples=sum(x[1]for x in self.window),teacher_minibatches=len(self.window),curriculum_teacher_samples=0)
        self.last.update(self.skill_bc.finish());self.window=[];return dict(self.last)
    def summary(self):
        change=max(float((v-self.teacher_initial[k]).abs().max())for k,v in self.keep_teacher.state_dict().items())
        assert change==0. and all(p.grad is None for p in self.keep_teacher.parameters())
        return dict(spec=self.spec,keep_teacher_sha256=self.sha,keep_teacher_max_parameter_change=change,keep_teacher_no_grad=True,updates=self.updates,last=self.last,sampling=self.last_sample_counts,online_success_replay=None,native_skill_supervision=self.skill_bc.summary(),external_policy_dims=[35,6],critic_input_dim=78)

def install_teacher_retention(algorithm,plan,job):
    assert algorithm.symmetry is None and algorithm.rnd is None
    retention=TeacherRetention(algorithm,plan);original=algorithm.update.__func__
    tree=ast.parse(textwrap.dedent(inspect.getsource(original)));fn=tree.body[0];losses=returns=0
    for i,node in reversed(list(enumerate(fn.body))):
        if isinstance(node,ast.For):
            for j,item in reversed(list(enumerate(node.body))):
                if isinstance(item,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='loss'for t in item.targets):
                    node.body[j+1:j+1]=ast.parse('loss = loss + self._teacher_retention.compute(self,batch.observations)').body;losses+=1
        if isinstance(node,ast.Return)and isinstance(node.value,ast.Name)and node.value.id=='loss_dict':
            fn.body[i:i]=ast.parse('loss_dict.update(self._teacher_retention.finish_update())').body;returns+=1
    assert(losses,returns)==(1,1)
    ast.fix_missing_locations(tree);ns=dict(original.__globals__);exec(compile(tree,'<native-ppo-current-model-retention>','exec'),ns)
    algorithm._teacher_retention=retention;algorithm.update=types.MethodType(ns['update'],algorithm)
    (Path(job)/'PPO_UPDATE_WITH_TEACHER.py').write_text(ast.unparse(tree)+'\n',encoding='utf8')
    return retention
