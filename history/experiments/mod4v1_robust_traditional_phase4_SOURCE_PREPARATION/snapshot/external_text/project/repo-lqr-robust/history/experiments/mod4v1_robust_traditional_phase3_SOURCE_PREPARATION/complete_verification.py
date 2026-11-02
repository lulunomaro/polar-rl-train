"""Append-only final completion of metadata/link checks after admin NameError.
No recapture, prior file overwrite, raw content read, model/test or Git call.
"""
from pathlib import Path
import datetime,hashlib,json,re
P=Path(__file__).resolve().parent;WT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,obj):assert not p.exists(),str(p);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'relative':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'SHA':sha(p)}
def main():
    assert not (P/'FINAL_INDEX.json').exists()
    manifest=load(P/'FINAL_SOURCE_MANIFEST.json');receipt=load(P/'FINAL_CONSISTENCY_RECEIPT.json');initial_index=load(P/'INDEX.json');count=0;future=[]
    assert receipt['actual_unresolved_in_scope_source_versions']==0 and receipt['Git_stage_commit_tag_push_or_recordhelper_calls']==0
    for e in manifest['entries']:
        if e['snapshot_path']:
            assert sha(WT/e['snapshot_path'])==e['snapshot_SHA'];count+=1
            st=Path(e['path']).stat()
            if (st.st_size,st.st_mtime_ns)!=(e['bytes'],e['mtime_ns']):future.append({'path':e['path'],'captured_SHA':e['source_SHA'],'note':'future_version_not_replaced_or_recaptured'})
    for e in initial_index['files']:assert sha(Path(e['path']))==e['SHA'],'initial metadata changed after finalizer attempt'
    errors=[{'path':str(P/'PREPARATION_FAILURE_001.txt'),'SHA':sha(P/'PREPARATION_FAILURE_001.txt'),'source_SHA':'f40c3ffea5ffef4edb90087ba605ad9c24cf62d9bd29b767a9737ca06c488efc','kind':'parse-time archive helper implementation error no data run'}, {'path':str(P/'PREPARATION_FAILURE_002.txt'),'SHA':sha(P/'PREPARATION_FAILURE_002.txt'),'source_SHA':'14ef72fd3c4eccecd5163cca9fe1f4269c50ccde1c816436ae03fc6acfab42ed','kind':'post-metadata link-check missing re import; no payload corruption; main not replayed'}]
    handoff='''# FINAL HANDOFF — PH3 source snapshot封好，Git仍等待\n\n**本目录只SOURCE_PREPARATION，未stage/commit/tag/push/recordhelper，未写sourceRoot/原expertindex/main，0physics/旧test/GPU/newagent/真实IO。**\n\n主入口：[最终source manifest](<FINAL_SOURCE_MANIFEST.json>)、[最终缺失/排除](<FINAL_MISSING_AND_EXCLUSIONS.json>)、[source一致性收据](<FINAL_CONSISTENCY_RECEIPT.json>)、[补齐验证收据](<COMPLETION_VERIFICATION_RECEIPT.json>)、[FINAL_INDEX](<FINAL_INDEX.json>)。\n\n3229源条目，2119新text/15,173,369B、441既有PH1/2Git引用；669raw仅metadata，其中665已有producerSHA、4unknown；270R17–R34物理result、4R25软件ERROR、22batch/abort报告。explicit根闭包与active排除表齐全，没有mtime盲纳。\n\n[初始README](<README.md>)保留详细语义。初始INDEX写出后最终linkchecker因漏import re出现[admin002](<PREPARATION_FAILURE_002.txt>)；未重跑main或覆盖旧metadata，改由本append-only completion核对所有payload/原index SHA和链接。本收据及FINAL_INDEX才标识最终验证结束。另[admin001](<PREPARATION_FAILURE_001.txt>)原归档脚本SyntaxError也连原sourceSHA保留。它们不是模型/机器人失败。\n\n[关联erratum](<PROVENANCE_ASSOCIATION_ERRATUM.json>)保存六个objectSHA误关联source.C及四个basename metadata假缺失，canonical实际in-scope source缺口0。历史Desktop XML只线索未外扩读取，R25缺轨迹不重建，CONT_R34的R35后段仅handoff，R35+实验/heading/streamed/FRONT/ACTIVEBOX全排除。\n\n所有待Git：后续新phase3trial须父另行确认；不重record Phase1/2，整体Goal保持active。\n'''
    (P/'FINAL_HANDOFF.md').write_text(handoff,encoding='utf-8')
    completion={'status':'COMPLETE_LOCAL_SOURCE_SNAPSHOT_VERIFIED_WAIT_GIT','verified_text_SHA_pairs':count,'initial_source_manifest_preserved_SHA':sha(P/'SOURCE_MANIFEST.json'),'canonical_source_manifest_SHA':sha(P/'FINAL_SOURCE_MANIFEST.json'),'prior_index_generated_before_link_error_SHA':sha(P/'INDEX.json'),'all_initial_index_file_SHA_unchanged':True,'actual_in_scope_unresolved_source_versions':0,'unknown_raw_SHA':receipt['unknown_raw_SHA'],'administrative_errors_preserved':errors,'future_source_versions_observed_not_substituted':future,'sourceRoot_writes':False,'Git_stage_commit_tag_push_record_calls':0,'physics_tests_GPU_newagents_realIO':False,'original_expert_index_main_writes':False,'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    # All links are checked after creating every referenced metadata file. The
    # final index is excluded until it exists, then checked in a final pass.
    new(P/'COMPLETION_VERIFICATION_RECEIPT.json',completion)
    files=sorted(p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='FINAL_INDEX.json')
    new(P/'FINAL_INDEX.json',{'name':'PH3_SOURCE_PREPARATION','status':'LOCALLY_SEALED_SOURCE_SNAPSHOT_COMPLETE_GIT_NOT_CALLED','primary_handoff':meta(P/'FINAL_HANDOFF.md'),'manifest':meta(P/'FINAL_SOURCE_MANIFEST.json'),'consistency_receipt':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'completion_receipt':meta(P/'COMPLETION_VERIFICATION_RECEIPT.json'),'original_index_and_errors_preserved':True,'through_R34_only':True,'Git_pending_no_stage_commit_tag_push':True,'files':[meta(p) for p in files]})
    links=0
    for p in P.glob('*.md'):
        for link in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):assert (p.parent/link.split('#')[0]).exists(),(p,link);links+=1
    print(json.dumps({'locally_sealed':True,'FINAL_HANDOFF':meta(P/'FINAL_HANDOFF.md'),'FINAL_INDEX':meta(P/'FINAL_INDEX.json'),'FINAL_SOURCE_MANIFEST':meta(P/'FINAL_SOURCE_MANIFEST.json'),'COMPLETION_RECEIPT':meta(P/'COMPLETION_VERIFICATION_RECEIPT.json'),'source_summary':manifest['summary'],'verified_text_SHA_pairs':count,'links_checked':links,'Git_calls':0,'actual_source_gaps':0,'unknown_raw_SHA':receipt['unknown_raw_SHA']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
