"""Derive only NEW SOURCE from the complete immutable V2 CLI. Never call its entry.
The future runtime plan is derived only after actual stage stream evidence; SOURCE
prepare/preflight/receipt/seal flags stay disabled. This generator does no stage IO.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'source_stage_good_expert_holdout_v2'
OLD_ENTRY_PIN=(47717,'f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d')
OLD_SEAL_PIN=(1874,'efee47debc71f12b9eed123283e08e34dcec757893cbff5532056db08657d75c')
OLD_ROOT='eb8b7b9ea06bbac56132eb0a761da35780547cc35ff9f9c1fb0166838a6b7d42'

HELPER='''def derive_materialized_runtime_plan(source_plan, source_plan_bytes, materials, observed, *, originals, preservation, required):
    """Pure evidence-to-plan derivation; no IO, approval bool, admission or native call.
    Stage owns the observed map populated by its unchanged copy/hash/fsync loop.
    The caller must also run the unchanged complete metadata_validate on this plan
    BEFORE publishing GROUP_PLAN. This helper alone is not a materialization proof.
    """
    need(type(source_plan) is dict and type(source_plan_bytes) is bytes,
         'original SOURCE plan and exact encoded bytes required')
    need(all(source_plan.get(key) is False for key in ('enabled','staged','source_native_enabled','dispatched')),
         'SOURCE plan flags must remain exactly False before materialization publication')
    encoded_source=json.dumps(source_plan,indent=2,allow_nan=False).encode()
    need(encoded_source == source_plan_bytes and len(encoded_source) <= 262144,
         'SOURCE plan bytes changed or exceed original262144 bound')
    seed=source_plan.get('seed')
    need(type(seed) is int and seed in ALLOWED_SEEDS, 'independent holdout seed required before runtime publication')
    purpose='GOOD_EXPERT_HOLDOUT_C878_S135_SEED'+str(seed)+'_V1'
    need(source_plan.get('kind') == 'GOOD_EXPERT_HOLDOUT_C878_S135_PLAN_V1'
         and source_plan.get('batch_purpose') == purpose, 'runtime publication kind/seed/purpose differs')
    group_id=source_plan.get('group_id')
    need(type(group_id) is str and group_id != ORIGINAL_GROUP_ID and str(seed) in group_id
         and re.fullmatch(r'[A-Za-z0-9_]+',group_id) is not None, 'runtime publication seed-tagged group differs')
    protocol=source_plan.get('holdout_protocol')
    need(type(protocol) is dict and protocol.get('seed') == seed and protocol.get('purpose') == purpose
         and source_plan.get('paired_reset_protocol') == paired_plan(seed), 'runtime publication cross-seed protocol differs')
    need(source_plan.get('requested_roles') == list(REQUESTED)
         and source_plan.get('deferred_roles') == [r for r in ROLES if r not in REQUESTED], 'runtime publication role subset differs')
    roles=source_plan.get('roles')
    need(type(roles) is list and len(roles) == 8 and len({r['role'] for r in roles}) == 8
         and {r['role'] for r in roles} == set(ROLES), 'runtime publication complete8 catalog required')
    need(all(r.get('seed') == seed and r.get('num_envs') == 80 and r.get('controls') == 750
             for r in roles if r['role'] in REQUESTED), 'runtime publication member seed/N80/750 differs')
    need(type(materials) is dict and materials and type(observed) is dict and set(observed) == set(materials),
         'actual stream observations must cover exactly all materialized inputs')
    for rel,(_,info) in materials.items():
        safe_relative(rel)
        need(type(info) is dict and set(info) == {'bytes','SHA'} and type(info['bytes']) is int and info['bytes'] > 0
             and is_sha(info['SHA']) and type(observed[rel]) is dict and type(observed[rel].get('bytes')) is int
             and observed[rel] == info, 'actual materialized stream identity differs: '+rel)
    required_rows=[dict(relative=rel,bytes=n,SHA=sha) for rel,(n,sha) in sorted(required.items())]
    need(len(required_rows) == 27 and preservation_digest(required_rows) == ORIGINAL_DEPENDENCY_SHA,
         'runtime publication requires the fixed complete original27 dependencies')
    need(preservation.get('installed_status') == 'ACTUAL_STREAM_HASH_VERIFIED_STATIC_FILES',
         'runtime publication needs actual stream-preservation evidence, not planned identities')
    validate_preservation(preservation,materials,originals=originals,required=required,observed=observed)
    rows=source_plan.get('worker_files')
    need(type(rows) is list and len(rows) == len({r['relative'] for r in rows}) and ALIASES <= {r['relative'] for r in rows},
         'runtime publication complete unique worker aliases required')
    for row in rows:
        rel=safe_relative(row['relative'])
        need(set(row) == {'relative','bytes','SHA'} and rel in materials
             and {k:row[k] for k in ('bytes','SHA')} == materials[rel][1], 'runtime publication worker-file binding differs: '+rel)
    runtime_plan=copy.deepcopy(source_plan)
    runtime_plan.update(enabled=True,staged=True)
    need(dict(runtime_plan,enabled=False,staged=False) == source_plan,
         'runtime publication changed more than the two existing entry flags')
    runtime_bytes=json.dumps(runtime_plan,indent=2,allow_nan=False).encode()
    need(len(runtime_bytes) <= 262144, 'runtime plan exceeds original262144 metadata bound')
    return runtime_plan,runtime_bytes
'''


def H(raw):return hashlib.sha256(raw).hexdigest()
def replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('unique complete SOURCE target absent: '+old[:100])
    return text.replace(old,new,1)
def functions(text):return {n.name:n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
def root_of(rows):return H(''.join(r['name']+'\t'+str(r['bytes'])+'\t'+r['SHA256']+'\n' for r in sorted(rows,key=lambda r:r['name'])).encode())


def main():
    raw=(OLD/'SOURCE_SEAL.json').read_bytes()
    assert (len(raw),H(raw))==OLD_SEAL_PIN
    seal=json.loads(raw);assert len(seal['files'])==9 and seal['root_SHA256']==root_of(seal['files'])==OLD_ROOT
    for row in seal['files']:
        assert Path(row['name']).name==row['name']
        member=(OLD/row['name']).read_bytes();assert (len(member),H(member))==(row['bytes'],row['SHA256'])
    raw=(OLD/'stage_good_expert_holdout_v2.py').read_bytes();assert (len(raw),H(raw))==OLD_ENTRY_PIN
    text=raw.decode('utf-8');before=functions(text)
    text=replace_once(text,'V2 fixed original27 + independently retained bytes.','V3 typed two-flag runtime publication after full verified materialization; fixed original27 + independently retained bytes.')
    text=replace_once(text,'SOURCE_DERIVATION_VERSION = 2','SOURCE_DERIVATION_VERSION = 3')
    text=replace_once(text,"def stage(prepared):",HELPER+'\n\ndef stage(prepared):')
    text=replace_once(text,"kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V2'","kind='SOURCE_GOOD_EXPERT_HOLDOUT_PREFLIGHT_ONLY_V3'")
    old="source_derivation_version=2,original_preservation=preservation_summary(prepared['original_preservation'])"
    text=replace_once(text,old,old.replace('version=2','version=3'))
    old="        put_once(root/'GROUP_PLAN.json',prepared['encoded_plan'])\n        validation=metadata_validate(prepared,actual_root=root)"
    new="""        runtime_plan,runtime_bytes=derive_materialized_runtime_plan(
            prepared['plan'],prepared['encoded_plan'],prepared['materials'],written,
            originals=prepared['originals'],preservation=preservation,required=prepared['original_dependency_files'])
        runtime_prepared=dict(prepared,plan=runtime_plan,encoded_plan=runtime_bytes)
        need(runtime_plan['group_id'] == root.name,'runtime plan/root identity differs before publication')
        validation=metadata_validate(runtime_prepared,actual_root=root)
        put_once(root/'GROUP_PLAN.json',runtime_bytes)"""
    text=replace_once(text,old,new)
    text=replace_once(text,"kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V2'","kind='SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3'")
    text=replace_once(text,'source_derivation_version=2,original_preservation=preservation_summary(preservation)',
        'source_derivation_version=3,original_preservation=preservation_summary(preservation)')
    old="            original_plan_SHA=prepared['original_plan_SHA'],model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,"
    new="            original_plan_SHA=prepared['original_plan_SHA'],GROUP_PLAN_bytes=len(runtime_bytes),GROUP_PLAN_SHA256=H(runtime_bytes),\n            model_stat_hash_open_decode=0,C_lock_SDK_GPU_GO_operations=0,"
    text=replace_once(text,old,new)
    after=functions(text);changed={name for name in before if ast.dump(before[name],include_attributes=False)!=ast.dump(after[name],include_attributes=False)}
    assert changed=={'preflight_summary','stage'} and set(after)-set(before)=={'derive_materialized_runtime_plan'}
    for name in ('prepare','main','metadata_validate','native_boundary','producer_final','put_once','validate_preservation','retain_originals','original_dependency_map'):
        assert ast.dump(before[name],include_attributes=False)==ast.dump(after[name],include_attributes=False)
    target=HERE/'stage_good_expert_holdout_v3.py';result=text.encode('utf-8')
    if target.exists():assert target.read_bytes()==result,'existing NEW SOURCE differs'
    else:
        with target.open('xb') as stream:stream.write(result)
    print(json.dumps(dict(kind='NEW_GOOD_HOLDOUT_V3_SOURCE_DERIVED_NOT_STAGE',bytes=len(result),SHA256=H(result),changed_functions=sorted(changed),unchanged_V2_functions=len(before)-len(changed),new_helper='derive_materialized_runtime_plan',runtime_plan_fields_changed=['enabled','staged'],wire_COMPLETE='STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json',actual_prepare_preflight_stage_executed=False)))

if __name__=='__main__':main()
