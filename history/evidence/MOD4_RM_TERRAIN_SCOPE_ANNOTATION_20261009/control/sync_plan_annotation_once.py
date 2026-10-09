"""Append a user-requested curriculum annotation; no runtime/ledger/launch writes."""
from pathlib import Path
import json,time,hashlib,sys,copy
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train/history/plans'
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'RM_TERRAIN_SCOPE_METADATA_SYNCED.json').exists()
v=read(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json');ID=v['id'];g=read(R/'RM_TERRAIN_SCOPE_GIT_RECORDED.json')
assert g['remote_main_tag_peeled_verified'] and not g['push_pending'] and sha(P/'MOD4_MOE_MASTER_PLAN.md')==v['master_sha256']
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();central='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
try:
 with c.open_sftp() as f:
  def get(n):return json.loads(f.open(central+'/'+n).read())
  def put(n,raw):
   if not isinstance(raw,bytes):raw=json.dumps(raw,ensure_ascii=False,indent=2).encode('utf8')
   path=central+'/'+n;temp=path+'.rm_terrain_annotation_tmp'
   with f.open(temp,'wb') as out:out.write(raw)
   f.posix_rename(temp,path);assert f.open(path).read()==raw
  approval=get('PLAN_APPROVAL.json');tracks=get('EXECUTION_TRACKS.json');current=get('MOE_PLAN_EXECUTION_CURRENT.json');handoff=f.open(central+'/LATEST_HANDOFF.md').read()
  assert approval['approved'] and approval['approved_plan_sha256']==v['master_sha256'] and approval['S8_authorized'] is False
  assert ID not in approval.get('plan_annotations',{})
  protected_approval={k:copy.deepcopy(approval[k]) for k in ('approved','approved_plan_sha256','version','allowed_stages','conditional_stages','S8_authorized','authorized_budget_ceiling_seconds')}
  protected_tracks={k:copy.deepcopy(tracks[k]) for k in ('learning','evaluation','budget') if k in tracks}
  protected_current=copy.deepcopy(current)
  for n,raw in [('PLAN_APPROVAL.json',f.open(central+'/PLAN_APPROVAL.json').read()),('EXECUTION_TRACKS.json',f.open(central+'/EXECUTION_TRACKS.json').read()),('MOE_PLAN_EXECUTION_CURRENT.json',f.open(central+'/MOE_PLAN_EXECUTION_CURRENT.json').read()),('LATEST_HANDOFF.md',handoff)]:
   backup=n.rsplit('.',1)[0]+'_BEFORE_RM_TERRAIN_SCOPE_20261009.'+n.rsplit('.',1)[1]
   try:f.stat(central+'/'+backup)
   except FileNotFoundError:put(backup,raw)
  for n in ('MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md','MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json','MOD4_PLAN_ANNOTATIONS.md'):put(n,(P/n).read_bytes())
  put('RM_TERRAIN_SCOPE_GIT_RECORDED.json',g)
  ref=dict(id=ID,document='MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md',json='MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json',document_sha256=sha(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md'),json_sha256=sha(P/'MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.json'),basis=v['basis'],human_request=v['human_request'],annotation_only=True,applies_to=['S3 E1 terrain foundation','S7 E1/E2 terrain spin'],no_current_D7_changes=True,new_budget_seconds=0,Git=g)
  approval.setdefault('plan_annotations',{})[ID]=ref
  tracks.setdefault('curriculum_annotations',{})[ID]=ref
  current.setdefault('curriculum_annotation_refs',[]).append(ref)
  for k,old in protected_approval.items():assert approval[k]==old
  for k,old in protected_tracks.items():assert tracks[k]==old
  check=copy.deepcopy(current);check.pop('curriculum_annotation_refs',None);prior=copy.deepcopy(protected_current);prior.pop('curriculum_annotation_refs',None);assert check==prior
  appendix='''\n\n## 用户明确新增的RM地形计划标注（2026-10-09）
后续S3/E1及S7/E1-E2执行前读取 MOD4_RM_TERRAIN_SPIN_ENTRY_LIP_ANNOTATION.md/json 与 MOD4_PLAN_ANNOTATIONS.md。
小陀螺目标：普通地面/宽公路路面、双方起伏路、中心岛连接坡的坡面、公路连接坡与梯形高地斜面。明确排除狗洞内、台阶踏面/边缘/台阶上的台面；飞坡跨沟/腾空仍是后续独立技能。部件内含多种表面，必须实际区域mask分开，不额外给actor/gate地形真值。
台阶通行工作单必须包含二级中心岛入口小路坎（给定CAD part383/BREP_424，y=0局部倒角约49.561756mm高差、45度）及其与主坡/台阶的连续过渡，覆盖上/下、倒退、左右斜向、停后起步，不能只在坎后reset。45度是局部入口倒角，不是整条主坡；另有part280/281约100mm独立边缘凸坎不能混为同物或算入已有5cm档。
这是用户本次要求的计划补充，主v1.5批准SHA不变；当前D7学习/冻结来源/预算不改。实际新几何仍完成自己的范围/ground/contact/reset读回，再按合法保存边界实施；不重复有效时钟45min或同范围PPO。原S8新危险reset具体批准边界保持。本标注不是地形技能已训练/已通过的证明。
'''
  assert ID.encode() not in handoff
  put('PLAN_APPROVAL.json',approval);put('EXECUTION_TRACKS.json',tracks);put('MOE_PLAN_EXECUTION_CURRENT.json',current);put('LATEST_HANDOFF.md',handoff+appendix.encode('utf8'))
  assert get('PLAN_APPROVAL.json')['plan_annotations'][ID]==ref and get('EXECUTION_TRACKS.json')['curriculum_annotations'][ID]==ref
  live_current=get('MOE_PLAN_EXECUTION_CURRENT.json');live_current.pop('curriculum_annotation_refs',None);assert live_current==prior
  proof=dict(epoch=time.time(),metadata_only=True,master_SHA_unchanged=v['master_sha256'],annotation=ref,active_learning_evaluation_budget_metadata_unchanged=True,production_sources_ledger_GPU_PPO_launch_writes=0,Git=g)
  put('RM_TERRAIN_SCOPE_METADATA_SYNCED.json',proof);(R/'RM_TERRAIN_SCOPE_METADATA_SYNCED.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps(dict(synchronized=True,annotation_id=ID,master_unchanged=True,current_learning_unchanged=True,no_GPU_PPO_budget_transactions=True)))
finally:c.close()
