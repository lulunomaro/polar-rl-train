"""New-payload CPU source/data admission. API: check(B, key).

B is the actual h1 or recovery payload root, key is 'h1' or 'recovery'.
No Isaac import, GPU API, policy inference, scene, reset, rollout or budget write.
Recovery checks read this NEW payload bank once, then reuse those same bytes in
memory for normal/inference constructor comparison. This is not a live SDK test.
"""
import os,ast,base64
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,importlib.util,io,json,sys
from pathlib import Path
from unittest import mock

EXPECTED={
 'h1':{
  'h1_production_control_prefix_trace_v1.py':'4bb1353f28f55fca48d12de6cd3e7979bf1c6a751cabd5aaabe9ed36772a08f1',
  'h1_lifetime_goal_counter_v1.py':'c4448cb9971efc356aaae16506731065988cc515daf868730be0e0f8f93c2f1c',
  'reference_sources/actual79c_counter_original_bytes.txt':'05e57b768f8e2069c2cf9af6c1ce031341af16b8c00110fbebe03bd2706f2a01',
  'sampling_trace_npz_lossless_v1.py':'ce2335df8ac300fb52659d69fd41df82dd8a58964adc990448709cd332d8057f'},
 'recovery':{
  'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':'7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d',
  'job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py':'ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a'}}
BASE={
 'h1':{'h1_production_control_prefix_trace_v1.py':'d14f69cd14a1297f558ea7f7df83f17f735cec2f99da037f3b2d623a2f590dd6'},
 'recovery':{'job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py':'0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd'}}
BANK_SHA='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
BANK_BYTES=32022178
PERMUTATION_SHA='e1b5a6ddc0d0bbd9115387fb366e5ccabd05c035395f9d91b7aba0f2a07bb119'


def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def _original_geometry(torch,points,recipe):
    # Original source0f8fd2... place_declared_fall per-selected arithmetic.
    device=points.device;degrees=torch.tensor([-90.,-60.,-30.,30.,60.,90.],device=device)
    angle=torch.where(recipe<12,degrees[recipe.clamp(max=11)%6],0.)*torch.pi/180
    quat=torch.zeros((len(recipe),4),device=device)
    quat[torch.arange(len(recipe),device=device),torch.where(recipe<6,0,1)]=torch.sin(angle/2);quat[:,3]=torch.cos(angle/2)
    minimum=torch.empty(len(recipe),device=device)
    for first in range(0,len(recipe),128):
        last=min(first+128,len(recipe));v=quat[first:last,None,:3];p=points[None].expand(last-first,-1,-1)
        rot=p+2*torch.cross(v.expand_as(p),torch.cross(v.expand_as(p),p,dim=-1)+quat[first:last,None,3:4]*p,dim=-1)
        minimum[first:last]=rot[:,:,2].amin(-1)
    return quat,minimum,(1+torch.cos(angle))/2


