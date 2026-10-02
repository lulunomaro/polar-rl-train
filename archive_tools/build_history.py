"""Build a retrospective experiment catalog without fabricating deployment/results."""
from pathlib import Path
import collections
from datetime import datetime, timezone, timedelta
import difflib
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
TZ=timezone(timedelta(hours=8))
SKIP_SEGMENTS={'refs','reference_scut','source_current','.pytest_cache','source_snapshot','src_snapshot',
               'spin_source_snapshot','mild_source_snapshot','snapshot','assets','data','deploy','asset'}
RECORD_WORDS=('report','eval','result','probe','trial','baseline','comparison','audit','acceptance','readback',
              'decision','recovery','repair','fix','receipt','preflight','runtime','verification','diagnos',
              'handover','production_started','production_verified','parameter','benchmark','findings',
              'smoke','summary','scaling','invalid','ab_','_ab','limit_change','applied')
DOC_WORDS=('diagnos','experiment','findings','audit','decision','recovery','repair','fix','summary','scaling','_ab_')

def load_entry(e):
    return (ROOT/e['object_path']).read_text(encoding='utf8',errors='replace')

def date_for(e,data=None):
    path=e['relative_path']
    match=re.search(r'20(\d{2})[-_]?(\d{2})[-_]?(\d{2})',path)
    if not match:match=re.search(r'20(\d{2})[-_]?(\d{2})[-_]?(\d{2})',e['stage'])
    if match:
        try:return datetime.strptime('20'+''.join(match.groups()),'%Y%m%d').strftime('%Y%m%d'),'path_date'
        except ValueError:pass
    return datetime.fromtimestamp(e['mtime_epoch'],TZ).strftime('%Y%m%d'),'captured_source_mtime'

def flatten_scalars(data,prefix='',depth=0):
    output={}
    if depth>3 or not isinstance(data,dict):return output
    for k,v in data.items():
        name=prefix+k
        if isinstance(v,dict):output.update(flatten_scalars(v,name+'.',depth+1))
        elif isinstance(v,(str,int,float,bool)) or v is None:
            if (isinstance(v,bool) or any(t in name.lower() for t in
                ('status','reason','error','checkpoint','iteration','seed','seconds','num_env','limit','cap',
                 'nonfinite','closure','mimic','elapsed','sampling','stage','profile'))):
                if not isinstance(v,str) or len(v)<500:output[name]=v
    return output

def classify(e):
    p=Path(e['relative_path']);low=e['relative_path'].lower();parts=set(p.parts)
    if p.name=='run_manifest.json':return 'training_run_configuration'
    if any(marker in p.name.lower() for marker in ('.py.','.json.','.sh.','.yaml.','.m.','.xml.')):
        return 'preserved_source_variant'
    if parts & SKIP_SEGMENTS or low.startswith(('source/','incoming/','train/deploy/')):return None
    if p.name.lower() in ('status.json','next_ai_tasks.json','reset_bank.json','env.json','cpu_validation.json',
                          'package.json','package-lock.json','shasums.json','sha256sums.json'):return None
    if any(t in p.name.lower() for t in ('source_freeze','source_inventory','sha256sum','source_fingerprint',
                                        'source_difference','source_manifest','ledger_before','status_before')):return None
    if p.suffix=='.json' and (any(w in p.name.lower() for w in RECORD_WORDS) or
                                any(w in '/'.join(p.parts[:-1]).lower() for w in ('reports','results','eval'))):
        return 'recorded_evaluation_or_verification'
    if p.suffix=='.md' and any(w in p.name.lower() for w in DOC_WORDS):return 'documented_repair_or_diagnosis'
    if p.suffix=='.log' and any(w in p.name.lower() for w in ('preflight','probe','eval','retry','supervisor')):
        text=load_entry(e)
        if any(w in text for w in ('Traceback (most recent call last)','SameFileError','CUDA out of memory','ModuleNotFoundError')):
            return 'preserved_failed_execution_log'
    return None

