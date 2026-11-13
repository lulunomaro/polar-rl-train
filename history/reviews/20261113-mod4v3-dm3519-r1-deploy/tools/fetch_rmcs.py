"""Fetch only actual pinned RMCS build dependencies from the official repository."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
REV='a27e3d14c36ef8d780287e154b32ed4a70bbbdc9'
def fetch(row):
    path=ROOT/'reference/RMCS'/row['path']
    url=f"https://raw.githubusercontent.com/Alliance-Algorithm/RMCS/{REV}/{row['path']}"
    if path.exists():data=path.read_bytes()
    else:
        with urllib.request.urlopen(url,timeout=40) as response:data=response.read()
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    assert blob==row['sha'],(row['path'],blob,row['sha'])
    return dict(path=str(path),url=url,bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),git_blob_SHA1=blob)
if __name__=='__main__':
    tree=json.loads((ROOT/'reference/RMCS_TREE.json').read_text(encoding='utf-8'))['tree']
    prefixes=tuple('rmcs_ws/src/'+name+'/' for name in ('rmcs_executor','rmcs_utility','rmcs_msgs'))
    rows=[row for row in tree if row['type']=='blob' and row['path'].startswith(prefixes)]
    with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(fetch,rows))
    dest=ROOT/'reference/RMCS_PINNED_SOURCES.json';assert not dest.exists()
    dest.write_text(json.dumps(dict(commit=REV,files=results),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(files=len(results),bytes=sum(r['bytes'] for r in results),commit=REV)))
