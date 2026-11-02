"""N80 freshDR benchmark core/cache, NOT saved20k DR projection/resume.
Stdlib import only. Torch is injected in an ADMITTED futureworker, not source tests.
"""
from pathlib import Path
from types import MappingProxyType
import hashlib,io
PURPOSE='SLOPE135_N80_FRESH_FULLDR_SKILL15S_NOT_FULL20K_RESUME'
TYPED_SHA='f2b22040f90c31d133e3b006d35c868b257cc05e9445bcffdadb3b33605e1519'
TYPED_BYTES=17613845
CORE=('actor_state_dict','critic_state_dict','optimizer_state_dict','iter')
STD6=[23.26227569580078,.040672194212675095,.04223071411252022,.044310685247182846,.05442657694220543,.059898391366004944]


def require_scope(task):
    assert task['purpose']==PURPOSE
    assert task['num_envs']==80 and task['controls']==750 and task['physics_callbacks']==6000 and task['feedback_samples']==1500
    assert task['seed']==20260928 and task['source_SHA']==TYPED_SHA and task['source_bytes']==TYPED_BYTES
    assert task['physics_dt']==.0025 and task['policy_hz']==50 and task['feedback_hz']==100 and task['TGS']==[32,4]
    assert task['closure_m']==.01 and task['mimic_rad']==.01 and task['gas_N']==400 and task['stiffness_N_m']==2000
    assert task['fresh_fullDR_cohort'] is True and task['saved20k_DR_physically_applied'] is False
    assert task['state_projection_or_slicing'] is False and task['whole20k_savedrestore_claim'] is False
    assert task['optimizer_updates']==0 and task['new_training_GO']==False
    return True


class WholeCheckpointIdentityCache:
    """Onewholebyte/hash/decode; completeunknownroot retained untouched.
    ExposesCORE only. D0-D7 saved20k tensors/RNG/queues are nevergiven toenv.
    """
    def __init__(self,path,torch_module,*,expected_SHA=TYPED_SHA,expected_bytes=TYPED_BYTES,read_bytes=None):
        self.t=torch_module;self.path=str(path);self.physical_byte_opens=1
        self.raw=(read_bytes or (lambda p:Path(p).read_bytes()))(path)
        self.byte_count=len(self.raw);assert self.byte_count==expected_bytes
        self.SHA=hashlib.sha256(self.raw).hexdigest();self.SHA_calls=1;assert self.SHA==expected_SHA
        self.decode_calls=1;self._root=self.t.load(io.BytesIO(self.raw),map_location='cpu',weights_only=False)
        assert type(self._root) is dict and all(k in self._root for k in CORE)
        self._snapshot=self._freeze(self._root);self.metadata=self._metadata()
    def _freeze(self,x):
        if self.t.is_tensor(x):return ('tensor',x,x.detach().clone(),str(x.dtype),tuple(x.shape))
        if type(x) is dict:return ('dict',x,[(k,self._freeze(v)) for k,v in x.items()])
        if type(x) in (list,tuple):return (type(x).__name__,x,[self._freeze(v) for v in x])
        if x is None or type(x) in (str,int,float,bool,bytes):return ('scalar',x)
        return ('opaque_identity_only',x,type(x).__module__+'.'+type(x).__qualname__)
    def _same(self,x,s):
        kind=s[0]
        if kind=='tensor':return x is s[1] and str(x.dtype)==s[3] and tuple(x.shape)==s[4] and self.t.equal(x,s[2])
        if kind=='dict':return x is s[1] and list(x)==[k for k,_ in s[2]] and all(self._same(x[k],y) for k,y in s[2])
        if kind in ('list','tuple'):return x is s[1] and len(x)==len(s[2]) and all(self._same(a,b) for a,b in zip(x,s[2]))
        if kind=='scalar':return type(x) is type(s[1]) and x==s[1]
        return x is s[1]
    def _metadata(self):
        actor=self._root['actor_state_dict'];critic=self._root['critic_state_dict'];opt=self._root['optimizer_state_dict']
        assert len(actor)==9 and len(critic)==8 and len(opt['state'])==17
        steps=[int(v['step'].item()) if self.t.is_tensor(v['step']) else int(v['step']) for v in opt['state'].values()]
        assert set(steps)=={642980} and int(self._root['iter'])==32069
        lr=float(opt['param_groups'][0]['lr']);assert lr==6.666666666666667e-05
        std=actor['distribution.std_param'].tolist();assert std==STD6
        assert tuple(actor['mlp.0.weight'].shape)==(256,35) and tuple(critic['mlp.0.weight'].shape)==(256,38)
        return dict(iteration=32069,Adam17=steps,LR=lr,STD6=std,actor_tensor_count=9,critic_tensor_count=8,rootkeys=list(self._root))
    def core(self,key):
        if key not in CORE:raise ValueError('N80fresh purpose doesnot expose saved20k physicalhistory toanenv')
        v=self._root[key];return MappingProxyType(v) if isinstance(v,dict) else v
    def assert_entire_root_unchanged(self):
        assert self._same(self._root,self._snapshot),'Anyoriginalcore/root/nested/savedphysicalhistory mutation is an error'
        return True
    def receipt(self):
        self.assert_entire_root_unchanged()
        return dict(purpose=PURPOSE,source_SHA=self.SHA,source_bytes=self.byte_count,physical_byte_opens=self.physical_byte_opens,SHA_calls=self.SHA_calls,decodes=self.decode_calls,metadata=self.metadata,entire_original_root_and_nested_identity_preserved=True,source_raw_bytes_retained=True,saved20k_DR_physically_applied=False,saved20k_history_sliced=False,live_actor_STD_loaded=True,critic17AdamLRiter_cached_unchanged_not_live_runner_restore=True,whole20k_savedrestore_claim=False,optimizer_updates=0)


