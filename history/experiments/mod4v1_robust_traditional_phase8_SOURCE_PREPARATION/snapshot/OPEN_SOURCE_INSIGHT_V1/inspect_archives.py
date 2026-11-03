"""List only the two explicitly referenced ZIP central directories. Execute no members."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib,json,stat,zipfile
D=Path(__file__).resolve().parent
paths=[('SPR',Path(r'C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip')),
       ('QI_Q26',Path(r'C:\Users\lulu\Downloads\Qi-Q26-Leg_Robot.zip'))]
reports=[]
for label,path in paths:
 entries=[];exts=Counter();groups=Counter();candidates=[]
 with zipfile.ZipFile(path) as z:
  for i in z.infolist():
   n=i.filename;p=PurePosixPath(n.replace('\\','/'))
   unsafe=p.is_absolute() or '..' in p.parts or (p.parts and ':' in p.parts[0])
   link=stat.S_ISLNK(i.external_attr>>16)
   r={'name':n,'bytes':i.file_size,'compressed_bytes':i.compress_size,
      'CRC32':format(i.CRC,'08x'),'directory':i.is_dir(),'unsafe_path':bool(unsafe),
      'symlink':bool(link),'encrypted':bool(i.flag_bits&1)}
   entries.append(r)
   if not i.is_dir():
    ext=p.suffix.lower();exts[ext]+=1
    groups['/'.join(p.parts[:2])]+=1
    if ext in {'.c','.h','.cpp','.hpp','.ino','.m','.py','.md','.txt','.rst','.yml','.yaml'}:
     score=sum(k in n.lower() for k in ('jump','vmc','lqr','mpc','kalman','observer','power','chassis','balance','fsm','state','readme','license'))
     if score:candidates.append(dict(r,score=score))
 reports.append({'label':label,'archive_path':str(path),'archive_bytes':path.stat().st_size,
  'archive_SHA_not_computed':True,'central_directory_entries':len(entries),
  'file_count':sum(not e['directory'] for e in entries),'uncompressed_file_bytes':sum(e['bytes'] for e in entries),
  'extensions':dict(exts),'groups':dict(groups),'priority_text_candidates':sorted(candidates,key=lambda a:(-a['score'],a['name'])),
  'entries':entries})
out={'scope':'two explicit archives only; central directory, no member execution/extraction/model/physics',
 'producer_script_SHA':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'archives':reports,'PH8pending':True}
with (D/'ARCHIVES_CENTRAL_DIRECTORY.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
for a in reports:
 print(json.dumps({k:a[k] for k in ['label','archive_bytes','central_directory_entries','file_count','uncompressed_file_bytes','extensions','groups']},ensure_ascii=False))
 print('PRIORITY_TEXT_PATHS '+a['label'])
 for c in a['priority_text_candidates'][:35]:print(str(c['bytes'])+' '+c['name'])
