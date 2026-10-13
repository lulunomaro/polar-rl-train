"""New owned archive extraction only; no Torch/Isaac imports or old main calls."""
from pathlib import Path
import sys,zipfile,hashlib,json,time
R=Path(__file__).resolve().parent
archives=[
 ('TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013.zip',2145000,'bfd6eb54412091a119659b538e02f90279b822951fe593ae726e06a15caf1a44','sdk_exact'),
 ('SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013.zip',45447841,'01b9180a42b2fda8df4f869f552a4c7e9dc0dc06ff017e0b78bfe503808eb382','immutable_source459'),
 ('TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013.zip',56162,'75d7d4a083cd0cc9bcaf735bf317455c6636223dbae8989ed8564764bd0eaa87','immutable_windows_abi')]
out=R/'install_reports/EXACT_THREE_ARCHIVES_EXTRACTED_CPU_ACTUAL.json'
assert not out.exists(), 'immutable extraction report consumed'
receipt=dict(epoch=time.time(),no_Torch_Isaac_CUDA_or_GPU_or_PPO=True,archives=[],source459_oldmain_once_preserved_not_executed=True,unused128projection_preserved_not_active20k=True)
for name,size,sha,target in archives:
 p=R/'packages'/name;assert p.stat().st_size==size and hashlib.sha256(p.read_bytes()).hexdigest()==sha
 destination=R/target;assert not destination.exists(), 'immutable extraction target already exists '+str(destination)
 rows=[]
 with zipfile.ZipFile(p) as z:
  for entry in z.infolist():
   rel=Path(entry.filename)
   assert not rel.is_absolute() and '..' not in rel.parts and ':' not in entry.filename
   actual=(destination/rel).resolve();assert actual.is_relative_to(destination.resolve())
   if entry.is_dir():continue
   data=z.read(entry);actual.parent.mkdir(parents=True,exist_ok=True)
   with actual.open('xb') as f:f.write(data)
   digest=hashlib.sha256(actual.read_bytes()).hexdigest();assert digest==hashlib.sha256(data).hexdigest()
   rows.append(dict(path=str(actual),bytes=len(data),sha256=digest))
 receipt['archives'].append(dict(path=str(p),bytes=size,sha256=sha,target=str(destination),actual_file_count=len(rows),actual_files=rows))
 receipt['partial_prefix_all_prior_extracted_bytes_retained']=True
 # Preserve incremental receipt independently if an ensuing archive rejects.
 partial=R/'install_reports'/('EXACT_ARCHIVE_'+target+'_EXTRACTED_CPU_ACTUAL.json')
 assert not partial.exists();partial.write_text(json.dumps(receipt['archives'][-1],indent=2),encoding='utf8')
ck=R/'immutable_source459/source459/checkpoint/model_32264_d05c.pt'
assert ck.stat().st_size==19043064 and hashlib.sha256(ck.read_bytes()).hexdigest()=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
receipt['checkpoint_source_exact']=True;receipt['passed_CPU_archive_byte_identity_only']=True
out.write_text(json.dumps(receipt,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),source=str(ck),all_files=sum(x['actual_file_count'] for x in receipt['archives']))))
