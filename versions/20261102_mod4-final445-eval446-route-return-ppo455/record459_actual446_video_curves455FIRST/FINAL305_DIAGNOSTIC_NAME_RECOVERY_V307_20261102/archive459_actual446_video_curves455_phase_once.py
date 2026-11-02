"""Archive actual445close/446failure/video-curves/455FIRST once, protect all historical tags."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib,traceback
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports';G=T.parent/'polar-rl-train'
ID='mod4-final445-eval446-route-return-ppo455';TAG='trial-20261102-'+ID
V=G/('versions/20261102_'+ID)/'record459_actual446_video_curves455FIRST'
read=lambda p:json.loads(p.read_bytes())
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{r.split()[1]:r.split()[0]for r in s.splitlines()}
def main():
    assert not git('status','--porcelain')and git('branch','--show-current')=='main'
    assert not V.exists()and not(R/'RECORD459_ONCE_CONSUMED_BEFORE_GIT.json').exists()and not git('tag','--list',TAG)
    oldrefs=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
    assert all(remote.get(k)==v for k,v in oldrefs.items())
    lqr=git('ls-remote','origin','refs/heads/lqr').split()[0];assert lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
    assert oldrefs['refs/tags/trial-20261102-mod4-final433-eval437-saturation-ppo445']=='d4a60f4a47b341f46693802d3e7e13021b753612'
    reqpath=R/'AUTOMATION458_VIDEO_CURVES_LIVE455_SOLE456_REQUEST.json';req=read(reqpath)
    cfg=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert cfg['prompt']==req['prompt']and cfg['rrule']==req['rrule']and cfg['status']==req['status']=='ACTIVE'and cfg['target_thread_id']==req['targetThreadId']
    receipt=R/'AUTOMATION458_ACTUAL_APP_UPDATE_TOOL_RECEIPT.json';assert not read(receipt).get('isError')
    put(R/'AUTOMATION458_SAVED_CONFIG_VERIFIED.json',dict(epoch=time.time(),passed=True,requestSHA=H(reqpath),actualtoolreceiptSHA=H(receipt),samehourlyACTIVEcurrentthread=True))
    work=read(R/'CURRENT_ACTUAL458_FINAL445_EVAL446_VIDEO_CURVES_LIVE455_SOLE456_WORK_ORDER_V1.json')
    assert work['actual446']['strict']==0 and work['actual455']['FIRST']['passed']and work['sole456']['launch']['PID']==56540
    put(R/'RECORD459_ONCE_CONSUMED_BEFORE_GIT.json',dict(epoch=time.time(),phase=ID,tag=TAG,oldrefs=oldrefs,remote_before=remote,lqr=lqr,
        pushretry='Continueexistingobjectsneverrerunrecordorretag',actual445closed=True,actual446strict0=True,nativevideo_curvereview457=True,actual455FIRSTcomplete=True,sole456PID=56540,modelreads_for_archive=0))
    note=R/'RECORD459_ACTUAL446_VIDEO_CURVES_AND_455_RETURN_REPAIR.md'
    note.write_text('''人类交付明确是RL实际跳上270mm并稳定，传统MPC不是交付。最新要求详细看视频、曲线解释跳不上和偏离路线。本阶段完整保存实际445结束/446评测失败/正确451回放取回/457详细视频曲线诊断，及已启动455实际回报归因修复、唯一456收尾。仍无RL上台成功，不把FIRST/寿命改善/CPU通过称技能毕业。

445已完整fullsave安全关闭/fullformaltransfer/newfullCPU790finite。final34229331B SHA056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed，PPO=Pi=critic169/newWM5428total36159/5459controls436720ownpairs，actorAdam56634critic13694/teacher17Adam42940STD/三Adam/EMA/normRNG/savedorigin完整，原owner1482264/node1482274/worker1482287 ownwaited/private共享free。fee3604.6878695487976s/closingbalance340598.1940984726s仅历史。normal445/CPU445once已消费不重复读模型归档。

独立实际446完成80firstepisodes400controls8sseed9137新DRsamefixededge.8/270，3200physics800feedback。0strict0wholefootprintclear0leadingcross80everairborne22orientation58full8s/mean6.15125median8s/longesttopmanifold0；allownwaited/private共享released/SSHclosedSESSIONrestoredFREE。全部返回94MB JSON逐字节完整分片，不截取原失败/原raw。

446物理评测有效，但本地回放传输在dest.mkdir拒绝。450发现准备445/446误复制437replay/旧renderreports，只改名未改内容，原copiedNPZsha仍437且不等实际446sha。原source/原false/once保留，不用旧回放充当前结果，不重跑eval。451独立只将4个实际已保存NPZ取回新root、核两端SHA，共1352295B；0NN/SDK/新physics/optimizer/模型读取，原共享private准入与finallyclosedFREE完整。451回放原生view_image已审。

452保存早期yaw/pitch和creditwindow事实；453候选准备在CPU执行/learnerwrite前因metadata仍32拍静态拒绝，原source/false/unusedroot保留。454独立修齐metadata，必要final445一次CPUdecode完整restore56634/13694/36159，不reset网络或Adam。19条保存坐标/奖励行重复为128并新合成latent仅CPUfixture非新actualonpolicy；延迟57拍事件returns.5696016等于gamma^56、旧32为0，done不串下一episode；actorgrad2.14635critic4.18021/KL.0043078/delta.0333711有限，候选权重Adam全部恢复，0生产优化/SDK/physics。CUDA16BRNG保留opaqueCPUfixture另generator，生产restore同GPUactualRNG不改。454准入不是物理成功，不重复PT验模。

455在本次人类详查前已实际GO。全网络/三Adam/STDteacher/EMA/normRNG/saved389origin完整续final445，physicalDRqueue/replayfresh；实际PPO仅将rollout32改128controls2.56s和GAElambda.95改1，gamma.99/oneepochclip.2/同exp(-weightedtrackingcost/5)/actualdone/latent饱和探索floor.15gain.6cap2/postAdamfullGaussianKL<=.01maxdelta<=.05保持。WMH32独立无actorWMgradient，未来actualdepthGTmap不入imagination。actor103=35proprio9currentdepth59reference/critic106，固定347processed50Hz电机前馈+1*tanh(actor-origin)，无onlineMPC/接管/力矩cloning，非自主depth-only。不是说延长回报窗已经修好路线。

真实run ACTUAL_RESIDUAL_PPO455_1793628540456858000/owner1486968create1793628647.19/node1486977create1793628647.62/worker1486992create1793628653.76，原Popenbash和实际绑定后execidentity分开见458。GPU-c27eecbd-6838-7290-1cd2-37e34522213d；GO2026-11-02T22:10:51.156631+08，SAVE23:10:51.156631/NOMINAL23:15:51.156631/normal最早23:00:51.156631。原3900save3600exit300唯一canonicalstrictreserve未改。INDEX455SHAb8a4ce9993381fb15be3fcf2505ad8259686e574648780cefb3495f68c5bfe8f/workerSHA26a291d2ee019707f516a9c0277a8f3610f60056085071f681a94cb22fe420d2/learner454SHA00ccbf6eec797539c7f39c4cfbd39861e08ef35509c2662cb92763faa2ce84d2。

已唯一收FIRST_UPDATED，实际128controls10240ownpairs1024physics256feedback，PPO=Pi=critic1/newWM97total36256；actorgrad3.038812critic13.074018/native24通过，actualdoneGAEtrue/terminal0/actorWMgradfalse，acceptedhalfLR5e-5/KL.002595513/delta.02385843/2proposals一次commit。首完整32811065B SHAaafc1446bc5d07459e7467efec80f223f161155252e384ac037e99aedc656449/actorAdam56635critic13695WM36256。snapshot576controlsPPO4/WM36704/124orientation是训练重复episode，不是独立技能评测。健康不restart/hotpatch/重跑startup/验模/FIRST。

唯一456bind/timer已消费，localPID56540/create2026-11-02T22:17:53.666981+08/确切CIM见458。INDEX456SHAf09cdab0da5eca1c0e30e96114aedefa3f3616ef6e4fef0a4c3dcdd79c72fbf3。原normal900 localtimer/忙localwait，同一processnormal455fullsave安全退出/fulltransfer/newCPUoffsets56634/13694/36159，独立45680首episodes400controls/seed9137same270新DRactualmanifold+真实pose；新包只白名单静态source和2data，不复制旧replay/reports/frames，自索引排除自身。活timer不得第二SSH/watcher/normal/CPU/eval。最终必须当前模型原生看pose核manifold，并按457曲线对比后决定修复/续训，不原样再训一小时。

457按用户要求做详细运动归因：四例各400实际姿态帧成MP4半速、前1.52秒GIF四分之一速度、固定侧视/俯视15时刻图。当前模型原生view_image已审4例密集图及.94/.98/1/1.1/2.46s帧、全部关键曲线；无新NN/SDK/physics。将路线与参考、x/y/z和姿态/速度、左右轮target/dq、legtarget/q、named400Hz实际efforts、ground/topmanifold、奖励cost拆解逐拍对齐，输出8图/CSV/JSON/人类报告。媒体SHA在原render/plotreceipt中产生，归档只引用pathbytes已有SHA，frame原件保留不为Git读取二进制。

测量失效链：四例.18-.20s yaw过.2rad，.4s约yaw30deg/pitch22deg，早于.76s起跳。env0前20拍保存前馈左右2.008/1.896rad/s，加RL残差-7.257/+4.759后总目标-5.249/+6.655，实测-5.505/+4.004。轮距.4376m/r.0637的实际轮差积分.4s yaw30.76deg，实测31.08deg，支持电机差速造成早期偏航；后期滚动简化公式不是精确动力学。depth初始270mm/.854m，四例前20拍valid1，首次missing.44-.48s之后，不能称初始盲视；没有显式routeplanner决定绕行，6路残差形成曲线路径。

四例最高轮心仅.240-.286m，较低轮底最高估计.176-.206m，台面.270，upright轮心需约.334m；env0.76s vz1.35m/s vs参考2.26。约1.10-1.12s首次落回地面，最前轮心第一跳约x.62-.64m还没到台沿。env41/1/0轮胎首次保存的立面接触2.12/2.30/2.46s，z.0625/.0507/.0609m，非台顶。全80actualtopforce最大0。约.98-1.02s前速明显反转，未保存所有非轮接触manifold，不能排除非轮碰撞，不能把轮胎未触沿推成整机此前绝无碰撞；限制单独保留。

用记录root/q/dq/bodyposes/hipanchor/worldwheelforces重建原trackingcost，全部项均值与原eval误差<.001。env0.4s已经yaw31deg/pitch22deg仍reward.964，rotationcost贡献仅.0383；台前撑住仍~.22/拍。错路线被positioncost惩罚，不说reward奖励绕路；没有显式整轮越台/台顶manifold项，短32拍.64s GAE.95与饱和继承策略可能形成存活撑台局部解，但无Q/advantage反事实证明唯一成因。原PD/DC限幅实际存在，局部wheelcomputed17-21Nm却applied约5.776、腿局部40Nm，不据此增加PD或力矩限额。

物理400Nengineeringk2000/50policy100feedback400physics/.0025TGS32-4/fullD0whitev3D1-D7/.01单envclosure/.01mimic/原PD_DCclip_queue_solver/historicalH1资产保持；84x48暂定camera非D435i硬件标定。strict首次飞行整轮rearfootprint越沿、双轮actual400Hztopmanifold、无groundedge返回/vxyvz.03/rollpitch10deg/yaw.2rad连续.5s不改。MPC不是RL交付。345unused不启动。凭据不输出Git，finiteSSHfreshLOCALknownCIMFREE/parentCNone/private共享准入；finallySSHclosedSESSIONrestoreFREE，不抢锁清activekillunknownPIDscan。

458实际工作单和同一mod4-10 ACTIVE/currentthread真实appupdate及配置验证完整归档，silentunchanged语义保留，不新Goal/chat/automation。所有450..458原source/report/reader错/false/once/actual结果完整保存，同SHA旧报告引用原Gitpath，大UTF8按bytechunk完整重组，PT/NPZ/USD/媒体只pathbytes已有SHA。不为归档读模型/重physics。旧448objectd4a60f4a47b341f46693802d3e7e13021b753612/peel49319b0e662beaf48afb25094ba780ebfb319be7及449mainf30410178844fbd6d122922f218831b1ac095821、全部旧tags/peels/lqr5848b45a99b8c32af02eb61b507c3f95ab39e4ad保护。push失败续已有objects，不重record/retag；postGit验证只工具输出不追HEAD报告循环。
''',encoding='utf8')
    names=('RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102','RL445_SINGLE_PROCESS_POSTROUND_V446_20261102','RL445_FINAL_INDEPENDENT_EVAL_V446_20261102',
        'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102','RL_LAUNCH_LANDING_RETURN_REPAIR_V453_20261102','RL_LAUNCH_LANDING_RETURN_REPAIR_V454_20261102',
        'RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102','RL455_SINGLE_PROCESS_POSTROUND_V456_20261102','RL455_FINAL_INDEPENDENT_EVAL_V456_20261102','RL_MOTION_ROUTE_DIAGNOSIS_V457_20261102')
    roots=[(P.name,P)]+[(name,T/name)for name in names]
    known={};identities={}
    prior=[b for b in(G/'versions').iterdir()if b.is_dir()and b.name.startswith('20261102_mod4-')]
    for base in prior:
        for p in base.rglob('*CAPTURE_INDEX*.json'):
            for row in read(p).get('files',[]):
                if row.get('SHA')and row.get('Git_path')and(G/row['Git_path']).is_file()and row.get('capture')in('full_UTF8_byte_exact','full_same_SHA_reference'):
                    known.setdefault(row['SHA'],dict(Git_path=row['Git_path'],capture='full_same_SHA_reference'))
                elif row.get('SHA')and row.get('capture')in('full_UTF8_byte_sequence_chunked','full_same_SHA_chunk_sequence_reference')and row.get('redactions',0)==0:
                    assert all((G/x['Git_path']).is_file()for x in row['parts'])
                    known.setdefault(row['SHA'],dict(capture='full_same_SHA_chunk_sequence_reference',parts=row['parts'],archive_SHA=row['archive_SHA'],original_index=p.relative_to(G).as_posix()))
    def collect(v,receipt):
        if isinstance(v,dict):
            sha=v.get('SHA')or v.get('sha256');size=v.get('bytes')
            if isinstance(sha,str)and len(sha)==64 and all(c in'0123456789abcdef'for c in sha)and isinstance(size,int):
                for key in('path','local_path','source','remote_path'):
                    if isinstance(v.get(key),str):identities.setdefault((v[key].replace(chr(92),'/'),size),(sha,receipt))
            for x in v.values():collect(x,receipt)
        elif isinstance(v,list):
            for x in v:collect(x,receipt)
    for label,root in roots:
        assert root.exists(),str(root)
        for p in sorted(root.rglob('*.json')):
            try:collect(read(p),str(p))
            except(ValueError,UnicodeDecodeError):pass
    sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
    binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.gif','.usd','.usda','.usdc','.stl','.obj','.zip','.gz','.pyc'}
    texts={'.py','.json','.md','.txt','.log','.xml','.toml','.sh','.ps1','.csv','.tsv','.yaml','.yml'}
    V.mkdir(parents=True);(V/'.gitattributes').write_text('* -text\n',encoding='utf8');rows=[];heavy=[]
    for label,root in roots:
        for p in sorted(root.rglob('*')):
            if not p.is_file()or'__pycache__'in p.parts:continue
            size=p.stat().st_size;relative=Path(label)/p.relative_to(root)
            if p.suffix.lower()in binary:
                item=identities.get((str(p).replace(chr(92),'/'),size));heavy.append(dict(path=str(p),bytes=size,SHA=item[0]if item else'unknown:noarchiveonlybinaryhash',SHA_receipt=item[1]if item else None,capture='metadata_only_no_content_or_hash_for_Git'));continue
            assert p.suffix.lower()in texts,str(p)
            raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
            if sha in known:rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,**known[sha]));continue
            safe,count=redact(raw.decode('utf8'));data=raw if count==0 else safe.encode('utf8');dest=V/relative;dest.parent.mkdir(parents=True,exist_ok=True)
            if len(data)>45*1024*1024:
                parts=[]
                for i,start in enumerate(range(0,len(data),20*1024*1024)):
                    part=data[start:start+20*1024*1024];target=dest.with_name(dest.name+f'.part{i:03d}.txt');target.write_bytes(part);parts.append(dict(Git_path=target.relative_to(G).as_posix(),bytes=len(part),SHA=hashlib.sha256(part).hexdigest()))
                row=dict(path=str(p),bytes=len(raw),SHA=sha,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='full_UTF8_byte_sequence_chunked',parts=parts,reassemble='ConcatenateallpartsandverifytotalarchiveSHA');rows.append(row)
                if not count:known[sha]=dict(capture='full_same_SHA_chunk_sequence_reference',parts=parts,archive_SHA=row['archive_SHA'])
                continue
            dest.write_bytes(data);gp=dest.relative_to(G).as_posix();rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(data).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
            if not count:known[sha]=dict(Git_path=gp,capture='full_same_SHA_reference')
    put(V/'CAPTURE_INDEX_RECORD459.json',dict(epoch=time.time(),phase=ID,files=rows,large_artifacts=heavy,oldrefs=oldrefs,remote_before=remote,lqr=lqr,
        all_saved_text_full_or_sameSHA_or_completechunks=True,actual445close_CPU=True,actual446strict0=True,native457video_curves_review=True,actual455GOFIRST=True,sole456PID=56540,no_modelreads_for_archive=True))
    files=[p.relative_to(G).as_posix()for p in sorted(V.rglob('*'))if p.is_file()]
    import record_experiment
    original_git=record_experiment.git
    def exact_directory_add(*args):
        if len(args)>=2 and args[:2]==('add','--'):
            record=args[2];selected=set(args[3:]);assert selected==set(files)
            result=original_git('add','--',record,V.relative_to(G).as_posix());assert set(original_git('diff','--cached','--name-only').splitlines())==selected|{record};return result
        return original_git(*args)
    record_experiment.git=exact_directory_add
    sys.argv=['record_experiment.py','--id',ID,'--title','Diagnose RL445 actual failed route from video and curves; start actual128-return PPO455','--kind','repair','--note-file',str(note),
        '--validation','445fullcloseCPU790;446actual0of80topforce0;451verifiedrecordedposes;457densevideo_native_review/actioncostcurves;453staticfalse;454CPUfixture;455actualFIRST10240samplesfullsave;sole456timer','--files',*files]
    record_experiment.main()
    head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}');assert peel==head
    git('push','--atomic','origin','HEAD:refs/heads/main','refs/tags/'+TAG)
    after=refs(git('show-ref','--tags','-d'));remote_after=refs(git('ls-remote','--tags','origin'))
    assert all(after.get(k)==v and remote_after.get(k)==v for k,v in oldrefs.items())and all(remote_after.get(k)==v for k,v in remote.items())
    assert remote_after['refs/tags/'+TAG]==obj and remote_after['refs/tags/'+TAG+'^{}']==head
    assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==lqr
    assert not git('status','--porcelain')
    print(json.dumps(dict(passed=True,HEAD=head,remote_main=head,tag=TAG,tagobject=obj,peel=peel,files=len(files),indexed=len(rows),large_metadata=len(heavy),oldrefsprotected=True,lqr=lqr,clean=True,actual455FIRST=True,sole456PID=56540)),flush=True)
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('RECORD459_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),preserve_existing_objects=True,no_rerun_record_or_retag=True));raise