def validate_V8_trace_reward_publication_only(path):
    from h1_lifetime_goal_counter_v1 import canonical_V8_trace_tree
    tree=canonical_V8_trace_tree(path)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1ControlPrefixTrace')
    install=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='install')
    step=next(n for n in install.body if isinstance(n,ast.FunctionDef) and n.name=='step')
    pub=ast.parse('self.env._h1_sampled_actions_for_reward=raw').body[0]
    clear=ast.parse('self.env._h1_sampled_actions_for_reward=None').body[0]
    matches=[n for n in step.body if ast.dump(n)==ast.dump(pub)]
    assert len(matches)==1
    step.body.remove(matches[0])
    enabled=ast.parse('self.env._h1_sampled_excess_training_active=True').body[0]
    flags=[n for n in step.body if ast.dump(n)==ast.dump(enabled)];assert len(flags)==1;step.body.remove(flags[0])
    tries=[n for n in step.body if isinstance(n,ast.Try)];assert len(tries)==1
    disabled=ast.parse('self.env._h1_sampled_excess_training_active=False').body[0]
    assert len(tries[0].finalbody)==2 and ast.dump(tries[0].finalbody[0])==ast.dump(clear) and ast.dump(tries[0].finalbody[1])==ast.dump(disabled)
    tries[0].finalbody=[]
    original=base64.b64decode('IiIiUmVhZC1vbmx5IHNhbXBsaW5nL2NvbnRyb2wgZXZpZGVuY2UgYW5kIGltbXV0YWJsZSBwcmUtdXBkYXRlIGZ1bGwgY2hlY2twb2ludHMuCgpOZXZlciByZWNvbXB1dGVzIG9ic2VydmF0aW9ucywgc2FtcGxlcyBhY3Rpb25zLCBhZHZhbmNlcyBSTkcsIGNoYW5nZXMgZm9yY2VzIG9yIGlucHV0cy4KQ29udHJvbC1yYXRlIHRyYWluaW5nIHJlY29yZHMgYXJlIG5vdCBmdWxsIHBoeXNpY2FsLWNhbGxiYWNrIHJlcGxheSBldmlkZW5jZS4KIiIiCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aAppbXBvcnQgdGltZSxqc29uLGhhc2hsaWIsdHJhY2ViYWNrCmltcG9ydCB0b3JjaCxudW1weSBhcyBucApmcm9tIHNhbXBsaW5nX3RyYWNlX25wel9sb3NzbGVzc192MSBpbXBvcnQgd3JpdGVfdHJhY2Vfcm93c19ucHosc2hhMjU2X2ZpbGUKZGVmIEgocCk6cmV0dXJuIHNoYTI1Nl9maWxlKHApCmRlZiBwdXQocCx2KToKIHA9UGF0aChwKTtxPXAud2l0aF9zdWZmaXgocC5zdWZmaXgrJy5wYXJ0aWFsJyk7cS53cml0ZV90ZXh0KGpzb24uZHVtcHModixpbmRlbnQ9MikpO3EucmVwbGFjZShwKQpjbGFzcyBIMUNvbnRyb2xQcmVmaXhUcmFjZToKIGRlZiBfX2luaXRfXyhzZWxmLHJ1bm5lcixmb2xkZXIpOgogIHNlbGYucnVubmVyPXJ1bm5lcjtzZWxmLnZlYz1ydW5uZXIuZW52O3NlbGYuZW52PXNlbGYudmVjLnVud3JhcHBlZDtzZWxmLmZvbGRlcj1QYXRoKGZvbGRlcik7c2VsZi5mb2xkZXIubWtkaXIoKTtzZWxmLnJvd3M9W107c2VsZi5pbmRleD1bXTtzZWxmLnNvdXJjZV9tb2RlbHM9W107c2VsZi5vYnNlcnZlZD1Ob25lO3NlbGYuZnJhbWU9Tm9uZTtzZWxmLnRlcm1zPWxpc3Qoc2VsZi5lbnYucmV3YXJkX21hbmFnZXIuX3Rlcm1fbmFtZXMpO3NlbGYudG90YWw9MAogZGVmIGluc3RhbGwoc2VsZik6CiAgb2xkX2FjdD1zZWxmLnJ1bm5lci5hbGcuYWN0O29sZF9zdGVwPXNlbGYudmVjLnN0ZXA7b2xkX3Rlcm09c2VsZi5lbnYudGVybWluYXRpb25fbWFuYWdlci5jb21wdXRlO29sZF9yZXdhcmQ9c2VsZi5lbnYucmV3YXJkX21hbmFnZXIuY29tcHV0ZQogIGRlZiBhY3Qob2JzLCphcmdzLCoqa3dhcmdzKToKICAgaWYgbm90IHNlbGYucm93czoKICAgIHA9c2VsZi5mb2xkZXIvKCdwcmV1cGRhdGVfZnVsbHNvdXJjZV8nK3N0cihsZW4oc2VsZi5zb3VyY2VfbW9kZWxzKSkrJy5wdCcpO3RtcD1wLndpdGhfc3VmZml4KCcucHQucGFydGlhbCcpO3NlbGYucnVubmVyLnNhdmUoc3RyKHRtcCkpO3RtcC5yZXBsYWNlKHApO3NlbGYuc291cmNlX21vZGVscy5hcHBlbmQoZGljdChwYXRoPXN0cihwKSxieXRlcz1wLnN0YXQoKS5zdF9zaXplLFNIQT1IKHApLGJlZm9yZV9jb250cm9sPXNlbGYudG90YWwsbm9fb3B0aW1pemVyX2NhbGw9VHJ1ZSkpCiAgIHNlbGYub2JzZXJ2ZWQ9ZGljdChwb2xpY3kzNT1vYnNbJ3BvbGljeSddLmRldGFjaCgpLmNsb25lKCksY3JpdGljMzg9b2JzWydjcml0aWMnXS5kZXRhY2goKS5jbG9uZSgpKTtyZXR1cm4gb2xkX2FjdChvYnMsKmFyZ3MsKiprd2FyZ3MpCiAgZGVmIHRlcm0oKmFyZ3MsKiprd2FyZ3MpOgogICB2YWx1ZT1vbGRfdGVybSgqYXJncywqKmt3YXJncykKICAgaW1wb3J0IG1vZDRfdGFzayBhcyB0YXNrCiAgIGU9c2VsZi5lbnY7cj1lLnNjZW5lWydyb2JvdCddO3A9ZS5oMV9waGFzZTtzZWxmLmZyYW1lPWRpY3Qocm9vdDEzPXIuZGF0YS5yb290X3N0YXRlX3cuZGV0YWNoKCkuY2xvbmUoKSxxMzA9ci5kYXRhLmpvaW50X3Bvcy5kZXRhY2goKS5jbG9uZSgpLGpvaW50X3ZlbG9jaXR5PXIuZGF0YS5qb2ludF92ZWwuZGV0YWNoKCkuY2xvbmUoKSxhcHBsaWVkX3RvcnF1ZT1yLmRhdGEuYXBwbGllZF90b3JxdWUuZGV0YWNoKCkuY2xvbmUoKSxleGVjdXRlZDY9ZS5hY3Rpb25fbWFuYWdlci5hY3Rpb24uZGV0YWNoKCkuY2xvbmUoKSxoaXN0b3J5NW1zPWUuX2ludGVncmF0ZWRfY29udGFjdC5oaXN0b3J5LmRldGFjaCgpLmNsb25lKCksaW1wdWxzZT1lLl9pbnRlZ3JhdGVkX2NvbnRhY3QuaW1wdWxzZS5kZXRhY2goKS5jbG9uZSgpLGNsb3N1cmU9dG9yY2guc3RhY2sobGlzdCh0YXNrLmNsb3N1cmVfZXJyb3JzKGUpLnZhbHVlcygpKSkuYW1heCgwKSxtaW1pYz10b3JjaC5zdGFjayhsaXN0KHRhc2subWltaWNfZXJyb3JzKGUpLnZhbHVlcygpKSkuYW1heCgwKSxwdWJsaWNfcmVxdWVzdD1wLnJlcXVlc3RfZm9yX2FjdGlvbi5kZXRhY2goKS5jbG9uZSgpLGV2ZW50X2V4cGVjdGVkPXAuZXZlbnRfY29udHJvbC5kZXRhY2goKS5jbG9uZSgpLHByb2dyZXNzX2V4cGVjdGVkPXAucHJvZ3Jlc3NfY29udHJvbC5kZXRhY2goKS5jbG9uZSgpLHByb2dyZXNzX3BlYWs9cC5wZWFrLmRldGFjaCgpLmNsb25lKCkscHJvZ3Jlc3NfcGFpZD1wLmdvYWwucHJvZ3Jlc3MuZGV0YWNoKCkuY2xvbmUoKSxzdGVwX3N0YWJsZV90aWNrcz1wLmdvYWwuc3RhYmxlX3RpY2tzLmRldGFjaCgpLmNsb25lKCksc3RlcF9zdWNjZXNzPXAuZ29hbC5zdWNjZXNzLmRldGFjaCgpLmNsb25lKCksc3RlcF93aGVlbF9jcm9zc2VkPXAuY3Jvc3NlZC5kZXRhY2goKS5jbG9uZSgpLHRha2VvZmZfY291bnQ9cC50YWtlb2ZmX2NvdW50LmRldGFjaCgpLmNsb25lKCksbGFuZGluZ19jb3VudD1wLmxhbmRpbmdfY291bnQuZGV0YWNoKCkuY2xvbmUoKSxyZWNvdmVyeV9jb3VudD1wLnJlY292ZXJ5X2NvdW50LmRldGFjaCgpLmNsb25lKCksZXBpc29kZT1lLl9zZW5zb3JfbWlsZC5lcGlzb2RlLmRldGFjaCgpLmNsb25lKCkpO3JldHVybiB2YWx1ZQogIGRlZiByZXdhcmQoZHQsKmFyZ3MsKiprd2FyZ3MpOgogICByZXN1bHQ9b2xkX3Jld2FyZChkdCwqYXJncywqKmt3YXJncykKICAgaWYgc2VsZi5mcmFtZSBpcyBub3QgTm9uZTpzZWxmLmZyYW1lWydyZXdhcmRfdGVybV9jb250cmlidXRpb24nXT1zZWxmLmVudi5yZXdhcmRfbWFuYWdlci5fc3RlcF9yZXdhcmQuZGV0YWNoKCkuY2xvbmUoKSpzZWxmLmVudi5oMV9yZXdhcmRfcmVhZG91dF9zY2FsZQogICByZXR1cm4gcmVzdWx0CiAgZGVmIHN0ZXAoYWN0aW9ucyk6CiAgIHJhdz1hY3Rpb25zLmRldGFjaCgpLmNsb25lKCk7c2VsZi5mcmFtZT1Ob25lCiAgIHRyeToKICAgIG91dHB1dD1vbGRfc3RlcChhY3Rpb25zKTtvYnMscmV3YXJkLGRvbmUsaW5mbz1vdXRwdXQ7YXNzZXJ0IHNlbGYuZnJhbWUgaXMgbm90IE5vbmUgYW5kIHNlbGYub2JzZXJ2ZWQgaXMgbm90IE5vbmU7cm93PXsqKnNlbGYub2JzZXJ2ZWQsKipzZWxmLmZyYW1lLCdyYXdfc2FtcGxlZDYnOnJhdywndG90YWxfcmV3YXJkJzpyZXdhcmQuZGV0YWNoKCkuY2xvbmUoKSwnZG9uZSc6ZG9uZS5kZXRhY2goKS5jbG9uZSgpfTtzZWxmLnJvd3MuYXBwZW5kKHtrOnYuZGV0YWNoKCkuY3B1KCkubnVtcHkoKS5jb3B5KCkgZm9yIGssdiBpbiByb3cuaXRlbXMoKX0pO3NlbGYudG90YWwrPTEKICAgIGlmIGxlbihzZWxmLnJvd3MpPT0yNDpzZWxmLnBlcnNpc3QoKQogICAgcmV0dXJuIG91dHB1dAogICBleGNlcHQgQmFzZUV4Y2VwdGlvbjoKICAgIHB1dChzZWxmLmZvbGRlci8nQUNUVUFMX1NURVBfT1JJR0lOQUxfRVJST1IuanNvbicsZGljdChlcG9jaD10aW1lLnRpbWUoKSxlcnJvcj10cmFjZWJhY2suZm9ybWF0X2V4YygpLGNvbXBsZXRlZF9jb250cm9sX3Jvd3M9c2VsZi50b3RhbCxmYWlsZWRfY3VycmVudF9jb250cm9sX25vdF9jbGFpbWVkX2NvbXBsZXRlPVRydWUpKTtzZWxmLnBlcnNpc3QoKTtyYWlzZQogIHNlbGYucnVubmVyLmFsZy5hY3Q9YWN0O3NlbGYudmVjLnN0ZXA9c3RlcDtzZWxmLmVudi50ZXJtaW5hdGlvbl9tYW5hZ2VyLmNvbXB1dGU9dGVybTtzZWxmLmVudi5yZXdhcmRfbWFuYWdlci5jb21wdXRlPXJld2FyZAogZGVmIHBlcnNpc3Qoc2VsZik6CiAgaWYgc2VsZi5yb3dzOgogICBwPXNlbGYuZm9sZGVyLygnY29udHJvbF9wcmVmaXhfJytzdHIobGVuKHNlbGYuaW5kZXgpKSsnLm5weicpO3RtcD1wLndpdGhfc3VmZml4KCcubnB6LnBhcnRpYWwnKQogICB3aXRoIHRtcC5vcGVuKCd4YicpIGFzIGY6d3JpdGVfdHJhY2Vfcm93c19ucHooZixzZWxmLnJvd3MsY29tcHJlc3NsZXZlbD0xKQogICB0bXAucmVwbGFjZShwKTtzZWxmLmluZGV4LmFwcGVuZChkaWN0KHBhdGg9c3RyKHApLGJ5dGVzPXAuc3RhdCgpLnN0X3NpemUsU0hBPUgocCksY29udHJvbHM9bGVuKHNlbGYucm93cykscHJldXBkYXRlX3NvdXJjZT1zZWxmLnNvdXJjZV9tb2RlbHNbbGVuKHNlbGYuaW5kZXgpXSkpO3NlbGYucm93cy5jbGVhcigpCiAgcHV0KHNlbGYuZm9sZGVyLydDT05UUk9MX1ZBTElEX1BSRUZJWF9JTkRFWF9BQ1RVQUwuanNvbicsZGljdChlcG9jaD10aW1lLnRpbWUoKSxjb250cm9scz1zZWxmLnRvdGFsLGluZGV4PXNlbGYuaW5kZXgscHJldXBkYXRlX2Z1bGxfc291cmNlcz1zZWxmLnNvdXJjZV9tb2RlbHMscmV3YXJkX3Rlcm1zPXNlbGYudGVybXMscGh5c2ljYWxfY2FsbGJhY2tfcmVwbGF5PUZhbHNlLG5vX2V4dHJhX2FjdG9yX2ZvcndhcmRfb3JfUk5HX2RyYXc9VHJ1ZSxyYXdfc2FtcGxlZF9hY3Rpb25fYW5kX2FjdHVhbGNsaXBfZXhlY3V0aW9uX3NlcGFyYXRlPVRydWUsYWxsX3N1Y2Nlc3NfYW5kX2ZhaWxlZF9jb250cm9sX3ByZWZpeGVzX3JldGFpbmVkPVRydWUpKQoKZnJvbSBoMV9wcmVmaXhfcGFpcl9yZXRlbnRpb25fdjEgaW1wb3J0IHdyYXBfdHJhY2VfcGVyc2lzdApIMUNvbnRyb2xQcmVmaXhUcmFjZS5wZXJzaXN0PXdyYXBfdHJhY2VfcGVyc2lzdChIMUNvbnRyb2xQcmVmaXhUcmFjZS5wZXJzaXN0KQo=')
    assert hashlib.sha256(original).hexdigest()=='a24011df3a43e580fa15037791c30e9f8dacdaf4d0f6b9dd62b00276798414bd'
    assert ast.dump(tree)==ast.dump(ast.parse(original.decode('utf8')))
    return dict(passed=True,only_existing_raw_clone_training_scope_and_finally_clear=True,original_step_forwarding_persist_retention_fullSHA_and_errors_AST_exact=True)