class OriginalSlopePredicate:
    """review_slope135.audit scalar streamingsemantics, notnewaggregatepassrate."""
    def __init__(self,n=80):
        assert n==80;self.n=n;self.first_failure=[None]*n;self.segments=[{} for _ in range(n)]
    def observe(self,control,episode,u2,support2,terminated):
        assert len(episode)==len(u2)==len(support2)==len(terminated)==80
        for i in range(80):
            if terminated[i] and self.first_failure[i] is None:self.first_failure[i]=control
            if self.first_failure[i] is not None:continue
            if i%3==2:continue
            s=self.segments[i].setdefault(int(episode[i]),dict(first=control,last=control,before=[],after=[]));s['last']=control
            before=max(u2[i]) < -1.2 if i%3==0 else min(u2[i])>1.2
            after=min(u2[i]) > 1.2 if i%3==0 else max(u2[i])< -1.2
            if before and all(support2[i]):s['before'].append(control)
            if after and all(support2[i]):s['after'].append(control)
    def finish(self):
        rows=[]
        for i in range(80):
            segments=[dict(episode=ep,first_control=s['first'],last_control=s['last'],original1N_contact_confirmed=bool(s['before'] and s['after'] and min(s['before'])<max(s['after']))) for ep,s in self.segments[i].items()]
            rows.append(dict(env=i,group=('ascending','descending','stand')[i%3],first_ordinary_failure_control=self.first_failure[i],contact_confirmed=any(s['original1N_contact_confirmed'] for s in segments),crossing_required=i%3!=2,segments=segments))
        groups={g:dict(environments=sum(x['group']==g for x in rows),contact_confirmed_envs=sum(x['group']==g and x['contact_confirmed'] for x in rows)) for g in ('ascending','descending','stand')}
        return dict(groups=groups,rows=rows,standing_not_required_to_cross=True,original_per_env_sameepisode_beforefirstordinary_predicate=True,no_new_aggregate_graduation_rate=True,skill_graduation='PARENT_REVIEW_COUNTS_AND_ORIGINAL_SCOPE_NO_AUTO_GRADUATION')


def physical_support_from_eight(force_z,physics_dt=.0025,control_dt=.02):
    assert len(force_z)==8 and physics_dt==.0025 and control_dt==.02
    return sum(max(0.,float(x)) for x in force_z)*physics_dt/control_dt>1.
