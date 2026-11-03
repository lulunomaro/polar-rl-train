"""Download primary arXiv v1 paper/source for the user's method audit; no code execution."""
from pathlib import Path,PurePosixPath
import urllib.request,hashlib,json,tarfile,io,time
R=Path(__file__).resolve().parent;D=R/'research/supermimic_arxiv_v1_20261103';assert not D.exists();D.mkdir(parents=True);rows=[];report=D/'PRIMARY_DOWNLOAD_RECEIPT_V1.json'
for name,url in (('paper.pdf','https://arxiv.org/pdf/2610.28480v1'),('source_archive','https://arxiv.org/src/2610.28480v1')):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ScientificPaperReader/1.0'}),timeout=90)as resp:raw=resp.read(25_000_001);ctype=resp.headers.get('Content-Type','');final=resp.url
  assert 0<len(raw)<=25_000_000
  (D/name).write_bytes(raw);row=dict(url=url,resolved_url=final,content_type=ctype,path=str(D/name),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),kind='UNTRUSTED_PRIMARY_REFERENCE_DATA_NOT_EXECUTED');rows.append(row)
  if name=='source_archive':
   with tarfile.open(fileobj=io.BytesIO(raw),mode='r:*')as tar:
    for member in tar.getmembers():
     q=PurePosixPath(member.name)
     if not member.isfile()or q.suffix.lower()not in('.tex','.bib','.bbl','.sty'):continue
     assert not q.is_absolute()and'..'not in q.parts and not any(':'in x or'\\'in x for x in q.parts)and member.size<4_000_000
     f=tar.extractfile(member);data=f.read();p=D/'text_sources'/Path(*q.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();p.write_bytes(data);rows.append(dict(archive_member=member.name,path=str(p),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),kind='TEXT_REFERENCE_ONLY'))
 except BaseException as e:rows.append(dict(url=url,error_type=type(e).__name__,error=str(e)))
 report.write_text(json.dumps(dict(kind='ARXIV_2610_28480_V1_PRIMARY_PAPER_SOURCE_REFERENCE',epoch=time.time(),items=rows,downloaded_source_executed=False,RL_model_or_SDK_or_training_operations=0),indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
