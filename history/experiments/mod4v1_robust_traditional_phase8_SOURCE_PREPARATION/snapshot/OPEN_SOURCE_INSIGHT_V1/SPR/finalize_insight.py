"""One saved-evidence metadata seal; no source execution/ZIP reopening/QA."""
from pathlib import Path
import json,hashlib,re,urllib.parse
O=Path(__file__).resolve().parent

def load(n):return json.loads((O/n).read_bytes())
def record(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
m=load('SELECTED_SOURCE_MANIFEST.json');c=load('CENTRAL_CURRENT.json')
assert m['selected_files']==len(m['selected'])==28
assert m['new_text_bytes_written']==218234<=m['max_text_total']==12582912
assert m['large_zip_hashes']==m['code_or_readme_commands_executed']==c['nested_payload_reads']==0
now=Path(c['archive']['path']).stat();assert now.st_size==c['archive']['bytes']and now.st_mtime_ns==c['archive']['mtime_ns']
assert len({r['member'].casefold()for r in c['members']})==len(c['members'])==21
assert all(r['safe_relative_non_symlink']for r in c['members'])
oldrefs=[]
for r in m['prior_metadata_refs']:
    actual=record(Path(r['path']));assert actual==r;oldrefs.append(actual)
files=[];oldtext=0
for r in m['selected']:
    p=Path(r['path']);assert p.resolve().is_relative_to(O.resolve())
    a=record(p);assert a['SHA']==r['readable_SHA']and a['bytes']<=1048576
    if r['container_archive']is not None:
        prev=record(Path(r['prior_path']));assert prev['SHA']==r['readable_SHA']and prev['bytes']==r['readable_bytes'];oldtext+=1
    files.append(a)
assert oldtext==27 and sum(r['bytes']for r in files)==218234
# Selected-case uniqueness in the saved prior inner directory; do not reopen nested payload.
inner=json.loads(Path(next(r['path']for r in oldrefs if Path(r['path']).name=='chassis_central_index.json')).read_bytes())
for r in m['selected']:
    if r['container_archive']is not None:assert sum(i['member'].casefold()==r['member'].casefold()for i in inner['members'])==1
rp=O/'REPORT.md';text=rp.read_text(encoding='utf-8');lines=text.splitlines();assert len(lines)<=120
links=[]
for match in re.finditer(r'\]\(<([^>]+)>\)',text):
    raw=match.group(1);path,_,anchor=raw.partition('#');p=Path(urllib.parse.unquote(path)).resolve()
    assert p.is_relative_to(O.resolve())and p.is_file(),raw
    if anchor:
        lm=re.fullmatch(r'L(\d+)(?:-L(\d+))?',anchor);assert lm,raw
        lo=int(lm[1]);hi=int(lm[2]or lm[1]);assert 1<=lo<=hi<=len(p.read_text(encoding='utf-8-sig').splitlines()),raw
    links.append(raw)
report=record(rp);primaries=[record(O/n)for n in['REPORT.md','SCOPE.json','SELECTED_SOURCE_MANIFEST.json','CENTRAL_CURRENT.json','inspect_select.py','selection_01.log','finalize_insight.py']]
receipt=dict(status='SEALED_STATIC_SOURCE_INSIGHT_PRIOR_TEXT_REUSE_NOT_TRANSFER_OR_DYNAMIC_QUALIFICATION',report_lines=len(lines),report=report,selected_files=28,text_bytes=218234,report_links_verified=len(links),current_outer_central_entries=21,all_current_outer_metadata_equal_prior=True,chassis_container=dict(bytes=122201554,crc32='24706a7e'),current_nested_payload_reread=False,current_nested_payload_SHA_recomputed=False,whole_archive_SHA_recomputed=False,current_outer_readme_direct_bytes=1450,prior_readable_texts_reverified=oldtext,prior_metadata_reverified=oldrefs,source_snapshots=files,primaries=primaries,source_evidence_boundary='Current container size/CRC metadata matched prior audit; selected readable bytes match audited SHA with prior original member producer SHA/CRC/encoding retained. No fresh nested-payload cryptographic revalidation claimed.',analysis='Actual source read with read tool; call sites vs stubs/comments distinguished; 5 mechanisms plus reconstruction boundaries and minimum unexecuted proposals.',not_performed=['contained script/build/macro/README command execution','PHY/model/train/oldQA/compilation','Git/agents/goal/memory changes','oldraw/H5/large asset scan','old source/controller/gain/score edits','new contact/actuation/270 qualification'],PH8='pending',other_calibration_and_h002_default_off='unchanged')
with(O/'RECEIPT.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=receipt['status'],report=report,report_lines=len(lines),verified_links=len(links),selected_files=28,text_bytes=218234,manifest=record(O/'SELECTED_SOURCE_MANIFEST.json'),receipt=record(O/'RECEIPT.json')),ensure_ascii=False,indent=2))