def stage_topic(name):
    n=name.lower()
    if 'deepseek' in n:return '其他 AI 留存试验：延长训练、奖励/PD/动作幅度与观测噪声对照；作者以原文声明为准'
    if 'native_floor_fix' in n:return '同策略地板对照与原生 Plane 修复；保留无效过滤探针和未部署限速替代方案'
    if 'native_floor' in n:return '原生 Plane 续训、完整检查点恢复和有效训练预算记账'
    if 'integrated' in n or 'sampling' in n:return '接触漏采诊断与 0.5ms 冲量 / 5ms 均力历史适配；旧统计保留为影子'
    if 'contact_probe' in n:return '冻结权重高速子步接触探针及 solver 对照，保留实际卸载/间隙/滑移'
    if 'backward' in n:return '倒车异常复现、真实地面接触与单因素对照'
    if 'rescue' in n:return '平地真实地面高度、SCUT 指数分母和完整闭链复位修复'
    if 'speed_repair' in n:return '移除意外偏航课程覆盖、直线提速与接触/轮网格/腿保持对照'
    if 'spin_rate' in n:return '纯自转 3→4→6…rad/s 阶梯、保存边界晋级与归档/控制目录修复'
    if 'spin_stage' in n:return '左右 1–2rad/s 持续自转、启停反转和原站跑回归'
    if 'sensor' in n or 'sim2real' in n:return '传感器噪声/延迟隔离候选与 off/on 配对；未通过项保留，不等同正式部署'
    if 'mild_dr' in n:return 'white_v1 轻 DR：质量惯量、主轮摩擦、六电机输出；参数回读与名义配对'
    if 'fps_turn' in n:return '普通低速转弯冻结候选与 FPS 操控需求；先验收现有泛化，再决定是否新增训练'
    if 'translation' in n or 'moving' in n:return '低速自转世界定向净进度候选；数学/SDK 准备不等同技能毕业'
    if 'rough' in n:return '固定 SCUT 提交的 Rough v1 来源/配方、地面查询与隔离适配；未完成项明确保留'
    if 'budget' in n:return '用户授权预算扩展与唯一 canonical 账本运行时修复，禁止重复应用'
    if 'restart' in n or 'audit' in n:return '接管/重启/运行状态审计及此前推断的纠正'
    if 'local' in n or 'onnx' in n or 'replay' in n:return '本机模型拉取、交互操控、Isaac 真策略与 MuJoCo 姿态显示/播放器维护'
    if 'takeover' in n:return '早期 RMUC/平地多个修复版本、材料容量、弹簧/强姿态/高度实验与完整训练快照'
    if 'candidate' in n or n.startswith('exp_'):return '早期候选/独立对照：具体改动与有效结果以配置、报告和日志为准'
    return '项目来源、修复交接或历史试验资料；部署与结果仅按保存证据判断'

