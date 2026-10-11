"""Unique actual complete135/new136 stage; preserve originals and verify remote objects."""
from archive_slope_scope_stage_once import *
import io,contextlib,importlib.util
ID='e1-slope5-complete135-reviewed-and-single-angle8-frozen-deployed'

def main():
 assert not g('status','--porcelain') and json.loads((R/'COMPLETE135_SLOPE136_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 save('COMPLETE135_SLOPE136_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_tag_replay=True))
 note=R/'COMPLETE135_SLOPE136_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# 完整135坡面候选与新8°单轴冻结范围

source404 ownmodel32069 SHA24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411、CPU102/79actualsnapshot、own2588230/PASSED与335.2109215s唯一结清已实际核验，父guardian孩子自然退出/两OS锁free/canonicalidle。135四caseactualcomplete/errorfree，两host8probe/result字节SHAexact、181145243byte完整rawNPZ SHA c0fe281d8db1f0e489e4bdf93ac1e040803525d14f1c172bad8f256bf9a3394b，初始化root30q参数配方assignment/6000callback/ground-contact积分COMlinkhardware原容差、全signedcircle实际审查。

5°/2m镜像、0.4m接近、两轮完整坡段及200mm后支撑上下各27/27，1N接触证据吻合，站立26无跨坡要求。ordinary0/closure.662365521mm/四声明route截断原覆盖exact。来源3643c97同5°也上下各27/27，不声称因果训练收益。旧world63→64/64，maxcross.049271624；负4π7→5/8下降、正8/8、直线.020943796/.055501711与全部原strictfalse保留。只冻结接受本次5°范围候选，非整个SLOPE/RM/MoE部署，gate未训。

积极推进已批准RM003坡度5→8一个轴：新136冻结包36,559,243bytes SHA050ef42a3909b13292f0caf29c3a82a05c030d38a35a16312bdc6790c2a5b0c9、287manifest逐字SHAexact，派生8°/2m高.281081669m/9m镜像、原0.4m接近与200mm后支撑。198独立三角射线及法向CPU合同通过，步进/health/contact/hardware审查loop ASTexact；CPU不代物理验收。使用已存在135同SHA24b许可artifact，不重新训练或复制canonical。旧404真实fullsave/退出/唯一结清/两OS锁核后才新136唯一发布，健康3060工作器不重启；实际结果未生成是pending。不同8°不能冒同5°精确初始化，完整136决定/必要新范围恢复SDK/native/PPO准入前不启动更多学习或升10°。

读者兼容错误：旧135collector把地形full_route_raw强套legacy技能KeyError，原错误/源码保留；独立schema collector按actualresultSHA=manifestSHA=ownformalSHA及job/checkpoint.bin接收旧技能，地形fullraw原合同不松。首次136发布guard全字串SHA替换误伤canonical_SHA导致本地compile SyntaxError，在任何远端写/队列/GPU前拒绝；原source/error保持，独立唯一placeholder修正只续未执行发布。没有重发任何validcomplete或修改false/raw/cost。

中央完整135决定与136新冻结范围实际CAS同步，历史master/approval/tracks/RM/canonicalbytes保持；预算828000s/六扩展各一次/新增0、当前idle316797.542619s仅快照。E0/Wave/CURB与5°自身权重不覆盖，S8后续具体批准/人类WASD播放器不干预。全部newreports/source/errors/workorders/同步与此前stage后报告完整捕获，大weights/rawNPZ/USD/ZIP仅真实path-size-SHA。Git阶段后的监控/Gitreceipt与后来136实际结果仍ordinarysupplement，remote验证工具证明优先。
''',encoding='utf8')
 entries,files=capture(DEST/'complete135_slope136')
 spec=importlib.util.spec_from_file_location('complete135_stage_record',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review complete isolated slope5 candidate and deploy approved8degree frozen scope','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','Actual135 all4 complete errorfree,8twohostJSON byteSHA and fullNPZ SHA checked; original fullroot30q DRassignments callbacks groundcontactCOMlinkhardware tolerances and signedcircles reviewed. Ascendingdescending27/27 each with original1N contact; scoped5degree frozen candidate only. Negative4pi7to5 diagnostic decline and oldstrictfalse retained. Own404CPU102/79snapshot/PASSED/unique segment/exits twoOSlocks canonicalidle verified. Singleangle8 new136 CPU198 rays and287manifest exact, loopAST exact; published frozen only on healthy worker using existing135SHA24b artifact, noPPO orbudgetwrite. Collector schema and publisher prewriteSyntaxError retained and independently repaired, noeval replay. Complete135/new136 CAS synced masterapprovaltracksRMcanonical unchanged. Allsavedreports/errors captured, large originals actualpathsizeSHA only.','--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('COMPLETE135_SLOPE136_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_only_continue_objects=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('COMPLETE135_SLOPE136_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))

if __name__=='__main__':
 try:main()
 except BaseException:save('COMPLETE135_SLOPE136_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
