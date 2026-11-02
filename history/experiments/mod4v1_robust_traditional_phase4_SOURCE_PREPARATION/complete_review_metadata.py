"""Append-only final review aliases. No new capture/source/raw/Git operation."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def new(p,v):assert not p.exists();p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def meta(p):return {'path':str(p),'relative':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'SHA':sha(p)}
def main():
    assert not (P/'REVIEW_INDEX.json').exists();g=load(P/'FINAL_MISSING_AND_EXCLUSIONS.json');r=load(P/'PROVENANCE_RECONCILIATION.json');m=load(P/'FINAL_SOURCE_MANIFEST.json');entries=m['entries'];version_fixed=[];true_gaps=[];name_fixed=[];name_gaps=[]
    aliases={x['initial_event']['path'].lower():x for x in r['prior_record_repository_path_aliases']}
    for x in g['actual_missing_saved_smalltext_version_claims']:
        a=aliases.get(x['path'].lower())
        if a and a['reference']['SHA']==x['expected_SHA']:version_fixed.append({'initial_claim':x,'resolution':a['reference'],'already_verified_repository_relative_alias':True})
        else:true_gaps.append(x)
    for x in g['remaining_named_missing_or_unbound_links']:
        pieces=x['path'].replace('\\','/').split('/');suffix='/'.join(pieces[2:]);c=[e for e in entries if e['path'].replace('\\','/').endswith('/'+suffix) and e['snapshot_path'] and e['path'].replace('\\','/').startswith('F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/')]
        if len(c)==1:name_fixed.append({'initial_unversioned_link':x,'resolution':'known_closed_module_suffix_after_document_relocation','selected_path':c[0]['path'],'snapshot_path':c[0]['snapshot_path'],'SHA':c[0]['source_SHA'],'not_executed_source_version_identity':True})
        else:name_gaps.append({'event':x,'candidate_count':len(c),'not_arbitrarily_selected':True})
    new(P/'FINAL_REVIEW_GAPS.json',{'status':'APPEND_ONLY_REVIEW_ALIAS_COMPLETION_NO_SOURCE_VERSION_FABRICATION','previous_reports_unchanged':True,'four_repo_relative_version_aliases_resolved':version_fixed,'relocated_unversioned_document_links_resolved':name_fixed,'actual_missing_saved_smalltext_version_claims':true_gaps,'remaining_named_link_ambiguities':name_gaps,'raw_unknowns_unchanged':g['raw_unknowns'],'R35_unknown_consumption_and_lost_rows_not_reconstructed':True,'no_more_capture_no_scope_expansion':True,'parent_cutoff_review_required_before_Git':True})
    handoff=f'''# PH4 local source preparation — parent review入口\n\n**仅SOURCE_PREPARATION，尚无stage/commit/tag/push/recordhelper；无physics/旧once/test/compile/GPU/newagent/真实IO，sourceRoot/旧expertindex/main未改。**\n\n- [FINAL_SOURCE_MANIFEST](<FINAL_SOURCE_MANIFEST.json>)：9262原件映射，2903new text/68,499,328B，5155同bytePH1/2/3Gitrefs；1204rawmetadata(1189producerSHAknown/15unknown)。\n- [一致性receipt](<FINAL_CONSISTENCY_RECEIPT.json>)和[范围/原README](<README.md>)，所有8058text/source-snapshot对已验证，变化0/redaction0。\n- [最终review缺口表](<FINAL_REVIEW_GAPS.json>)：旧record的repo-relative不是task-relative；2147旧namespace aliases已逐SHA验证，不是2147新文件缺失。其中4条versiongap已并回同证明。另6个老revision/snapshot文档relocationlink按已纳module suffix说明，不冒executedSHA身份。实际smalltext旧version缺口{len(true_gaps)}、未定名link{len(name_gaps)}，如实保留，未用activecurrent替换。初始2226events/53claims全留未覆盖。\n- [资格/ZIP边界](<QUALIFICATION_AND_DELIVERY_BOUNDARIES.json>)：stageZIP10,725,489B，producerSHA8b5bd15b3c26db510ee353b233597332b5899e81e5cec4ef723d265dabe01288，仅metadata，未开/重hash/解包。\n- [CASE/FAILURE registry](<CASE_AND_FAILURE_REGISTRY.json>)：R36closed26+R38six+R39four=36result，R35四savedlog/config损失与R36前AST失误另保留、不伪造0/N/精确耗步。R35八0Btrace/partial仍producerSHA未知；两nativeFSM exe存在冲突producerclaim也不重hash。\n- [explicitrootallowlist](<EXPLICIT_ROOT_ALLOWLIST.json>)165root closure，非mtime盲纳；[exclusions](<EXCLUSIONS.json>)70路径/整树，R40/R41+/ROUGH_WORLD_LEG/v2mini/newround4continuation全排除。\n- [REVIEW_INDEX](<REVIEW_INDEX.json>)是包含此append-onlyaddendum的最终清单；早先FINAL_INDEX完整保留，未覆盖其任何字节。\n\nC3/HOST/H2/ASQP/nativeFSM/nativeMPC各自数学/IO/compile事实不升级board/WCET/整机资格；supervisor仍UNSEALED，stdioactiveQP仍BLOCKED/NOTSEALED且framesUNSENT，front仅staticproposal，R39不是baseline。所有失败/旧false/未知原样保存。请父reviewcutoff后另指示Git，禁止重复recordPH1/2/3，整体Goal仍active。\n'''
    (P/'REVIEW_HANDOFF.md').write_text(handoff,encoding='utf-8')
    for p in P.glob('*.md'):
        for link in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
            if link=='REVIEW_INDEX.json':continue
            assert (p.parent/link.split('#')[0]).exists(),(p,link)
    files=sorted(p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='REVIEW_INDEX.json');new(P/'REVIEW_INDEX.json',{'status':'PH4_SOURCE_ONLY_READY_FOR_PARENT_CUTOFF_REVIEW_GIT_NOT_CALLED','handoff':meta(P/'REVIEW_HANDOFF.md'),'manifest':meta(P/'FINAL_SOURCE_MANIFEST.json'),'receipt':meta(P/'FINAL_CONSISTENCY_RECEIPT.json'),'canonical_review_gaps':meta(P/'FINAL_REVIEW_GAPS.json'),'actual_smalltext_version_gaps':len(true_gaps),'remaining_named_links':len(name_gaps),'old_reports_and_indexes_unchanged':True,'Git_not_called':True,'files':[meta(p) for p in files]})
    print(json.dumps({'REVIEW_HANDOFF':meta(P/'REVIEW_HANDOFF.md'),'REVIEW_INDEX':meta(P/'REVIEW_INDEX.json'),'FINAL_REVIEW_GAPS':meta(P/'FINAL_REVIEW_GAPS.json'),'actual_smalltext_version_gaps':true_gaps,'named_link_gaps':name_gaps,'repo_version_aliases_resolved':len(version_fixed),'relocated_link_hints_resolved':len(name_fixed),'Git_calls':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
