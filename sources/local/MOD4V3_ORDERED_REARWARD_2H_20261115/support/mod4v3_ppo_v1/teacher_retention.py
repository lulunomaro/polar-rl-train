"""Persistent teacher supervision balanced by high stance and stair phase/angle."""
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
        dataset_path=Path(self.spec['dataset']);self.dataset_sha256=hashlib.sha256(dataset_path.read_bytes()).hexdigest();assert self.dataset_sha256==self.spec['dataset_sha256']
        data=torch.load(dataset_path,map_location='cpu',weights_only=False)
        assert data['metadata']['teacher_sha256']==self.spec['stair_teacher_sha256']
        assert data['policy'].shape[1]==35 and data['actions'].shape==(len(data['policy']),6)
        assert bool((data['endpoint']>=150).all()),'Specialist preparation actions must not supervise high stance'
        self.demo_obs=data['policy'].float().to(self.device);self.demo_actions=data['actions'].float().to(self.device)
        self.seed_groups={}
        for phase in (0,1):
            for angle in range(5):
                for engine in (0,1):
                    idx=((data['phase'].long()==phase)&(data['angle_group']==angle)&(data['source_engine']==engine)).nonzero().flatten()
                    if len(idx):self.seed_groups[(phase,angle,engine)]=idx.to(self.device)
        self.seed_sampled={str(k):0 for k in self.seed_groups}
        high_path=Path(self.spec['high_stance_dataset']);self.high_dataset_sha256=hashlib.sha256(high_path.read_bytes()).hexdigest();assert self.high_dataset_sha256==self.spec['high_stance_dataset_sha256']
        high=torch.load(high_path,map_location='cpu',weights_only=False)
        assert high['metadata']['target_teacher_sha256']==self.spec['keep_teacher_sha256']
        self.high_obs=high['policy'].float().to(self.device);self.high_actions=high['actions'].float().to(self.device)
        for value in [self.demo_obs,self.demo_actions,self.high_obs,self.high_actions]:assert len(value)>0 and bool(torch.isfinite(value).all())
        self.dataset_metadata=data['metadata'];self.teacher_initial={k:v.detach().clone() for k,v in self.keep_teacher.state_dict().items()}
        reference=plan['rearward_reference'];reference_path=Path(reference['dataset']);self.reference_sha256=hashlib.sha256(reference_path.read_bytes()).hexdigest();assert self.reference_sha256==reference['sha256']
        data=torch.load(reference_path,map_location='cpu',weights_only=False);self.reference_metadata=data['metadata'];assert data['policy'].shape[1]==35 and data['actions'].shape[1]==6
        self.rear_obs=data['policy'].float().to(self.device);self.rear_actions=data['actions'].float().to(self.device);self.rear_spec=reference;self.rear_groups=[(data['phase']==i).nonzero().flatten().to(self.device)for i in range(4)];assert all(len(x)>0 for x in self.rear_groups)
        assert len(self.rear_obs)>0 and bool(torch.isfinite(self.rear_obs).all()) and bool(torch.isfinite(self.rear_actions).all())
        self.window=[];self.last={};self.total_updates=0;self.success_replay=None;self.last_sample_counts={}

    def sample_seed(self,count):
        chosen=[]
        for phase in (0,1):
            requested=count//2+(count%2 if phase==1 else 0)
            angles=[a for a in range(5) if any(k[0]==phase and k[1]==a for k in self.seed_groups)]
            assert angles,'Both approach and first-to-second-step phases need real successful frames'
            for ai,angle in enumerate(angles):
                number=requested//len(angles)+int(ai<requested%len(angles))
                engines=[e for e in (0,1) if (phase,angle,e) in self.seed_groups]
                for ei,engine in enumerate(engines):
                    size=number//len(engines)+int(ei<number%len(engines))
                    if not size:continue
                    group=(phase,angle,engine);bank=self.seed_groups[group]
                    idx=bank[torch.randint(len(bank),(size,),device=self.device)]
                    chosen.append(idx);self.seed_sampled[str(group)]+=size
        idx=torch.cat(chosen);assert len(idx)==count
        return self.demo_obs[idx],self.demo_actions[idx]

    def compute(self,algorithm,observations):
        mask=observations['teacher_keep'].reshape(-1)>.5
        high_mask=observations['teacher_high_stance'].reshape(-1)>.5
        zero=observations['policy'].sum()*0.;keep=zero
        def predict(x):return algorithm.actor(TensorDict({'policy':x},batch_size=[len(x)]),stochastic_output=False).clamp(-6,6)
        if bool(mask.any()):
            x=observations['policy'][mask];predicted=predict(x)
            with torch.no_grad():target=self.keep_teacher(x).clamp(-6,6)
            keep=(predicted-target).square().sum(-1).mean()
        anchor_count=int(self.spec['high_stance_minibatch']);hi=torch.randint(len(self.high_obs),(anchor_count,),device=self.device)
        high_anchor=(predict(self.high_obs[hi])[:,:4]-self.high_actions[hi,:4]).square().sum(-1).mean()
        high=high_anchor
        if bool(high_mask.any()):
            x=observations['policy'][high_mask];predicted=predict(x)
            with torch.no_grad():target=self.keep_teacher(x).clamp(-6,6)
            high_live=(predicted[:,:4]-target[:,:4]).square().sum(-1).mean()
            high=.5*(high_anchor+high_live)
        count=seed_count=new_count=0;seed_loss=new_loss=stair=zero
        if float(self.spec['stair_fraction'])>0.:
            count=min(int(self.spec['demo_minibatch']),len(self.demo_obs));online=self.success_replay
            new_count=int(round(count*float(online.spec['new_fraction']))) if online is not None and sum(online.counts)>0 else 0
            seed_count=count-new_count;x,target=self.sample_seed(seed_count)
            seed_loss=(predict(x)-target).square().sum(-1).mean();new_loss=zero
            if new_count:
                x,target=online.sample(new_count);new_loss=(predict(x)-target).square().sum(-1).mean()
            stair=(seed_loss*seed_count+new_loss*new_count)/count
        auxiliary=float(self.spec['lambda_bc'])*(float(self.spec['keep_fraction'])*keep+float(self.spec['stair_fraction'])*stair)+float(self.spec['lambda_high_stance'])*high
        ref_count=int(self.rear_spec['minibatch']);ref_idx=torch.cat([group[torch.randint(len(group),(ref_count//4+int(i<ref_count%4),),device=self.device)]for i,group in enumerate(self.rear_groups)])
        rear_loss=(predict(self.rear_obs[ref_idx])[:,:4]-self.rear_actions[ref_idx,:4]).square().sum(-1).mean()
        auxiliary=auxiliary+float(self.rear_spec['lambda_legs'])*rear_loss
        if not bool(torch.isfinite(auxiliary)):raise ValueError('Nonfinite teacher retention loss')
        self.last_sample_counts=dict(keep=int(mask.sum()),high_live=int(high_mask.sum()),high_anchor=anchor_count,stair_seed=seed_count,stair_online=new_count,seed_cumulative_by_phase_angle_engine=dict(self.seed_sampled),specialist_preparation_samples=0)
        self.window.append((float(keep.detach()),float(stair.detach()),float(auxiliary.detach()),int(mask.sum()),count,float(seed_loss.detach()),float(new_loss.detach()),new_count,float(high.detach()),int(high_mask.sum()),anchor_count,float(rear_loss.detach())))
        return auxiliary

    def finish_update(self):
        assert self.window
        n=len(self.window);self.total_updates+=1
        names={0:'teacher_keep_mse',1:'teacher_stair_mse',2:'teacher_aux_loss',5:'teacher_seed_mse',6:'teacher_new_success_mse',8:'teacher_high_stance_legs_mse',11:'rearward_reference_legs_mse'}
        self.last={name:sum(x[i] for x in self.window)/n for i,name in names.items()}
        self.last.update(teacher_keep_samples=sum(x[3] for x in self.window),teacher_stair_samples=sum(x[4] for x in self.window),teacher_minibatches=n,teacher_new_success_samples=sum(x[7] for x in self.window),teacher_high_live_samples=sum(x[9] for x in self.window),teacher_high_anchor_samples=sum(x[10] for x in self.window))
        self.window=[];return dict(self.last)

    def summary(self):
        change=max(float((v-self.teacher_initial[k]).abs().max()) for k,v in self.keep_teacher.state_dict().items())
        assert change==0. and all(p.grad is None for p in self.keep_teacher.parameters())
        return dict(rearward_reference=dict(sha256=self.reference_sha256,metadata=self.reference_metadata,lambda_legs=self.rear_spec['lambda_legs'],legs_only=True),online_success_replay=self.success_replay.summary() if self.success_replay is not None else None,spec=self.spec,dataset_sha256=self.dataset_sha256,high_dataset_sha256=self.high_dataset_sha256,dataset_metadata=self.dataset_metadata,last=self.last,updates=self.total_updates,keep_teacher_max_parameter_change=change,keep_teacher_no_grad=True,algorithm='Native PPO plus task-averaged retention, separate high-stance leg anchors, movement-only phase/angle/engine balanced successes',external_policy_dims=[35,6],critic_input_dim=78,sampling=self.last_sample_counts)

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
