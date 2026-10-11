"""Unique actual complete135/new136 stage; preserve originals and verify remote objects."""
from archive_slope_scope_stage_once import *
import io,contextlib,importlib.util
ID='e1-slope10-explicit-analyticnormal-query-contract-and-frozen138-deployed'

def main():
 assert not g('status','--porcelain') and json.loads((R/'SLOPE138_SCOPE_METADATA_SYNCED.json').read_bytes())['metadata_synced']
 before=g('rev-parse','HEAD');tags={x.split('|')[0]:(x.split('|')[1],x.split('|')[2] or x.split('|')[1]) for x in g('for-each-ref','--format=%(refname)|%(objectname)|%(*objectname)','refs/tags').splitlines()}
 remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==before
 save('SLOPE138_NORMAL_SCOPE_ARCHIVE_STARTED.json',dict(epoch=time.time(),trial_id=ID,prior_main=before,prior_tag_count=len(tags),no_old_record_tag_replay=True))
 note=R/'SLOPE138_NORMAL_SCOPE_STAGE_REPORT.md';assert not note.exists()
 note.write_text('''# 新10°解析法向合同及唯一冻结138部署

完整135/137 source404own24b已实际通过5°和8°镜像上下各27/27，旧negative4pi下降及strictfalse不改，不机械8°PPO或整体SLOPE/MoE毕业。本次执行已批准RM003单角度10°，派生连续2m高.352653961m/9m镜像/.4m接近/两轮全坡后200mm支撑，80env1500control15s/20260928white3，仅冻结source404原5°保存权重，不新的完整状态迁移或PPO。

原8°初始化sample-normalz>.99不适用cos10=.984807753。新显式解析三角面法向合同，actualworldfloat32射线height绑定/原ground1e-6，坡段normal[-orientation*sin10,0,cos10]与flat[0,0,1] component<=1e-6/unit<=1e-6/正z，35point查询不含接缝；独立2800actualinput三角射线、四接缝法向歧义披露通过。平支撑原>.99、原productionordinaryintegrity/groundcontactintegralCOMlinkhardware容差和步进循环ASTexact保持。新增geometry/profile/dispatcher/manifest、289文件SHAexact，新包36562686bytes SHA0ad115e2baf20e59a9810eab8d05f4c3ec54a08ca9844f0ae9685a979475ea2d，旧成员保留。

发布前真实404ownfullsave/PASSED/唯一settled335.210922s/三进程actualexit/两fcntlOS锁free/noactive/sourceSHA核验。当前健康E1_SLOPE8_QUERY_REVIEW worker28024及venv34940 source/baseguardSHAactual验证，无attention，不重启；同sharedsingleGPUlock/restrictedbridge/JSONboundedretry/demand0trigger/no4090launch/nocanonicalwrite，只有新唯一138job，不复播137/136或其它旧complete。旧136真实precontrolfailure/raw成本保持。

138实际完整两hostJSONbyteSHA/fullNPZ/初末root30q/参数recipesassignment/6000callback/原groundcontactCOMlinkhardware/两轮全坡支撑及所有validprefix审查仍依actual结果，不借CPU/包/进程称物理通过或自动PPO。下一完整合理证据后按004其它专家问题单轴诊断纠正，未审不自动更高坡度。中央new138scope同步已完成，masterapprovaltracksRMcanonical字节保持，总828000s六扩展各一次新增0，无PPO不扣。原5°8°和E0/Wave/CURB权重optimizer不变，gate未训/hardware未标定/S8后续批准/WASD不干预。

保存的CPU/source/manifest/dispatch/currentcollector/工作单/同步和全部后来complete/failure/reader/monitor/Gitreceipt仍Git；大weights/rawNPZ/USD/ZIP只有真实path-size-SHA，凭据不输出归档。原a63f54c0/1571f和cd740ccb/ca0fe、d0b520da/e760及所有旧tagobjects保持，push失败仅续objects，阶段后ordinarysupplement不漏报告。
''',encoding='utf8')
 entries,files=capture(DEST/'slope10_normal_scope138')
 spec=importlib.util.spec_from_file_location('complete135_stage_record',REPO/'archive_tools/record_experiment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);original_git=mod.git
 def short_git(*args):
  if args[:2]==('add','--'):
   p=subprocess.run(['git','-C',str(REPO),'add','--pathspec-from-file=-','--pathspec-file-nul'],input='\0'.join(args[2:])+'\0',capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
  return original_git(*args)
 mod.git=short_git
 sys.argv=[str(REPO/'archive_tools/record_experiment.py'),'--id',ID,'--title','Deploy unique slope10 frozen scope with explicit analyticnormal and actualray contract','--kind','evaluation','--note-file',str(note),'--files',*files,'--validation','CPU2800actualfloat32query triangle rays/normal maxerror3.33e-16/1.11e-16 andjoins reviewed. Explicit10degree analyticnormal componentunit1e-6, originalheight1e-6, flatnormal>.99 andproductionordinaryintegritycontactCOMlinkhardware original thresholds/control loopASTexact. Package36562686SHA0ad115e2/289immutablefilesexact. Actual404ownfullsavePASSED unique settled segment exits twoOSlocksfree budgetidle source24b verified. Healthynewworker actualsource/base/CIM no restart, unique138frozenpublished only, fullGPUresult not assumed. CentralCAS masterapprovaltracksRMcanonical preserved828000sixextensionsnew0. Allsaved reports/source/errors/indexed, lateractual138andmonitor supplement, oldtags unchanged.','--push']
 out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):mod.main()
 except BaseException:save('SLOPE138_NORMAL_SCOPE_RECORD_ERROR.json',dict(stdout=out.getvalue(),error=traceback.format_exc(),may_have_committed_only_continue_objects=True));raise
 tag,commit=out.getvalue().strip().splitlines()[-1].split();obj=g('rev-parse',tag);remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
 assert remote['refs/heads/main']==commit and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==commit
 for t,(o,c) in tags.items():assert remote[t]==o and remote.get(t+'^{}',c)==c
 assert not g('status','--porcelain');tracked=set(g('ls-tree','-r','--name-only','HEAD').splitlines());assert set(files)<=tracked
 for row in entries:
  if row.get('Git_path'):assert H((REPO/row['Git_path']).read_bytes())==row['archived_sha256']
 row=dict(epoch=time.time(),tag=tag,commit=commit,tagobject=obj,remote_main_tag_peeled_verified=True,push_pending=False,new_files=len(files),same_SHA_refs=sum(x['capture']=='existing_same_SHA_Git_reference' for x in entries),large_indices=sum('index_only' in x['capture'] for x in entries),all_old_tag_objects_unchanged=True)
 save('SLOPE138_NORMAL_SCOPE_STAGE_GIT_RECORDED.json',row);print(json.dumps(row))

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE138_NORMAL_SCOPE_ARCHIVE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_repeat_record_or_tag=True));raise
