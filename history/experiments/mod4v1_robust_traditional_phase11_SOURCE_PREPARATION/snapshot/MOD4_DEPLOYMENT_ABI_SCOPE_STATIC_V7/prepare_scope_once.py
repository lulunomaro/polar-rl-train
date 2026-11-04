"""V7 metadata freeze only: exact viewed official excerpts + six old small input hashes."""
from pathlib import Path
import hashlib, json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
V6=ROOT/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'
SPILL=Path(r'C:\Users\lulu\AppData\Local\Temp\dsh-spill-N99Hsy\session-de481967f16c')
DOCS=[('addenda32','b05f59045648-web_fetch.txt','https://raw.githubusercontent.com/ARM-software/abi-aa/main/addenda32/addenda32.rst',[(10,11),(789,827),(833,837),(888,904),(909,917),(924,963),(1349,1364),(1393,1401),(1687,1703)]),('aaelf32','beaf707652ab-web_fetch.txt','https://raw.githubusercontent.com/ARM-software/abi-aa/main/aaelf32/aaelf32.rst',[(10,11),(1251,1286)])]
def digest(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'SHA256':hashlib.sha256(b).hexdigest()}
def out(name, data):
 with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 refs=[]
 for n in ['objects/001_main.c.o','logs/first_object.fromelf.stdout.log','elf_attrs_v3.py','FIRST_OBJECT_GATE_V6_01.json','EXECUTION_LEDGER_V6_01.jsonl','COMPILE_RESULT_V6_01.json']:
  p=V6/n;assert p.is_file() and p.stat().st_size<=65536;refs.append(digest(p))
 assert refs[0]['bytes']==7804 and refs[0]['SHA256']=='8f39c7f715a84fd46df710a19ec69309677b0014c542f555285527247b1a1f51'
 assert refs[1]['bytes']==16518 and refs[1]['SHA256']=='4e2ec26cf6093f45a2a49de8b71e00ae7939f4339c1a4274477ed220095bc9e4'
 assert refs[2]['bytes']==2334 and refs[2]['SHA256']=='0f261003728e7e734378e2d9b77e215b7c5fe4e4b5a22ee24cfb10d333f2e585'
 evidence=[]
 for key,filename,url,ranges in DOCS:
  b=(SPILL/filename).read_bytes();lines=b.decode('utf-8').splitlines()
  assert '2026Q3' in lines[9] and 'November 2026' in lines[10]
  evidence.append({'document':key,'official_raw_URL':url,'official_rendered_URL':url.replace('https://raw.githubusercontent.com/ARM-software/abi-aa/main/','https://github.com/ARM-software/abi-aa/blob/main/'),'declared_release':'2026Q3','declared_issue_date':'2026-11-03','fetched_by':'host web_fetch HTTP 200 before reader implementation','commit_pinned':False,'formatted_fetch_receipt_SHA256_not_raw_rst_SHA256':hashlib.sha256(b).hexdigest(),'excerpts':[{'formatted_receipt_lines':[a,z],'quote':'\n'.join(lines[a-1:z])}for a,z in ranges]})
 out('OFFICIAL_RULES.json',{'license':'Arm source documents: CC-BY-SA-4.0 AND Apache-Patent-License; exact excerpts attributed to linked official documents','documents':evidence,'interpretation':'Public hierarchy honored voluntarily despite r2.09 deprecation. Omission means ABI zero absent nodefaults, not observed compiler default. Private vendor bytes remain opaque.'})
 out('INPUT_SNAPSHOT.json',{'old_read_only_inputs':refs,'method':digest(HERE/'METHOD.md'),'official_rules':digest(HERE/'OFFICIAL_RULES.json'),'new_fixture_blob_limit':4,'old_reader_executed':False,'ARM_native_compile_probe_link_invocations':0,'V6_original_compiler_success_count':1,'V6_original_post_ABI_accepted_prefix_count':0})
 print(json.dumps({'status':'V7_SOURCE_AND_OFFICIAL_EXCERPT_FREEZE_PASS','old_small_inputs':len(refs),'official_documents':2,'release':'2026Q3','fixtures_executed':0,'real_object_parsed':0,'ARM_native':0},ensure_ascii=False))
if __name__=='__main__':main()