def check(B,key):
    """Return JSON-serializable receipt or raise on any source/data mismatch."""
    import numpy as np
    B=Path(B).resolve();key='recovery' if key=='e3' else key
    if key not in EXPECTED:raise ValueError('Expected h1 or recovery payload root')
    actual={rel:H(B/rel) for rel in EXPECTED[key]}
    if actual!=EXPECTED[key]:raise RuntimeError('Installed acceleration file SHA mismatch')
    result=dict(passed=False,status='checking_CPU_only',key=key,base=str(B),
                expected_base_SHA=BASE[key],candidate_SHA=actual,
                exact_source_allowlist=list(EXPECTED[key]),no_GPU_API_SDK_scene_policy_physics_or_canonical=True,
                actual_live_SDK_joint_order_or_CUDA_outputs_not_claimed=True)
    if key=='h1':
        result['V8_reward_publication_AST']=validate_V8_trace_reward_publication_only(B/'h1_production_control_prefix_trace_v1.py')
        from h1_lifetime_goal_counter_v1 import installed_counter_CPU_checks,installed_landing_journal_CPU_checks
        result['lifetime_goal_diagnostic_CPU']=installed_counter_CPU_checks(B)
        result['landing_event_journal_CPU']=installed_landing_journal_CPU_checks(B)
        helper=_module('owned_acceleration_npz_CPU_check',B/'sampling_trace_npz_lossless_v1.py')
        rng=np.random.Generator(np.random.PCG64(20261025))
        arrays=dict(policy35=rng.standard_normal((24,3,35),dtype=np.float32),
                    q30=rng.standard_normal((24,3,30),dtype=np.float32),
                    history5ms=rng.standard_normal((24,3,3,2,3),dtype=np.float32),
                    counts=np.arange(72,dtype=np.int64).reshape(24,3),
                    flags=np.zeros((24,3),dtype=np.bool_),
                    special=np.array([0,0x80000000,0x7fc00001,0xffc00002,0x7f800000,0xff800000],dtype=np.uint32).view(np.float32))
        buf=io.BytesIO();helper.write_arrays_npz(buf,arrays,compresslevel=1);buf.seek(0)
        with np.load(buf,allow_pickle=False) as loaded:
            assert loaded.files==list(arrays)
            assert all(loaded[k].dtype==v.dtype and loaded[k].shape==v.shape and loaded[k].tobytes()==v.tobytes() for k,v in arrays.items())
        rows=[{k:v[i] for k,v in arrays.items() if k!='special'} for i in range(24)]
        buf=io.BytesIO();helper.write_trace_rows_npz(buf,rows,compresslevel=1);buf.seek(0)
        with np.load(buf,allow_pickle=False) as loaded:
            assert all(loaded[k].dtype==v.dtype and loaded[k].shape==v.shape and loaded[k].tobytes()==v.tobytes() for k,v in arrays.items() if k!='special')
        assert helper.sha256_file(B/'sampling_trace_npz_lossless_v1.py')==actual['sampling_trace_npz_lossless_v1.py']
        result.update(passed=True,status='CPU_exact_installed_sources_and_lossless_fixture_passed',
                      NPZ_array_bytes_dtype_shape_exact=True,full_SHA_preserved=True,
                      actual_persist_retention_evidence='V1 actual persist/retention/fault CPU report retained in preparation archive; exact canonical trace AST retains original persist/retention plus reviewed raw-reward publication only')
        return result
    import torch
    runtime=B/'job0/runtime/isaac/mod4';permpath=runtime/'e1_rough_reset_tensor.py'
    if H(permpath)!=PERMUTATION_SHA:raise RuntimeError('Original joint_permutation source changed')
    _module('e1_rough_reset_tensor',permpath)
    cachemod=_module('owned_acceleration_e3_cache_CPU_check',runtime/'e3_reset_bank_cache_v1.py')
    bankpath=runtime/'MOD4_RESET_COLLISION_BANK.npz'
    st=bankpath.stat()
    if st.st_size!=BANK_BYTES:raise RuntimeError('New-payload bank size mismatch')
    raw=bankpath.read_bytes()  # Exactly one byte read of the NEW payload bank.
    if hashlib.sha256(raw).hexdigest()!=BANK_SHA:raise RuntimeError('New-payload bank SHA mismatch')
    after=bankpath.stat()
    if (st.st_size,st.st_mtime_ns,st.st_ino,st.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ino,after.st_ctime_ns):
        raise RuntimeError('Bank changed during new-payload CPU validation')
    with np.load(io.BytesIO(raw),allow_pickle=False) as bank:
        names=list(bank['joint_names']);pick=int(np.argmin(abs(bank['root_height']-.25)))
        points=torch.as_tensor(bank['points_root'][pick],device='cpu',dtype=torch.float32)
        bank_q=bank['q'][pick].copy()
    before_rng=torch.random.get_rng_state().clone();cpu_threads=torch.get_num_threads();torch.set_num_threads(1)
    old_read=Path.read_bytes;memory_read_requests=0
    def cached_read(path):
        nonlocal memory_read_requests
        if path.resolve()==bankpath.resolve():memory_read_requests+=1;return raw
        return old_read(path)
    cases=[]
    try:
        with mock.patch.object(Path,'read_bytes',cached_read):
            for robot_names in (names,list(reversed(names))):
                recipe=torch.arange(520,device='cpu',dtype=torch.long)%13
                expected_geometry=_original_geometry(torch,points,recipe)
                perm=[names.index(x) for x in robot_names]
                expected_q=torch.as_tensor(bank_q[perm],device='cpu',dtype=torch.float32)[None].repeat(len(recipe),1)
                for inference_ctor in (False,True):
                    with torch.inference_mode(inference_ctor):cache=cachemod.E3ResetBankCache(bankpath,robot_names,'cpu')
                    with torch.inference_mode():values=cache.selected_geometry(recipe,robot_names)
                    assert all(a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b) for a,b in zip(values,(expected_q,*expected_geometry)))
                    cache.validate(robot_names)
                    assert cache.pick==pick and cache.source_sha==BANK_SHA
                    assert all(value._version>=0 for value in (cache._q,cache._quat,cache._minimum,cache._initial))
                    cases.append(dict(joint_order='bank' if robot_names==names else 'reverse',inference_constructor=inference_ctor,
                                      inference_selection=True,selected=520,original_per_selected_geometry_and_q_exact=True))
        assert torch.equal(before_rng,torch.random.get_rng_state())
    finally:torch.set_num_threads(cpu_threads)
    result.update(passed=True,status='CPU_exact_installed_sources_and_fresh_bank_geometry_context_passed',
                  bank_SHA=BANK_SHA,bank_bytes=BANK_BYTES,fresh_bank_physical_read_count=1,
                  constructor_memory_read_requests=memory_read_requests,points_per_pose=len(points),selected_bank_pose=pick,
                  normal_and_inference_cases=cases,global_CPU_torch_RNG_unchanged=True,
                  original_margin_m=.0001,selected_reset_SDK_calls_unchanged_by_exact_source_AST=True,
                  real_CUDA_or_live_SDK_validation_remaining=True)
    return result


if __name__=='__main__':
    import argparse,time
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--key',choices=['h1','recovery'],required=True);parser.add_argument('--report')
    args=parser.parse_args();receipt=check(args.root,args.key);receipt['epoch']=time.time()
    if args.report:
        with Path(args.report).open('x',encoding='utf8') as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt))
