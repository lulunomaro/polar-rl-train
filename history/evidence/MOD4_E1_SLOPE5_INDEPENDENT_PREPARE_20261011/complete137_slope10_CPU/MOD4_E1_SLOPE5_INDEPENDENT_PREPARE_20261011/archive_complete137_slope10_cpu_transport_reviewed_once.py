"""Unique actual complete135/new136 stage; preserve originals and verify remote objects."""
from archive_slope_scope_stage_once import *
import io,contextlib,importlib.util
ID='e1-slope8-complete-frozen-route-and-next10degree-cpu-component-reviewed'

def main():
 assert g('rev-parse','HEAD')=='d0b520da55e3a64125938196aa63b75337867b63'
 assert not g('tag','--list','*complete-frozen-route-and-next10degree*')
 assert not (R/'COMPLETE137_SLOPE10_CPU_ARCHIVE_STARTED.json').exists()
 assert not (R/'COMPLETE137_SLOPE10_CPU_STAGE_REPORT.md').exists()
 assert not (DEST/'complete137_slope10_CPU').exists()
 old=json.loads((R/'COMPLETE137_SLOPE10_CPU_ARCHIVE_ERROR_1791689271176951400.json').read_bytes())
 assert 'ls-remote' in old['error'] and 'missing close_notify' in old['error']
 save('COMPLETE137_SLOPE10_CPU_TRANSPORT_REVIEWED_STARTED.json',dict(epoch=time.time(),original_failure_before_archive_record=True,actual_local_remote_main_restored=True,continue_only_unexecuted_archive_same_trial_id=True,no_old_record_tag_or_commit_created=True))
 assert not g('status','--porcelain') and json.loads((R/'COMPLETE137_SLOPE10_CPU_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 save('COMPLETE137_SLOPE10_CPU_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_tag_replay=True))
 note=R/'COMPLETE137_SLOPE10_CPU_STAGE_REPORT.md';assert not note.exists()
 note.write_text('# 完整8°冻结通行与下一10°CPU组件\n\n137已actualcomplete/errorfree；两hostprobe/result字节SHAexact，181270701byte完整rawNPZ SHA b0d1059bbe50252e10fbfd672f436df79da0ed0664e6c10ed5a13977b9daef8f，全root30q/parameters/recipes/assignments/6000callback/实际groundcontact积分COMlinkhardware原容差独立审查。新actualworldfloat32射线原点/canonicalgrid身份原1e-6校验通过，完整2m镜像8°坡/.4m接近/200mm后支撑上下各27/27且1N支撑吻合，ordinary0/closure.663315877mm/7声明route截断two reasoncoverageexact，站立26无需跨坡。Frozen physicalprocess267.061986s无PPO/canonical扣账；原136failed-before-control与39.373877s成本保留不重标pass。\n\n采用完整135 own40424b/CPU102/79snapshot/PID/PASSED/唯一335.210922s源；接受观测5°及8°scope并冻结，无额外8°PPO，不声称因果训练收益或整个SLOPE/RM/MoE/gate毕业。135旧negative4pi7→5/8诊断下降与原strictfalse保持，E0一直冻结且未训练gate不借此证明整机switch已验收。原G3worker因136失败自然退出后独立E1_SLOPE8_QUERY_REVIEW worker/单GPUlock/restrictedbridge/无触发demandtask保持，健康新worker无GPU孩子idle合法不重启。\n\n积极准备已批准RM003下一单轴10°CPU组件，派生连续2m高.352653961m/9m镜像，198独立三角射线与法向验证，maxerror3.330669074e-16m。CPU是组件证据，尚无10°frozenpackage/job/SDK/native/完整状态/PPO/executor部署。cos10°=.984807753低于旧8°sample-normal>.99，新10°必须先显式解析三角法向/实际射线输入normal与height合同，原ground1e-6及contact/硬件/ordinary-integrity阈值保持，不能机械复制旧normal检查或静默放宽。完整来源5°terraincommand/CPUCUDA身份验证后明确5→10新geometry与assignment迁移，必要新scope准入/首300s保存复审仅实际需要学习时执行，不能机械每档固定PPO。\n\n中央complete137/next10CPU CAS实际同步，历史masterapprovaltracksRMcanonicalbytes保持，828000s六扩展各一次新增0；E0/Wave/CURB与5°/8°冻结source不覆盖，S8后续具体批准，WASD播放器不干预。新collector/review/decision/workorder/组件源码及阶段后监控/Gitreceipt/encoding错误全部Git捕获，大weights/rawNPZ/USD/ZIP仅actualpath-size-SHA。cd740ccb/ca0fe和d0b520da/e760以及所有旧tag对象保持；本stage后新monitor/sync/Gitreceipt仍ordinarysupplement，actualtracked/remote工具证明优先。\n',encoding='utf8')
 entries,files=capture(DEST/'complete137_slope10_CPU')
 spec=importlib.util.spec_from_file_location('complete135_stage_record',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete8degree frozen route and prepare approved10degree CPU component','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Actual137 complete errorfree,twohostJSON byteSHA/full181270701NPZ SHA verified. Original1e-6 actualfloat32 input-ground identity,fullroot30q DRparametersrecipesassignments6000callbacks groundcontactCOMlinkhardware tolerances independently reviewed.Ascendingdescending27/27 each with1N contact,ordinary0,7declaredroute truncations,two coverageexact. Frozen5and8 scope source404own24b only,no8PPO or fullSLOPEgate qualification;negative4pi diagnosticdecline andoldfalse preserved. Original136precontrolfailurecost retained.New10degreeCPU198rays/normals max3.33e-16 only;cos10 below old8normal sampleguard needs explicitnewgeometrynormal contract,no10GPUjob orlearning.MasterapprovaltracksRMcanonicalbytespreserved.Allsavedreports/source/errors indexed,largeoriginalsactualpathsizeSHA only,oldtagsunchanged.','--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('COMPLETE137_SLOPE10_CPU_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_only_continue_objects=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('COMPLETE137_SLOPE10_CPU_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE137_SLOPE10_CPU_TRANSPORT_REVIEWED_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
