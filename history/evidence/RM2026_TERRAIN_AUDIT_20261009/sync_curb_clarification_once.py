"""New metadata-only clarification sync. Preserve active learning/eval/budget fields.

Uses existing authorized credential environment, never embeds or prints a secret.
No remote shell, runtime, GPU, process, launch or canonical ledger operation.
"""
from pathlib import Path
import copy, hashlib, json, os, sys, time
D=Path(__file__).resolve().parent;W=D.parent;P=W/'polar-rl-train/history/plans'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
receipt=D/'RM_CURB_CLARIFICATION_METADATA_SYNCED.json'
assert not receipt.exists(), 'Already synced; do not repeat this once entry.'
v=read(P/'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json');ID=v['id']
assert sha(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
g=read(D/'RM_CURB_CLARIFICATION_GIT_RECORDED.json')
assert g['remote_main_tag_peeled_verified'] and not g['push_pending']
if not os.environ.get('RM_SSH_PASSWORD'):
    pending=dict(epoch=time.time(),metadata_sync_pending=True,reason='authorized_SSH_credential_environment_not_loaded',
        read_only_auth_attempts_completed_no_remote_mutation=True,
        production_runtime_GPU_PPO_canonical_writes=0,id=ID,Git=g)
    (D/'RM_CURB_CLARIFICATION_METADATA_SYNC_PENDING.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(metadata_sync_pending=True,remote_mutations=0,reason=pending['reason'])))
    sys.exit(0)
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
try:
    with c.open_sftp() as s:
        def get(n):return s.open(central+'/'+n).read()
        def put(n,raw,expected=None):
            if expected is not None:assert get(n)==expected, 'Concurrent metadata change; do not overwrite '+n
            path=central+'/'+n;temp=path+'.outer_curb_clarification_002_tmp'
            with s.open(temp,'wb') as f:f.write(raw)
            if expected is not None:assert get(n)==expected, 'Concurrent metadata change before rename: '+n
            s.posix_rename(temp,path);assert get(n)==raw
        names=['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_PLAN_ANNOTATIONS.md']
        before={n:get(n) for n in names}
        a=json.loads(before['PLAN_APPROVAL.json']);t=json.loads(before['EXECUTION_TRACKS.json']);q=json.loads(before['MOE_PLAN_EXECUTION_CURRENT.json'])
        assert a['approved'] and a['approved_plan_sha256']==v['master_sha256'] and a['S8_authorized'] is False
        ref=dict(id=ID,document='MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md',json='MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json',
            document_sha256=sha(P/'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md'),json_sha256=sha(P/'MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json'),
            human_request=v['human_request'],annotation_only=True,supersedes_interpretation_only=v['supersedes_interpretation_only'],
            applies_to=['S3 E1 terrain traversal','S7 E1/E2 terrain spin'],current_training_evaluation_budget_unchanged=True,new_budget_seconds=0,Git=g)
        olda=copy.deepcopy(a);oldt=copy.deepcopy(t);oldq=copy.deepcopy(q)
        for obj,key in [(a,'plan_annotations'),(t,'curriculum_annotations')]:
            if ID in obj.get(key,{}):assert obj[key][ID]==ref
            else:obj.setdefault(key,{})[ID]=ref
        refs=q.setdefault('curriculum_annotation_refs',[])
        existing=[x for x in refs if x.get('id')==ID]
        if existing:assert existing==[ref]
        else:refs.append(ref)
        # Removing only this new ref must reconstruct every original current field.
        for obj,old,key in [(a,olda,'plan_annotations'),(t,oldt,'curriculum_annotations')]:
            check=copy.deepcopy(obj);prior=copy.deepcopy(old)
            check.get(key,{}).pop(ID,None);prior.get(key,{}).pop(ID,None)
            if not check.get(key):check.pop(key,None)
            if not prior.get(key):prior.pop(key,None)
            assert check==prior
        check=copy.deepcopy(q);prior=copy.deepcopy(oldq)
        for obj in [check,prior]:
            if 'curriculum_annotation_refs' in obj:
                obj['curriculum_annotation_refs']=[x for x in obj['curriculum_annotation_refs'] if x.get('id')!=ID]
                if not obj['curriculum_annotation_refs']:obj.pop('curriculum_annotation_refs')
        assert check==prior
        for n,raw in before.items():
            backup=n.rsplit('.',1)[0]+'_BEFORE_OUTER_CURB_CLARIFICATION_002.'+n.rsplit('.',1)[1]
            try:s.stat(central+'/'+backup)
            except FileNotFoundError:put(backup,raw)
        for n in ['MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md','MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.json']:
            put(n,(P/n).read_bytes())
        put('RM_CURB_CLARIFICATION_GIT_RECORDED.json',json.dumps(g,ensure_ascii=False,indent=2).encode('utf8'))
        idx=before['MOD4_PLAN_ANNOTATIONS.md']
        if ID.encode() not in idx:
            idx+=('\n\n优先澄清 '+ID+'：读取MOD4_RM_OUTER_CURB_ROUGH_CLARIFICATION.md/json。用户箭头是左右外缘连续坎，原part383内侧49.56mm倒角位置解释被替代；旧测量/raw/trial及spin排除保持。RM起伏名义70/240mm，当前浅课不覆盖；未来自己的geometry/contact/reset准入，不据标注部署/毕业。\n').encode('utf8')
        handoff=before['LATEST_HANDOFF.md']
        if ID.encode() not in handoff:
            handoff+=('\n\n## 人类箭头明确澄清中心岛外缘坎（2026-10-09）\n'+ID+'优先于001位置解释。用户目标为左右外缘连续150mm条带及过渡，非part383内侧49.56mm/45度倒角。给定CAD有限样本内侧44.24或92-94mm，中心外侧平台约149.93mm，部分过渡约200.07mm；不能统一50mm/45度，必须按真实邻接面和完整轮迹准入。part280/281更符合前哨站底座位置/尺寸，不能误叫同一路坎。起伏原曲面当地法向70mm、峰距240.64mm，规则名义70/240；当前0-1cm起伏非RM范围。S3/E1与S7读取本澄清md/json，原spin排除/首≤5cm≤10度/S8边界保留。主SHA不变，本次仅计划metadata，不改当前训练/eval/budget/runtime/GPU/PPO/canonical，不复活93/94或MuJoCo。旧证据保留。\n').encode('utf8')
        updates={'PLAN_APPROVAL.json':a,'EXECUTION_TRACKS.json':t,'MOE_PLAN_EXECUTION_CURRENT.json':q}
        # Check all originals before first index mutation, then check each again immediately before its write.
        assert all(get(n)==raw for n,raw in before.items())
        for n,obj in updates.items():put(n,json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8'),before[n])
        put('MOD4_PLAN_ANNOTATIONS.md',idx,before['MOD4_PLAN_ANNOTATIONS.md'])
        put('LATEST_HANDOFF.md',handoff,before['LATEST_HANDOFF.md'])
        assert json.loads(get('PLAN_APPROVAL.json'))['plan_annotations'][ID]==ref
        assert json.loads(get('EXECUTION_TRACKS.json'))['curriculum_annotations'][ID]==ref
        proof=dict(epoch=time.time(),metadata_only=True,id=ID,master_SHA_unchanged=v['master_sha256'],
            learning_evaluation_budget_metadata_unchanged=True,production_runtime_GPU_PPO_canonical_writes=0,
            compare_before_write_protected=True,Git=g)
        raw=json.dumps(proof,ensure_ascii=False,indent=2).encode('utf8')
        put(receipt.name,raw);receipt.write_bytes(raw)
        print(json.dumps(dict(metadata_synced=True,id=ID,current_training_unchanged=True)))
finally:c.close()
