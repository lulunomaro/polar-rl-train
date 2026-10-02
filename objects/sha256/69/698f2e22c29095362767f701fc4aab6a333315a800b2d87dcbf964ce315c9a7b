from pathlib import Path
import hashlib
import json
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='DELIVERY_MANIFEST.json']
reference=ROOT/'reference_repos/WBR_simulation_20260917'
reference_files=[reference/'function/equation.m',reference/'LICENSE',reference/'README.md']
items=[]
for p in sorted(files+reference_files):
    items.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
manifest={'format':1,'reference_repository':'https://github.com/Particlela/WBR_simulation',
          'reference_commit':'83414c0be55632b7aa1d4dc9feaa0f5f63d5d93e',
          'validation':'PASS_REPRODUCIBLE_REDUCED_MODEL; see results/verification.json. No full-contact or real-robot certification.',
          'files':items}
manifest_path=HERE/'DELIVERY_MANIFEST.json'
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
out=ROOT/'deliveries/MOD4_MATLAB_WBR_Report_20260917.zip'
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files+reference_files+[manifest_path]):z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for item in items:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
print(json.dumps({'zip_path':str(out),'zip_bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'verified_files':len(items)},ensure_ascii=False))
