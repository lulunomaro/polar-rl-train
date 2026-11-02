"""Ordinary supplement for the already recorded MPC handoff phase; never retag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
BASE=G/'versions/20261102_mod4-mpc-control-handoff339-349';V=BASE/'supplement371_actual_MPC_reset_contact_and_request'
TAG='trial-20261102-mod4-mpc-control-handoff339-349';OBJ='f63c76d9c064a26e6261b544304c7f92a5bbdf76';PEEL='a6c59be6408153875b36ed851d59d3767f8e5709'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
assert not git('status','--porcelain')and git('branch','--show-current')=='main'
assert not V.exists()and not(R/'SUPPLEMENT371_ONCE_CONSUMED_BEFORE_GIT.json').exists()
assert git('rev-parse','refs/tags/'+TAG)==OBJ and git('rev-parse','refs/tags/'+TAG+'^{}')==PEEL
oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in oldrefs.items())
lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));req=read(R/'AUTOMATION370_UPDATE_REQUEST.json')
assert cfg['prompt']==req['prompt']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']and cfg['rrule']==req['rrule']
put(R/'AUTOMATION370_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(R/'AUTOMATION370_UPDATE_REQUEST.json'),toolreceipt=str(R/'AUTOMATION370_APP_UPDATE_ACTUAL_TOOL_RECEIPT.json'),same_existing_hourly_ACTIVE_thread=True))
put(R/'SUPPLEMENT371_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),mode='ordinary_supplement_existingphase_no_record_or_retag',tag=TAG,object=OBJ,peel=PEEL,oldrefs=oldrefs,remote_before=remote,lqr=lqr,push_retry='Resume existing commit/objects if pushfails; never rerun this once.'))
note=R/'SUPPLEMENT371_MPC_HANDOFF_RESET_CONTACT_AND_REQUEST.md'
note.write_text('''本补充承接既有 phase mod4-mpc-control-handoff339-349（record351，supplement361），不重建trial、不改旧tagobject/peel。人类问完整调好的MPC和电机轨迹为何无法跳台，本轮继续核实际控制链，未启动unused345，未读取神经检查点、未创建优化器或canonical writer。

362离线读取已保存355/357 source/actual日志，定位两个具体差异。第一，旧359/360离线比较把执行器local顺序当策略通道顺序。实际363具名joint_indices确认执行器腿顺序hipL,crankL,hipR,crankR，接轮L/R；转source应为[0,1,4,2,3,5]。原359/360错误和false全部保留，物理动作目标映射未因此修改。第二，source347复位D4初始保持目标使用计划实际q，355/357先reset默认q队列再写非零plannedstate，可能在命令延迟首拍产生默认零角PD回拉。

独立363冻结、CPU0step准入后执行80env、250controls/2000physics/500feedback，原50target/100feedback/400physics、2.5msTGS32-4、400N工程k2000/fullD0whitev3D1-D7/闭链10mm/mimic.01、PD和DC限幅保持。40legacydefaultqueue vs40plannedactualqheldtarget；helper只改选中applied/pending两buffer，RNG/lag/episode/tick不改，freshphysical/DR明确。所有80currentstateMPC按actual20ms重离散H8；0NN/学习/优化/模型读取/账。实际namedPD输入与computed误差max7.6113e-6Nm，plannedhold首拍不再回拉；但legacy17full5s23orientation均寿命2.8595s，planned11full29orientation均2.3005s，旧strict0各组。非逐项matchedDR，不能说复位修好/唯一原因。安全退出/ownwait/private_sharedreleased/SSHfinallyclosed/sessionrestoreFREE，实际bodyposes有限渲染和当前模型原生已审。env1/env40实际落台站住，env0/41台沿倾倒；364可视回放90s已真实启动、提前截图并退出。旧冻结viewer有kind隐藏平台和假actor标签，独立364修正显示/范围，原件不改。

进一步找到旧stablecounter被currentfirst_air==1一直约束；首次飞行整轮越沿之后，台面着陆反弹产生新air事件，会永远阻止后续恢复的稳定计时。363rawstrict0原封保留。独立365准备实际contact manifold审计但静态发现其新ontop同时改变controller.observe_top事件，不满足同controller承诺；365unused、0网络/SDK/物理，冻结源及scope错误保留，不执行。独立366保留363原controller_ontop expression，仅把评测改为首次飞行整轮rearfootprintclear latched、实际平台top接触points/normals/forces和全水平footprint；回地面/退沿作废，vxy/vz.03m/s、rollpitch10deg、yaw.2rad、连续.5s完全保留。原physics/PD/queue/限幅/控制器不改。

实际366安全完成80/250/2000/500，legacy7/40 strict，planned2/40 strict，总9/80。367独立保存数据核全部80controller14state/processedtarget逐值0差、firstepisode寿命/终止一致，4selected全数组bodyposes/actions/q/target逐值0差，新增contact读取没有改变运动。9候选都核首次飞行整轮clear及真实台顶manifold，env40连续strict1.4075s，222个实际solvercontactpoint例证支持双轮上表面，非COM或轮前缘进展冒充。全部原rawfalse保留，不能把9/80传统privilegedMPC结果重分类回写324学员或称自主depth-only技能毕业。

实际namedeffort记录显示push/flight轮requested常超过物理轮峰值，飞行请求峰约73.6Nm，source347成功轨迹轮request峰约11.56Nm；原物理真实DCclip始终执行，selectedPD计算并无符号/映射bug。独立368同80plannedqhold、同actual20msMPC和366实际manifold评测，0..39源请求，40..79仅push/flight/extend轮requested按同source nominal signedDC envelope和已经观察轮速约束，再inversePD。原实际PD/D4/gains/DCclip不改，腿requested/approach/recover公式不改，CPU0step fixtures核过。实际新finite结果：源4/40 strict、15full5s/25orientation、mean2.749s、32整轮clear；bounded7/40strict、22full/18orientation、mean3.396s、29整轮clear，总11/80。源组air超额wheelrequest946/1109、target60饱和637；bounded issued超额0/1198、target60为0。369独立复核11个strict实际manifold时间段，无ground/edge返回，DR同分布非exactpaired，不断言稳健提升/唯一因果。selected4这次都倒，实际图已原生看过，不能用selected图否定80原测量，也不能报技能毕业。

决定370：保留正确namedtelemetry、sourceplannedqhold、366评测修复/actualmanifold，wheelprebound是候选控制改进；不原样repeat368、不盲启345一小时。下一步先读保存368 push/flight成功失败q/dq/pitch/实际限幅/perenvDR，设计有据的新有限对照，优先真正matchedDR或source事件/时序控制交接。源100Hz闭环尚未忠实移植，现queue50Hz不暗改。MPC有privilegedrootx/vx/yaw且只属传统诊断；不是NN depthstudent、不是可查询PhysXactionteacher、不无限制torquecloning。324已关闭/CPU609finite且339独立0/80，345仍unused。

资源：NINEV8其他聊天collector60772退出且发布allownwaited/private/sharedreleased后才执行363。三次finite363/366/368均freshLOCAL广范围knowncontroller CIM只有owncaller、parentfreshCNone/private/shared原准入，全ownworkerswaited/locksreleased/SSHfinallyclosed/sessionrestoreFREE。无第二writer/预算增加/grant/copy/refund/clearactive/GPU PIDscan/unknownkill。所有once永久保留不可重跑。

本轮原source/false/raw/INDEX/once/reports/回放决定/automation通过此ordinarysupplement归档。控制日志fullreturned约34MB/82MB/87MB为文本报告完整归档（超Git单对象安全尺寸时按字节切片、总SHA和分片索引均记录），PT/NPZ/USD/media仅真实path/bytes/已有SHA索引，不为归档读权重/跑物理。凭据按既有redact并核数量，秘密不输出/入Git。现mod4-10 ACTIVE/hourly/samechat经工具更新至CURRENT370，无新Goal/automation。所有历史tags/peels和lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护，postGit验证只工具输出，push失败续已有objects。
''',encoding='utf8')
roots=[(P.name,P)]+[(n,T/n)for n in('MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102','MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V365_20261102','MPC_CONTACT_MANIFOLD_LANDING_AUDIT_V366_20261102','MPC_AIR_WHEEL_REQUEST_ENVELOPE_V368_20261102')]
ext=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports')
for name in('NINE_SINGLE_GPU_GROUP_STAGE_20261102_101426_1793585666425343700.json','NINE_V8_ACTUAL_PROGRESS_20261102_102304.json','NINE_SINGLE_GPU_V8_LATEST_CLOSED_RESULT_PATH.json','NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/CLOSED_RESULT.json'):
    roots.append(('resource_evidence',ext/name))
known={};identities={}
for base in(BASE,G/'versions/20261102_mod4-init311-paired317-short-h4-tracking-repair324',G/'versions/20261102_mod4-final305-recovery-eval308-targeted-repair307'):
    for p in base.rglob('*CAPTURE_INDEX*.json'):
        for r in read(p).get('files',[]):
            if r.get('SHA')and r.get('Git_path')and(G/r['Git_path']).is_file()and r.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):known.setdefault(r['SHA'],r['Git_path'])
def collect(v,receipt):
    if isinstance(v,dict):
        sha=v.get('SHA')or v.get('sha256');size=v.get('bytes')
        if isinstance(sha,str)and len(sha)==64 and all(x in'0123456789abcdef'for x in sha)and isinstance(size,int):
            for k in('path','local_path','source','remote_path'):
                if isinstance(v.get(k),str):identities.setdefault((v[k].replace('\\','/'),size),(sha,receipt))
        for q in v.values():collect(q,receipt)
    elif isinstance(v,list):
        for q in v:collect(q,receipt)
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*.json'))):
        try:collect(read(p),str(p))
        except(ValueError,UnicodeDecodeError):pass
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
V.mkdir();rows=[];heavy=[];chunkbytes=20*1024*1024
for label,root in roots:
    for p in([root]if root.is_file()else sorted(root.rglob('*'))):
        if not p.is_file()or'__pycache__'in p.parts:continue
        size=p.stat().st_size;relative=Path(label)/(p.name if root.is_file()else p.relative_to(root))
        if p.suffix.lower()in binary:
            item=identities.get((str(p).replace('\\','/'),size));heavy.append(dict(path=str(p),bytes=size,SHA=item[0]if item else'unknown:noarchiveonlybinaryhash',SHA_receipt=item[1]if item else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
        assert p.suffix.lower()in texts,str(p)
        raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8');dest=V/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        if len(data)>45*1024*1024:
            parts=[]
            for i,start in enumerate(range(0,len(data),chunkbytes)):
                b=data[start:start+chunkbytes];part=dest.with_name(dest.name+f'.part{i:03d}.txt');part.write_bytes(b);parts.append(dict(Git_path=part.relative_to(G).as_posix(),bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
            rows.append(dict(path=str(p),bytes=size,SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='full_UTF8_byte_sequence_chunked',reassemble='concatenate chunks in listed order; totalarchiveSHA verifies complete original',parts=parts));continue
        dest.write_bytes(data);gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=size,SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
        if not count:known[sha]=gp
put(V/'CAPTURE_INDEX_SUPPLEMENT371.json',dict(epoch=time.time(),existing_tag=TAG,object=OBJ,peel=PEEL,ordinary_supplement=True,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,actual363366368closed=True,no_training_GO=True,all_saved_text_reports_full_or_sameSHA_or_completechunks=True,noarchiveonlymodelreads=True))
files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
assert not git('diff','--cached','--name-only')
for i in range(0,len(files),24):git('add','--',*files[i:i+24])
git('commit','-m','Record MPC reset handoff and actual manifold successes; test feasible wheel requests')
head=git('rev-parse','HEAD');git('push','origin','HEAD:refs/heads/main')
after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())and all(remote_after.get(k)==v for k,v in remote.items())
assert remote_after['refs/tags/'+TAG]==OBJ and remote_after['refs/tags/'+TAG+'^{}']==PEEL
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,ordinary_supplement=True,HEAD=head,remote_main=head,tagobject=OBJ,peel=PEEL,alloldtagsprotected=True,lqr=lqr,files=len(files),indexed=len(rows),heavy_metadata=len(heavy),chunked_reports=sum(r['capture']=='full_UTF8_byte_sequence_chunked'for r in rows),clean=True)),flush=True)
