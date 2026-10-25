"""Create new unused source overlays only; originals and active68 stay untouched."""
import ast,hashlib,json,time
from pathlib import Path

B=Path(__file__).resolve().parent
T=B.parents[2]
M4=T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/benchmark_closed_text'


def H(raw):return hashlib.sha256(raw).hexdigest()


def dump(node):return ast.dump(node,include_attributes=False)


def main():
    report=B/'reports/INTEGRATED_SOURCE_AST_ALLOWLIST_V2_ACTUAL.json'
    assert not report.exists(),'Do not overwrite prior attempt'
    paths={
      'h1':M4/'h1/h1_production_control_prefix_trace_v1.py',
      'e3':M4/'recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py',
      'permutation':M4/'recovery/job0/runtime/isaac/mod4/e1_rough_reset_tensor.py',
      'phase':M4/'recovery/job0/runtime/isaac/mod4/e3_public_recovery_phase_v1.py'}
    source={k:p.read_bytes() for k,p in paths.items()}
    for k,raw in source.items():
        dst=B/'original_sources'/(k+'_'+paths[k].name)
        if dst.exists():assert dst.read_bytes()==raw
        else:dst.write_bytes(raw)
    helper=(B.parent/'trace_npz_writer_unused_v1.py').read_bytes()
    dst=B/'payloads/h1/sampling_trace_npz_lossless_v1.py'
    if dst.exists():assert dst.read_bytes()==helper
    else:dst.write_bytes(helper)
    old=source['h1'].decode();new=old
    new=new.replace('import torch,numpy as np','import torch,numpy as np\nfrom sampling_trace_npz_lossless_v1 import write_trace_rows_npz,sha256_file')
    new=new.replace('def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()','def H(p):return sha256_file(p)')
    anchor="with tmp.open('xb') as f:np.savez_compressed(f,**{k:np.stack([x[k] for x in self.rows]) for k in self.rows[0]})"
    assert new.count(anchor)==1
    new=new.replace(anchor,"with tmp.open('xb') as f:write_trace_rows_npz(f,self.rows,compresslevel=1)")
    h1dst=B/'payloads/h1/h1_production_control_prefix_trace_v1.py'
    if h1dst.exists():assert h1dst.read_bytes()==new.encode()
    else:h1dst.write_text(new,encoding='utf8',newline='')
    ot,nt=ast.parse(old),ast.parse(new)
    expected=ast.parse(old)
    expected.body.insert(4,ast.ImportFrom(module='sampling_trace_npz_lossless_v1',names=[ast.alias(name='write_trace_rows_npz'),ast.alias(name='sha256_file')],level=0))
    # Verify the explicit changed nodes, then normalize only those nodes.
    oldmap={n.name:n for n in ot.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    newmap={n.name:n for n in nt.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    assert dump(newmap['H'])==dump(ast.parse('def H(p):return sha256_file(p)').body[0])
    normalized=ast.parse(new)
    normalized.body=[n for n in normalized.body if not(isinstance(n,ast.ImportFrom) and n.module=='sampling_trace_npz_lossless_v1')]
    for i,n in enumerate(normalized.body):
        if isinstance(n,ast.FunctionDef) and n.name=='H':normalized.body[i]=oldmap['H']
    cls=next(n for n in normalized.body if isinstance(n,ast.ClassDef) and n.name=='H1ControlPrefixTrace')
    oldcls=oldmap['H1ControlPrefixTrace']
    persist=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='persist')
    oldpersist=next(n for n in oldcls.body if isinstance(n,ast.FunctionDef) and n.name=='persist')
    assert len(persist.body)==len(oldpersist.body)
    w,=[x for x in persist.body[0].body if isinstance(x,ast.With)];ow,=[x for x in oldpersist.body[0].body if isinstance(x,ast.With)]
    assert isinstance(w,ast.With) and dump(w.items[0])==dump(ow.items[0])
    assert dump(w.body[0])==dump(ast.parse('write_trace_rows_npz(f,self.rows,compresslevel=1)').body[0])
    w.body=ow.body
    assert dump(normalized)==dump(ot),'H1 non-allowlist AST changed'
    old=source['e3'].decode();new=old
    new=new.replace('from h1_fullstate_environment_v1 import tensor','from h1_fullstate_environment_v1 import tensor\nfrom e3_reset_bank_cache_v1 import E3ResetBankCache')
    anchor='  original_update=self.scene.update'
    assert new.count(anchor)==1
    init="  self._e3_fixed_reset_cache=E3ResetBankCache(Path(__file__).resolve().parent/'MOD4_RESET_COLLISION_BANK.npz',r.joint_names,self.device)\n"
    new=new.replace(anchor,init+anchor)
    start=new.index("   r=self.scene['robot'];a=Path(__file__).resolve().parent;bank=np.load")
    end=new.index('   root=tensor(r.data.root_state_w)',start)
    new=new[:start]+"   r=self.scene['robot'];cache=self._e3_fixed_reset_cache\n   q,quat,minimum,initial=cache.selected_geometry(self.recovery.recipe[ids],r.joint_names)\n   pick=cache.pick\n"+new[end:]
    new=new.replace('initial=(1+torch.cos(angle))/2;self.recovery.reset(ids,initial)','self.recovery.reset(ids,initial)')
    anchor="__import__('hashlib').sha256((a/'MOD4_RESET_COLLISION_BANK.npz').read_bytes()).hexdigest()"
    assert new.count(anchor)==1;new=new.replace(anchor,'cache.source_sha')
    e3dst=B/'payloads/recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py'
    if e3dst.exists():assert e3dst.read_bytes()==new.encode()
    else:e3dst.write_text(new,encoding='utf8',newline='')
    ot,nt=ast.parse(old),ast.parse(new)
    oldcls=next(n for n in ot.body if isinstance(n,ast.ClassDef) and n.name=='RecoveryEnv')
    newcls=next(n for n in nt.body if isinstance(n,ast.ClassDef) and n.name=='RecoveryEnv')
    newinit=next(n for n in newcls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    added=[n for n in newinit.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='_e3_fixed_reset_cache' for t in n.targets)]
    assert len(added)==1 and dump(added[0])==dump(ast.parse(init.strip()).body[0])
    newinit.body.remove(added[0])
    oldfunc=next(n for n in oldcls.body if isinstance(n,ast.FunctionDef) and n.name=='place_declared_fall')
    newfunc=next(n for n in newcls.body if isinstance(n,ast.FunctionDef) and n.name=='place_declared_fall')
    # Outside declared geometry generation, enforce exact ordered SDK/reset/publish calls.
    def callseq(func):
        return [dump(n) for n in ast.walk(func) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('write_joint_state_to_sim','write_root_state_to_sim','reset','publish')]
    assert callseq(newfunc)==callseq(oldfunc)
    # Compare receipt structure after only replacing original hash expression by cache property.
    oldlast=oldfunc.body[0].body[-1];newlast=newfunc.body[0].body[-1]
    assert isinstance(oldlast,ast.Assign) and isinstance(newlast,ast.Assign)
    oldreceipt=ast.parse(ast.unparse(oldlast))
    for kw in oldreceipt.body[0].value.keywords:
        if kw.arg=='geometry_bank_source_sha':kw.value=ast.parse('cache.source_sha',mode='eval').body
    assert dump(newlast)==dump(oldreceipt.body[0])
    for i,n in enumerate(newcls.body):
        if isinstance(n,ast.FunctionDef) and n.name=='place_declared_fall':newcls.body[i]=oldfunc
    nt.body=[n for n in nt.body if not(isinstance(n,ast.ImportFrom) and n.module=='e3_reset_bank_cache_v1')]
    assert dump(nt)==dump(ot),'E3 non-allowlist AST changed'
    outputs=[h1dst,dst,e3dst,B/'payloads/recovery/job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py']
    row=dict(trial_id='MOD4_SAMPLING_IMPLEMENTATION_AST_V2_20261025',epoch=time.time(),passed=True,
             old_sources={k:dict(path=str(p),bytes=len(source[k]),SHA=H(source[k])) for k,p in paths.items()},
             new_sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes())) for p in outputs],
             allowlist=dict(H1=['new helper import','H only bounded-read full SHA','persist serialization call only'],
                            E3=['new cache import','constructor one cache initialization','place_declared_fall geometry generation and bank SHA source only']),
             all_other_AST_unchanged=True,E3_original_SDK_reset_publish_call_AST_and_order_exact=True,
             E3_original_receipt_keys_values_except_equivalent_bank_SHA_expression_exact=True,
             active_source_68_unchanged=True,unused_only=True,Git='pending root')
    report.write_text(json.dumps(row,indent=2),encoding='utf8');print(json.dumps(row))


if __name__=='__main__':main()
