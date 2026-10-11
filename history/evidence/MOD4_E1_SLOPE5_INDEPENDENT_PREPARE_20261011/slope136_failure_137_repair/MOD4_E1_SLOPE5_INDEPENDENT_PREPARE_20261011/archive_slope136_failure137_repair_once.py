"""Unique actual complete135/new136 stage; preserve originals and verify remote objects."""
from archive_slope_scope_stage_once import *
import io,contextlib,importlib.util
ID='e1-slope8-precontrol-rayinput-rejection-and-isolated137-repair'

def main():
 assert not g('status','--porcelain') and json.loads((R/'SLOPE136_FAILURE_137_REPAIR_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 save('SLOPE136_FAILURE_137_REPAIR_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_tag_replay=True))
 note=R/'SLOPE136_FAILURE_137_REPAIR_STAGE_REPORT.md';assert not note.exists()
 note.write_text('# 136地面射线输入身份拒绝与独立137修复\n\n136初始化后、控制循环前ground expected断言失败，original result retained_failed、error.txt与两主机桥接字节SHA保持。物理进程39.373877s，没有PPO或控制循环，canonical未扣账。原GPU实际误差未保存，不假报CPU重核为GPU测量：独立CPU worldfloat32 dispatch点相对于理想float64采样的解析高度差最大1.059626870e-6m，2800独立三角射线按actual输入误差3.330669074e-16m。\n\n新137只将ground解析期望绑定实际worldfloat32射线原点与镜像canonical坐标并完整披露原requested grid。原1e-6容差/normal门槛保持，8°geometry/profile、完整控制循环/health/groundcontact/hardware audit ASTexact。287manifest逐字SHA，新package36,559,313bytes SHA bd69b2a2a842aff0f0bc9dfa03105fd089281d723bae678dd28d80f88a6306c7，只有dispatcher/manifest两成员bytes改变，原136不重发或重标pass。\n\n旧G3worker因实际失败自然退出，CIM无worker/GPU孩子、原sharedOSlockfree、old demandtask Ready且0trigger实核后才disable旧demandtask并部署新E1_SLOPE8_QUERY_REVIEW namespace。新增唯一136精确exclusion，baseguard/restrictedbridge/JSONboundedretry/singleGPUlock不变，new demandtask无periodic/boottrigger、no4090launch/no canonicalwrite。actualnewworker28024/creation1791687952.211及venv34940/.203只是定位；后actualCIM/result/attention优先，健康不重启。原source/attention/result/error/taskXML全保留。\n\n新137已actualpublished，仍source404完整135own24b/CPU102/79snapshot/ownPID/PASSED/唯一结清；8°/2m镜像/80env15s/0.4m接近和两轮200mm后支撑、完整raw合同原样。actualcomplete pending，未称物理通过。complete135全四case/5°上下各27/27已审，scopecandidate冻结，negative4pi7→5/8诊断退化不抹，gate未训/非全E1/RM/MoE。完整137review/必要新scope合同前不更多PPO或升10°。\n\n新failure137中央metadataCAS已同步，masterapprovaltracksRMcanonicalbytes保持/828000s六扩展各一次新增0。E0/Wave/CURB及5°weights/output不覆盖，WASD播放器不干预。全部failedraw/false/source/schema/部署/同步/reader/workorder及旧阶段后报告Git捕获，大weights/rawNPZ/USD/ZIP只actualpath-size-SHA；stage后monitor/Gitreceipt及未来137complete仍ordinarysupplement。此前cd740ccb/ca0fe已远端实核保持；不重record/tag/commit或旧once。\n',encoding='utf8')
 entries,files=capture(DEST/'slope136_failure_137_repair')
 spec=importlib.util.spec_from_file_location('complete135_stage_record',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Preserve slope8 precontrol rayinput rejection and deploy isolated actual-input scope','--kind','repair','--note-file',str(note),'--files',*files,'--validation','Original136 precontrolground assertion and2hostresult-errorbyteSHA retained,noPPO budgetcost. CPU2800rays shows ideal-versus-float32 input expectation mismatch1.059626870e-6;actualinputtriangleerror3.33e-16,notGPUmeasurement. New137 onlyexpected-inputidentity/protocoldisclosure,1e-6 tolerance geometry andloopASTexact,287manifest packageSHA exact. Oldworkernaturalexit/actualCIM nochildren sharedOSlockfree demandtask0triggersReady proven before unique namespace admission;only exactfailed136 retired,baseguardbridgeJSONlock unchanged.137 publishedfrozenonly source404own13524b,newresultpending.MasterapprovaltracksRMcanonicalbytespreserved.Allsavedfailures/reader/source/metadata/workorders indexed,largeactualpathsizeSHA only.','--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('SLOPE136_FAILURE_137_REPAIR_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_only_continue_objects=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('SLOPE136_FAILURE_137_REPAIR_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_FAILURE_137_REPAIR_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
