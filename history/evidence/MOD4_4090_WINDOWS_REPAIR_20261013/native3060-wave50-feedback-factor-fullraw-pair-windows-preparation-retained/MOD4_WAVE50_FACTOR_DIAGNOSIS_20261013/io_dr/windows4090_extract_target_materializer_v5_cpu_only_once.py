from pathlib import Path
import zipfile,json,time,hashlib
R=Path(__file__).resolve().parent
p=R/'packages/WINDOWS4090_TARGET_MATERIALIZER_V5_CPU_PREPARED.zip'
assert p.stat().st_size==384877 and hashlib.sha256(p.read_bytes()).hexdigest()=='a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90'
out=R/'install_reports/TARGET_MATERIALIZER_V5_CPU_ONLY_EXTRACTED_ACTUAL.json';assert not out.exists()
assert not (R/'repair_payload_materializer_v5').exists()
rows=[]
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in z.namelist():
  rel=Path(n);assert not rel.is_absolute() and '..' not in rel.parts and ':' not in n
  target=(R/rel).resolve();assert target.is_relative_to(R.resolve())
  assert n.startswith('repair_payload_materializer_v5/') or n=='TARGET_MATERIALIZER_V5_BUNDLE_MANIFEST.json'
  assert not target.exists()
  target.parent.mkdir(parents=True,exist_ok=True);b=z.read(n)
  with target.open('xb') as f:f.write(b)
  sha=hashlib.sha256(target.read_bytes()).hexdigest();assert sha==hashlib.sha256(b).hexdigest()
  rows.append(dict(path=str(target),bytes=len(b),sha256=sha))
j=dict(epoch=time.time(),archive=str(p),bytes=384877,sha256='a6dfeccdce21b5ff60ef246dccabb81071ee4fe4e52ffc953ade13884ec05a90',files=rows,only_CPU_plain_archive_extraction=True,no_module_import_GPU_Task_or_targetCPU_execution=True,old34304byte_package_not_consumed=True)
out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),filecount=len(rows))))
