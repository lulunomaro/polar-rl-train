"""Run inside WSL Ubuntu22.04 after the pinned packages have downloaded."""
import json
import os
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    base=ROOT/'toolchain/gcc13_jammy';dest=base/'root';dest.mkdir(exist_ok=True)
    results=[]
    for p in sorted((base/'packages').glob('*.deb')):
        r=subprocess.run(['dpkg-deb','-x',str(p),str(dest)],capture_output=True,text=True)
        results.append(dict(package=p.name,returncode=r.returncode,stderr=r.stderr))
        assert r.returncode==0,r.stderr
    env=os.environ.copy();env['LD_LIBRARY_PATH']=str(dest/'usr/lib/x86_64-linux-gnu')+':'+env.get('LD_LIBRARY_PATH','')
    p=subprocess.run([str(dest/'usr/bin/g++-13'),'--version'],env=env,capture_output=True,text=True)
    report=dict(extractions=results,gcc_returncode=p.returncode,gcc_stdout=p.stdout,gcc_stderr=p.stderr,system_install=False)
    (ROOT/'reports/gcc13_private_extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));assert p.returncode==0
