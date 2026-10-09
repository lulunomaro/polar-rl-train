"""New human-requested curriculum metadata sync; no shell/process/ledger access."""
from pathlib import Path
import copy,hashlib,json,sys,time
D=Path(__file__).resolve().parent;W=D.parent;P=W/'polar-rl-train/history/plans';R=D/'reports'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf8'))
receipt=R/'RM_TERRAIN_CURRICULUM_METADATA_SYNCED.json';assert not receipt.exists(),'Once already executed'
v=load(P/'MOD4_RM_TERRAIN_TRAINING_REVISION.json');prep=load(R/'TERRAIN_CURRICULUM_PREPARED.json');g=load(R/'RM_TERRAIN_CURRICULUM_GIT_RECORDED.json');ID=v['id']
assert g['remote_main_tag_peeled_verified'] and not g['push_pending']
assert digest(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
assert all(digest(P/n)==s for n,s in prep['files_sha256'].items())
assert all(digest(P/n)==s for n,s in v['prior_documents_sha256'].items())
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
try:
 with c.open_sftp() as s:
  def get(n):
   with s.open(central+'/'+n,'rb') as f:return f.read()
  def put(n,raw,expected=None):
   if expected is not None:assert get(n)==expected,'Concurrent metadata edit; abort '+n
   path=central+'/'+n;tmp=path+'.terrain_curriculum_003_tmp'
   with s.open(tmp,'wb') as f:f.write(raw)
   if expected is not None:assert get(n)==expected,'Concurrent metadata edit before rename '+n
   s.posix_rename(tmp,path);assert get(n)==raw
  names=['PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md','MOD4_PLAN_ANNOTATIONS.md','NEXT_E1_GENTLE_STABLE_TERRAIN_WORK_ORDER.json']
  before={n:get(n) for n in names};a=json.loads(before[names[0]]);t=json.loads(before[names[1]]);q=json.loads(before[names[2]]);w=json.loads(before[names[5]])
  assert a['approved'] and a['approved_plan_sha256']==v['master_sha256'] and a['S8_authorized'] is False
  assert ID not in a.get('plan_annotations',{}),'Revision already central; do not resync blindly'
  assert all(hashlib.sha256(get(n)).hexdigest()==h for n,h in v['prior_documents_sha256'].items()),'Prior central annotations differ; preserve and review'
  ref=dict(id=ID,document='MOD4_RM_TERRAIN_TRAINING_REVISION.md',json='MOD4_RM_TERRAIN_TRAINING_REVISION.json',
   document_sha256=prep['files_sha256']['MOD4_RM_TERRAIN_TRAINING_REVISION.md'],json_sha256=prep['files_sha256']['MOD4_RM_TERRAIN_TRAINING_REVISION.json'],
   human_request=v['human_request'],basis=v['basis'],type='human_requested_terrain_curriculum_revision',annotation_only=False,plan_only_no_learning_launch=True,
   revision_priority=v['revision_priority'],applies_to=['S3 independent E1 terrain traversal','S7 E1/E2 terrain spin'],
   next_work_orders=['NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.json','NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.json'],
   current_training_evaluation_budget_unchanged=True,new_budget_seconds=0,S8_authorized=False,Git=g)
  olda=copy.deepcopy(a);oldt=copy.deepcopy(t);oldq=copy.deepcopy(q);oldw=copy.deepcopy(w)
  a.setdefault('plan_annotations',{})[ID]=ref;t.setdefault('curriculum_annotations',{})[ID]=ref
  q.setdefault('curriculum_annotation_refs',[]).append(ref)
  t['next_E1_RM_terrain_work_order']=ref;q['next_E1_RM_terrain_work_order']=ref
  w['RM_annotation']='003 terrain curriculum revision first; 002 outer left/right curb geometry; 001 valid spin exclusions. Inner part383 49.56mm chamfer is separate, not human outer curb target.'
  w['future_terrain_curriculum_revision']=ref
  # Every previous actual learning/evaluation/budget field must remain structurally identical.
  for obj,old,key in [(a,olda,'plan_annotations'),(t,oldt,'curriculum_annotations')]:
   check=copy.deepcopy(obj);check[key].pop(ID)
   if key not in old:check.pop(key)
   if obj is t:check.pop('next_E1_RM_terrain_work_order')
   assert check==old
  check=copy.deepcopy(q);check['curriculum_annotation_refs']=[x for x in check['curriculum_annotation_refs'] if x.get('id')!=ID]
  if 'curriculum_annotation_refs' not in oldq:check.pop('curriculum_annotation_refs')
  check.pop('next_E1_RM_terrain_work_order');assert check==oldq
  check=copy.deepcopy(w);check.pop('future_terrain_curriculum_revision');check['RM_annotation']=oldw['RM_annotation'];assert check==oldw
  for n,raw in before.items():
   backup=n.rsplit('.',1)[0]+'_BEFORE_TERRAIN_CURRICULUM_003.'+n.rsplit('.',1)[1]
   try:s.stat(central+'/'+backup)
   except FileNotFoundError:put(backup,raw)
   else:raise RuntimeError('Partial previous sync boundary exists; independent review needed: '+backup)
   (R/('SYNC_BEFORE_'+n)).write_bytes(raw)
  uploaded={}
  for n in v['planned_documents']:
   raw=(P/n).read_bytes();put(n,raw);uploaded[n]=hashlib.sha256(raw).hexdigest()
  put('RM_TERRAIN_CURRICULUM_GIT_RECORDED.json',json.dumps(g,ensure_ascii=False,indent=2).encode('utf8'))
  idx=(P/'MOD4_PLAN_ANNOTATIONS.md').read_bytes()
  handoff=before['LATEST_HANDOFF.md']+('''

## 人类要求的地形课程修订003（2026-10-09）

最新人类“地形训练按照之间找到的修改一下计划”已转成MOD4-RM-TERRAIN-CURRICULUM-REVISION-003。先读MOD4_RM_TERRAIN_TRAINING_REVISION.md/json、NEXT_E1_RM_PROGRESSIVE_TERRAIN_WORK_ORDER.md/json、NEXT_S7_RM_TERRAIN_SPIN_WORK_ORDER.md/json；003课程优先，002外缘位置/几何澄清与001有效spin排除同时保留，原masterSHA/旧文件字节不改。

S3独立E1当前gentle两块/max4h收尾后审实际fullsave/整路线与旧技能，按起伏10/20/35/50mm、竖直坎20/35/50mm与当地坡5/8/10度分组准备，再实际70mm/约240.64mm/2.406m连续RM起伏、中央10.5度相对坡、左右外缘真实支撑->150mm宽条带->岛内路线。内侧44或92-94mm与外侧149.929或200.069mm高差分别准入，派生70/100/150mm坎只作中间档，不能冒称真RM或5cm覆盖15/20cm。普通低地采样差非同一坎高；原内侧part38349.56mm/45度另列，不再替代用户外缘目标。

先yaw0通行，再S7已验证表面/净空左右1->2->4->6->8->10->4pi纯转及定向移动；狗洞内、台阶踏面边缘台面、跨坎段排除，不给actor/gate地形真值。既有时钟/同范围合同SHA复用，新geometry/contact/ground/reset/fullresume补自己的必要合同/PPO弃权重各一次。当前source313/unique入口/actual进程/DR/runtime/PPO/canonical交易0，本次不hotpatch/kill/双开/clearactive、不复活93/94或MuJoCo。新范围必须旧fullsave/旧launch关闭/实际退出/两锁/账段自然结清后接管，S8危险reset边界保留。

沿用S3含已用时间30h、S7条件18h规划上限，预算新增0，按实际B保护专家/gate和min(18h,.13B)修复时间；非逐档强制训练/无限gentle/机械90/95/100毕业线。每2h监控ACTIVE、健康pending静默。plan_only_no_learning_launch=true；几何标注或本次计划发布不能称SDK/技能已经通过。
''').encode('utf8')
  assert all(get(n)==raw for n,raw in before.items()),'Concurrent metadata update before commit'
  updates={names[0]:a,names[1]:t,names[2]:q,names[5]:w}
  for n,obj in updates.items():put(n,json.dumps(obj,ensure_ascii=False,indent=2).encode('utf8'),before[n])
  put('MOD4_PLAN_ANNOTATIONS.md',idx,before['MOD4_PLAN_ANNOTATIONS.md']);put('LATEST_HANDOFF.md',handoff,before['LATEST_HANDOFF.md'])
  assert json.loads(get(names[0]))['plan_annotations'][ID]==ref
  assert json.loads(get(names[1]))['curriculum_annotations'][ID]==ref
  assert json.loads(get(names[2]))['next_E1_RM_terrain_work_order']==ref
  assert json.loads(get(names[5]))['future_terrain_curriculum_revision']==ref
  assert all(hashlib.sha256(get(n)).hexdigest()==h for n,h in uploaded.items())
  proof=dict(epoch=time.time(),id=ID,metadata_synced=True,metadata_only=True,master_SHA_unchanged=v['master_sha256'],
   prior_001_002_documents_unchanged=True,learning_evaluation_budget_metadata_unchanged=True,current_work_order_runtime_source_fields_unchanged=True,
   new_future_work_orders_and_current_reference_verified=True,uploaded_sha256=uploaded,compare_before_write_protected=True,
   production_runtime_GPU_PPO_canonical_writes=0,new_budget_seconds=0,Git=g)
  raw=json.dumps(proof,ensure_ascii=False,indent=2).encode('utf8');put(receipt.name,raw);receipt.write_bytes(raw)
  print(json.dumps(dict(metadata_synced=True,id=ID,master_unchanged=True,current_training_unchanged=True,new_budget_seconds=0),ensure_ascii=True))
finally:c.close()