def main():
    inventory=json.loads((ROOT/'provenance/capture_inventory.json').read_text(encoding='utf8'))
    entries=inventory['entries'];captured=[e for e in entries if e['captured']]
    by_stage=collections.defaultdict(list);by_path={}
    for e in captured:by_stage[e['stage_id']].append(e);by_path[(e['site'],e['stage'],e['relative_path'])]=e
    # Prefer remote originals over copied local handoff duplicates, while preserving all origins.
    candidates=collections.defaultdict(list)
    for e in captured:
        kind=classify(e)
        if kind:candidates[(kind,e['object_sha256'])].append(e)
    events=[]
    for (kind,sha),origins in candidates.items():
        origins.sort(key=lambda e:(e['site']!='remote',len(e['relative_path']),e['stage']))
        e=origins[0];data=None;text=None
        if Path(e['relative_path']).suffix=='.json':
            try:data=json.loads(load_entry(e))
            except (ValueError,TypeError):pass
        if kind.startswith('documented'):text=load_entry(e)
        date,db=date_for(e,data)
        title=Path(e['relative_path']).stem
        if isinstance(data,dict) and kind=='training_run_configuration':title=str(data.get('run_name',title))
        if text:
            first=next((line.strip('# ').strip() for line in text.splitlines() if line.strip()),title)
            title=first[:140]
        event={'schema_version':1,'kind':kind,'title':title,'historical_date':date,'date_basis':db,
               'primary_stage':e['stage_id'],'primary_evidence':e['repository_path'],'evidence_object_sha256':sha,
               'all_evidence_origins':[x['repository_path'] for x in origins],
               'historical_author':'Unknown unless stated in linked original evidence; archived by lulunomaro/Codex.',
               'recording_semantics':'Retrospective evidence record created now; not an original historical Git commit.',
               'repair_context':stage_topic(e['stage']),
               'deployment_claim':'Not inferred from filename, iteration count, directory name or a pass flag.',
               'version_evidence':{'level':'stage_source_at_archive_time','stage_index':f"history/stages/{e['stage_id']}.json"}}
        parent=Path(e['relative_path']).parent.as_posix()
        snap=[x['repository_path'] for x in by_stage[e['stage_id']] if
               x['relative_path'].startswith(parent+'/') and any(v in x['relative_path'] for v in
                   ('src_snapshot/','source_snapshot/','spin_source_snapshot/','mild_source_snapshot/'))]
        if kind=='training_run_configuration' and snap:
            event['version_evidence'].update(level='preserved_run_source_snapshot',snapshot_paths=snap)
        if isinstance(data,dict):
            event['observed_fields']=flatten_scalars(data)
            if 'env' in data and isinstance(data['env'],dict):event['training_env']=data['env']
            if 'src_sha256' in data:event['recorded_source_hashes']=data['src_sha256']
            if 'groups' in data and isinstance(data['groups'],list):
                event['group_results']=[{k:v for k,v in g.items() if isinstance(v,(str,bool,int,float)) and
                    any(w in k.lower() for w in ('command','yaw','error','tilt','height','strict','survival','stop','skill'))}
                    for g in data['groups'] if isinstance(g,dict)]
            if data.get('reused_frozen_baseline'):event['baseline_reuse']=True
        if kind=='preserved_source_variant':
            base=re.split(r'\.(?=py\.|json\.|sh\.|yaml\.|m\.|xml\.)',e['relative_path'],maxsplit=1)
            # Preserve the original extension, strip only the backup suffix.
            match=re.match(r'^(.*\.(?:py|json|sh|yaml|m|xml))\..+$',e['relative_path'])
            now=by_path.get((e['site'],e['stage'],match.group(1))) if match else None
            event['version_evidence']['level']='preserved_backup_variant'
            if now and not now['binary']:
                before=load_entry(e);after=load_entry(now)
                diff=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                            fromfile=e['relative_path'],tofile=now['relative_path']))
                if not diff:continue
                event['comparison_to_captured_current']={'path':now['repository_path'],
                    'sha256':now['object_sha256'],'not_a_proven_single_chronological_repair':True}
                event['_diff']=diff
        events.append(event)
    events.sort(key=lambda e:(e['historical_date'],e['primary_stage'],e['primary_evidence'],e['kind']))
    previous_runs={}
    for e in events:
        if e['kind']!='training_run_configuration' or 'training_env' not in e:continue
        previous=previous_runs.get(e['primary_stage'])
        if previous:
            before=previous['training_env'];after=e['training_env']
            delta={k:{'before':before.get(k),'after':after.get(k)} for k in sorted(before.keys()|after.keys())
                   if before.get(k)!=after.get(k)}
            e['configuration_comparison']={'previous_record':previous['primary_evidence'],
                 'relationship':'Chronological catalog neighbor in the same archived folder; not proof of parent checkpoint.',
                 'changed_environment_values':delta}
        previous_runs[e['primary_stage']]=e
    (ROOT/'history/experiments').mkdir(parents=True,exist_ok=True)
    (ROOT/'history/diffs').mkdir(parents=True,exist_ok=True)
    counters=collections.Counter()
    for e in events:
        date=e['historical_date'];counters[date]+=1
        slug=re.sub('[^a-z0-9]+','-',Path(e['primary_evidence']).stem.lower()).strip('-')[:52] or e['kind'].replace('_','-')
        e['id']=f"{date}-{counters[date]:04d}-{slug}"
        e['tag']='trial-'+e['id']
        if '_diff' in e:
            path='history/diffs/'+e['id']+'.diff';(ROOT/path).write_text(e.pop('_diff'),encoding='utf8')
            e['comparison_to_captured_current']['diff_path']=path
        path='history/experiments/'+e['id']+'.json';e['record_path']=path
        (ROOT/path).write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'history/experiments.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events),encoding='utf8')
    # Checkpoints remain external; preserve recorded hash claims separately from newly measured hashes.
    checkpoints=[e for e in entries if Path(e['relative_path']).suffix.lower() in {'.pt','.pth','.onnx'}]
    hashes={}
    def inspect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if isinstance(v,str) and v.endswith(('.pt','.pth','.onnx')):
                    possible=[value.get(k+'_sha256'),value.get(k.replace('_path','')+'_sha256')]
                    if k in ('path','checkpoint','checkpoint_path','model_path'):
                        possible.append(value.get('sha256'))
                    for digest in possible:
                        if isinstance(digest,str) and re.fullmatch('[a-fA-F0-9]{64}',digest):
                            hashes.setdefault(v.replace('\\','/'),set()).add(digest.lower())
                inspect(v)
        elif isinstance(value,list):
            for x in value:inspect(x)
    for e in captured:
        if e['relative_path'].endswith('.json') and e['captured_bytes']<5_000_000:
            try:inspect(json.loads(load_entry(e)))
            except (ValueError,TypeError):pass
    for e in checkpoints:
        e['previously_recorded_sha256_candidates']=sorted(hashes.get(e['source_path'].replace('\\','/'),set()))
        e['hash_status']='previously_recorded_not_rehashed_for_archive' if e['previously_recorded_sha256_candidates'] else 'not_available_in_discovered_receipts'
    (ROOT/'provenance/checkpoints.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in checkpoints),encoding='utf8')
    stages=json.loads((ROOT/'history/stages.json').read_text(encoding='utf8'))
    stage_lines=['# 版本与修复目录','', '每个目录均有 `version-*` 注释标签。原始来源分为本机/目标机；历史作者未知时不猜测。','',
                 '|版本目录|修复/试验范围|捕获/索引文件|','|---|---|---|']
    for s in stages:
        docs=[e['repository_path'] for e in by_stage[s['id']] if e['relative_path'].endswith('.md') and
              len(Path(e['relative_path']).parts)<3]
        summary={'stage_id':s['id'],'repair_context':stage_topic(s['name']),'linked_original_documents':docs,
                 'experiment_ids':[e['id'] for e in events if e['primary_stage']==s['id']],
                 'limitations':'This folder is an archive capture. Per-run saved snapshots, if available, establish historical source; unrecorded changes and authors cannot be reconstructed.'}
        path=f"history/stages/{s['id']}.summary.json";(ROOT/path).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
        stage_lines.append(f"|[{s['id']}](stages/{s['id']}.summary.json)|{summary['repair_context']}|{s['files_captured']}/{s['files_indexed']}|")
    (ROOT/'history/VERSIONS.md').write_text('\n'.join(stage_lines)+'\n',encoding='utf8')
    index=['# 全部已发现的试验、修复与训练记录','',
           '这些标签是本次补建的历史证据索引。原日期按记录路径或文件元数据标注；提交时间保持真实归档时间。',
           '评测、CPU 验证、失败程序、备份源码和训练运行分别标明，不把准备/短验收当正式开训或毕业。','',
           '|日期|标签|类别|记录|','|---|---|---|---|']
    for e in events:
        title=e['title'].replace('|','\\|').replace('\n',' ')[:150]
        index.append(f"|{e['historical_date']}|`{e['tag']}`|{e['kind']}|[{title}](experiments/{e['id']}.json)|")
    (ROOT/'history/INDEX.md').write_text('\n'.join(index)+'\n',encoding='utf8')
    stats={'stages':len(stages),'indexed_files':len(entries),'captured_files':len(captured),
           'unique_objects':len({e['object_sha256'] for e in captured}),'experiment_tags':len(events),
           'event_kinds':dict(collections.Counter(e['kind'] for e in events)),
           'external_checkpoints':len(checkpoints),'redacted_files':sum(e.get('redactions',0)>0 for e in captured),
           'moving_files':sum(not e.get('stable_during_read',True) for e in captured),
           'log_excerpts':sum(e.get('capture_kind','').startswith('head_') for e in captured),
           'source_capture_errors':len(inventory['errors'])}
    (ROOT/'provenance/archive_statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(stats,ensure_ascii=False))

if __name__=='__main__':main()
