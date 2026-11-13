"""Extract Jammy GCC13 packages privately; never changes system apt sources."""
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).resolve().parents[1]
BASE='https://ppa.launchpadcontent.net/ubuntu-toolchain-r/test/ubuntu/'
NAMES=('gcc-13-base','cpp-13','gcc-13','g++-13','cpp-13-x86-64-linux-gnu','gcc-13-x86-64-linux-gnu','g++-13-x86-64-linux-gnu','libgcc-13-dev','libstdc++-13-dev','gcc-16-base','libgcc-s1','libstdc++6')
if __name__=='__main__':
    dest=ROOT/'toolchain/gcc13_jammy/packages';dest.mkdir(parents=True,exist_ok=True)
    url=BASE+'dists/jammy/main/binary-amd64/Packages.gz'
    raw=urllib.request.urlopen(url,timeout=40).read();(dest/'Packages.gz').write_bytes(raw)
    records={}
    for section in gzip.decompress(raw).decode().split('\n\n'):
        row={}
        for line in section.splitlines():
            if line and not line[0].isspace() and ': ' in line:
                key,value=line.split(': ',1);row[key]=value
        if row.get('Package') in NAMES:records[row['Package']]=row
    assert set(records)==set(NAMES),records.keys()
    def download(name):
        row=records[name];p=dest/Path(row['Filename']).name
        if not p.exists():
            with urllib.request.urlopen(BASE+row['Filename'],timeout=120) as response:p.write_bytes(response.read())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA256']
        return dict(package=name,version=row['Version'],dependencies=row.get('Depends'),path=str(p),bytes=p.stat().st_size,SHA256=row['SHA256'],url=BASE+row['Filename'])
    with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(download,NAMES))
    report=dict(repository=BASE,index_SHA256=hashlib.sha256(raw).hexdigest(),packages=rows,system_install=False)
    attempt=sys.argv[1] if len(sys.argv)>1 else 'manual'
    output=ROOT/'reports'/('gcc13_private_packages_'+attempt+'.json');assert not output.exists()
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
