"""Preserve one evaluated R1 experiment with its actual recipe; no training."""
from pathlib import Path
import argparse,json,hashlib,shutil,stat,sys,base64
T=Path(__file__).resolve().parent;R=T.parents[2];ROOT=R.parent
sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
p=argparse.ArgumentParser();p.add_argument('--label',choices=['r1_010','r1_cubic_005'],required=True);p.add_argument('--reason',required=True);a=p.parse_args()
summary=json.loads((T/'evidence/ROUND_SUMMARY.json').read_text());stats=next(m for m in summary['models'] if m['model']==a.label)
origin=T if a.label=='r1_cubic_005' else T.parent/'MOD4V3_ROUGH_R1_20261111'
plan=json.loads((origin/'PLAN.json').read_text());name='model_005m.pt' if a.label=='r1_cubic_005' else 'model_010m.pt'
model=origin/'weights'/name;sha=hashlib.sha256(model.read_bytes()).hexdigest();assert sha==stats['sha256']
folder=('rough_r1_abscubic_005m_candidate_20261111' if a.label=='r1_cubic_005' else 'rough_r1_square15_010m_candidate_20261111')
out=ROOT/'frozen_models'/folder;assert not out.exists();out.mkdir();dest=out/name;shutil.copyfile(model,dest);dest.chmod(stat.S_IREAD)
remote=plan['root']+'/frozen/'+folder;source=plan['support'].rsplit('/support',1)[0]+'/'+plan['training_round']['job']+'/'+name
src="""from pathlib import Path
import hashlib,json,shutil
src=Path(SOURCE);out=Path(DEST);out.mkdir(exist_ok=False)
assert hashlib.sha256(src.read_bytes()).hexdigest()==SHA
f=out/src.name;shutil.copyfile(src,f);f.chmod(0o444)
print(json.dumps(dict(path=str(f),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),mode=oct(f.stat().st_mode&0o777))))
""".replace('SOURCE',repr(source),1).replace('DEST',repr(remote),1).replace('SHA',repr(sha),1)
c=connect()
try:
 _,o,e=c.exec_command(plan['python']+' -c "import base64;exec(base64.b64decode(\''+base64.b64encode(src.encode()).decode()+'\'))"',timeout=35)
 result=o.read().decode();error=e.read().decode();assert o.channel.recv_exit_status()==0,error;receipt=json.loads(result)
 assert receipt['sha256']==sha
 record=dict(label=a.label,sha256=sha,local_path=str(dest),remote=receipt,reason=a.reason,role='Experimental candidate; not fullDR graduation or replacement of mainStep7freeze',plan=plan,source_manifest=json.loads((origin/'evidence/SOURCE_SHA256.json').read_text()),source_directory=origin.relative_to(R).as_posix(),samebatch_statistics=stats,resume_scope='FullPPO with R1curriculum from matching support; freshphysicalepisodes; no newtraining authorization')
 raw=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode();(out/'RECIPE.json').write_bytes(raw);(out/'RECIPE.json').chmod(stat.S_IREAD)
 (T/'evidence'/(a.label+'_PRESERVED.json')).write_bytes(raw)
 sftp=c.open_sftp()
 with sftp.open(remote+'/RECIPE.json','wb') as f:f.write(raw)
 sftp.chmod(remote+'/RECIPE.json',0o444)
 sftp.close()
 print(json.dumps(dict(label=a.label,local=str(dest),remote=receipt,reason=a.reason),ensure_ascii=False))
finally:c.close()
