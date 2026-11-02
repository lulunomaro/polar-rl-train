"""N80 freshDR benchmark core/cache, NOT saved20k DR projection/resume.
Stdlib import only. Torch is injected in an ADMITTED futureworker, not source tests.
"""
from pathlib import Path
from types import MappingProxyType
import hashlib,io
PURPOSE='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
TYPED_SHA='f2b22040f90c31d133e3b006d35c868b257cc05e9445bcffdadb3b33605e1519'
TYPED_BYTES=17613845
CORE=('actor_state_dict','critic_state_dict','optimizer_state_dict','iter')
STD6=[23.26227569580078,.040672194212675095,.04223071411252022,.044310685247182846,.05442657694220543,.059898391366004944]




class WholeCheckpointIdentityCache:
    """Onewholebyte/hash/decode; completeunknownroot retained untouched.
    ExposesCORE only. D0-D7 saved20k tensors/RNG/queues are nevergiven toenv.
    """
    def __init__(self,path,torch_module,*,expected_metadata,expected_SHA,expected_bytes,read_bytes=None):
        self.t=torch_module;self.expected=expected_metadata;self.path=str(path);self.physical_byte_opens=1;self.live_actor_STD_loaded=False
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
        assert set(steps)=={self.expected['original_17Adam_step']} and int(self._root['iter'])==self.expected['original_iteration']
        lr=float(opt['param_groups'][0]['lr']);assert lr==self.expected['original_LR']
        std=actor['distribution.std_param'].tolist();assert std==self.expected['original_STD6']
        assert tuple(actor['mlp.0.weight'].shape)==(256,35) and tuple(critic['mlp.0.weight'].shape)==(256,38)
        return dict(iteration=int(self._root['iter']),Adam17=steps,LR=lr,STD6=std,actor_tensor_count=9,critic_tensor_count=8,rootkeys=list(self._root))
    def core(self,key):
        if key not in CORE:raise ValueError('N80fresh purpose doesnot expose saved20k physicalhistory toanenv')
        v=self._root[key];return MappingProxyType(v) if isinstance(v,dict) else v
    def assert_entire_root_unchanged(self):
        assert self._same(self._root,self._snapshot),'Anyoriginalcore/root/nested/savedphysicalhistory mutation is an error'
        return True
    def receipt(self):
        self.assert_entire_root_unchanged()
        return dict(purpose=PURPOSE,source_SHA=self.SHA,source_bytes=self.byte_count,physical_byte_opens=self.physical_byte_opens,SHA_calls=self.SHA_calls,decodes=self.decode_calls,metadata=self.metadata,entire_original_root_and_nested_identity_preserved=True,source_raw_bytes_retained=True,saved20k_DR_physically_applied=False,saved20k_history_sliced=False,live_actor_STD_loaded=self.live_actor_STD_loaded,critic17AdamLRiter_cached_unchanged_not_live_runner_restore=True,whole20k_savedrestore_claim=False,optimizer_updates=0)
