"""Create an isolated same-G2 continuation after complete123 paired behavior; no GPU."""
from pathlib import Path
import ast,json,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
L=W/'MOD4_E1_G2_LEARNING_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
assert not (R/'PREPARED.json').exists()
review_path=sorted((L/'reports').glob('OBSERVATION_123_REVIEW_*.json'))[-1]
review=json.loads(review_path.read_bytes());assert review['review_complete'] and not review['pending']
assert review['own']['checkpoint']['sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b'
assert review['own']['actual_updates']==6 and len(review['own']['unique_completed_segment'])==1
assert set(review['retention'])=={'flat','spin','world'} and review['terrain']['base_review']['ordinary']==0
assert review['terrain']['groups']['forward']['complete_envs']==27 and review['terrain']['groups']['reverse']['complete_envs']==26
assert review['retention']['world']['candidate']['passed']==62
assert review['retention']['spin']['candidate']['pure4pi'][0]['passed']==8 and review['retention']['spin']['candidate']['pure4pi'][1]['passed']==5
assert max(x['error'] for x in review['retention']['flat']['candidate']['straight'])<.05
raw=(L/'payload/supervise_e1_G2_reviewed_short_observation.py').read_bytes();tree=ast.parse(raw.decode())
replacements={
'verify':'''def verify():
    verify_original_records(s.q,D)
    a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
    f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(Path('/home/egde/rl_candidates/MOD4_S3_E1_G2_REVIEWED_20261010/reports/SOURCE_FREEZE.json'))['sha256']
    assert len(old)==329 and len(f)==330 and all(f[n]==h for n,h in old.items())
    for n,h in f.items():assert s.q.base.sha(D/n)==h,n
    b=read(R/'MATCHED_123_REVIEW.json');v=read(R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json')
    assert b['review_complete'] and not b['pending'] and b['own']['checkpoint']['sha256']==v['source']['sha256']
    assert v['actual_behavior_review_complete'] and v['source_count']==329 and v['snapshot_count']==62 and v['finite_tensors']==96
    assert read(R/'G2_TARGET_CPU_PASSED.json')['passed'] and read(R/'E1_COMPLETE_PPO_PREFLIGHT_PASSED.json')['weights_discarded']
    pkg=read(R/'G2_BEHAVIOR_PACKAGE_READY.json')['runtime'];assert s.q.base.sha(Path(pkg['path']))==pkg['sha256']=='c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271'
''',
'source':'''def source():
    row=read(R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json');p=Path(row['source']['path'])
    assert row['actual_behavior_review_complete'] and row['source']['sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b' and s.q.base.sha(p)==row['source']['sha256']
    assert fullsave(p)['finite_tensors']==96
    return p
''',
'wait_existing':'''def wait_existing():
    old=Path('/home/egde/rl_candidates/MOD4_S3_E1_G2_REVIEWED_20261010/reports');state=read(old/'E1_STATE.json');row=read(old/'e1_G2_reviewed_observation_PASSED.json')
    assert state['phase']=='E1_G2_reviewed_saved_review_ready' and state['child'] is None and (old/'E1_REVIEW_READY.json').exists() and not (old/'E1_ATTENTION.json').exists()
    for locator in (state['owner'],read(old/'E1_GUARDIAN_STARTED.json'),dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=72362884)):
        v=identity(locator['pid']);assert not v or v['state']=='Z' or v['start_ticks']!=locator['start_ticks']
    assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
    assert len([v for v in read(s.q.ctl.CANONICAL)['completed_segments'] if v['pid']==row['own_PID_bound_receipt']['pid']])==1
''',
'main':'''def main():
    import torch;torch.set_num_threads(1)
    assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source()
    s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
    before=s.q.ctl.CANONICAL.read_bytes()
    write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),old_parent_guardian_children_exited=True,two_original_locks_held=True,active_empty=True,new_budget_seconds=0,complete_four_case_source_review=True))
    write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),source=fullsave(init),matched_G2_observation_seconds=900,same_G2_geometry=True,no_new_native_PPO_clock_tests=True,new_budget_seconds=0))
    assert before==s.q.ctl.CANONICAL.read_bytes()
    with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
    write('E1_GUARDIAN_STARTED.json',identity(g.pid))
    init,row=train(init,20000,10000,min(900,s.left()),'e1_G2_matched_continuation',False)
    startup=read(Path(row['run'])/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json')
    assert startup['terrain_state_restored_exact'] and not startup['explicitly_new_E1_terrain'] and not startup['explicit_G0_to_G2_geometry_transition'] and startup['static_geometry_identity_preserved']
    publish(init,'124-e1-g2-matched-continuation')
    write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(init),all_courses_finished=False,same_G2_short_observation_complete=True,needs_actual_G2_route_and_old_skill_review=True,automatic_more_PPO_disallowed=True))
    phase('E1_G2_matched_continuation_saved_review_ready',child=None)
'''
}
for i,node in enumerate(tree.body):
    if isinstance(node,ast.FunctionDef) and node.name in replacements:tree.body[i]=ast.parse(replacements.pop(node.name)).body[0]
assert not replacements
class Labels(ast.NodeTransformer):
    def visit_Constant(self,n):
        if n.value=='G0_to_G2_20mm':n.value='same_G2_after_complete_matched_behavior_review'
        if isinstance(n.value,str) and '5min observation' in n.value:n.value=n.value.replace('5min observation','15min same-G2 matched observation')
        return n
tree=Labels().visit(tree);ast.fix_missing_locations(tree)
payload=D/'payload';payload.mkdir(exist_ok=True);out=payload/'supervise_e1_G2_matched_continuation.py';out.write_text(ast.unparse(tree)+'\n',encoding='utf8');compile(out.read_text(encoding='utf8'),str(out),'exec')
selection=dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-SOURCE-01',source=review['own']['checkpoint'],actual_behavior_review_complete=True,source_count=329,snapshot_count=62,finite_tensors=96,own_PID_bound_receipt=review['own']['own_PID_bound_receipt'],unique_completed_segment=review['own']['unique_completed_segment'],review_path=str(review_path.resolve()),review_sha256=H(review_path.read_bytes()),paired_cases=list(json.loads(Path(review['collection']).read_bytes())['cases']),decision='No material old-skill collapse after6updates; permit only one same20mm900s observation, review again before more PPO.',world63_to62_and_cross_residuals_retained=True,negative4pi5of8_residuals_retained=True,reverse26of27_incomplete_after_support_prefix_retained=True,no_permanent_anti_forgetting_or_E1_RM_graduation=True,new_budget_seconds=0)
(R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json').write_text(json.dumps(selection,indent=2),encoding='utf8')
(R/'MATCHED_123_REVIEW.json').write_bytes(review_path.read_bytes())
(R/'PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-PREPARE-01',original_controller_sha256=H(raw),new_controller_sha256=H(out.read_bytes()),same329_sources_preserved=True,new_controller_only=True,no_GPU_or_PPO=True,new_budget_seconds=0),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(D),selection=selection['source'],source_review_complete=True,new_controller_only=True)))
