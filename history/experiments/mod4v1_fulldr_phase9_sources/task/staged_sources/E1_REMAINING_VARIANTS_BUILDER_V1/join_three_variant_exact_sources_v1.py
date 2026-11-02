"""SOURCE_ONLY explicit268/3d/aab exact executed package text materialization.
No PT/stat/hash/decode, no binary/NPZ/USD reads, no runtime/Torch/SSH imports.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent.parent;W=Path(r'C:\Users\lulu\Desktop\claude\mjcf');P=W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/payload';I=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload'
NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.onnx','.safetensors','.pyc','.png','.jpg','.jpeg','.pdf','.stl','.obj','.ply','.bin'}

def H(raw):return hashlib.sha256(raw).hexdigest()
def main():
 pm=(P/'PAYLOAD_MANIFEST.json').read_bytes();tm=(I/'TRAIN_PACKAGE_MANIFEST.json').read_bytes();assert H(pm)=='d767ba02247d743b7438553d306eeb63300756dcf2000736fcd16f3f680710a1';assert H(tm)=='18102368b517da4c406ccfd1653f568e2aeaa6e1a7358753a14dde0751d7500e'
 p=json.loads(pm);i=json.loads(tm);out=[]
 for name,role,SHA,base,manifest,prefix,baseCanonical in [('CURB_PROTECTED878','E1_CURB','268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1',P,p,'plant/','CURB141'),('CURB_INDEPENDENT113','E1_CURB','3d2b0b6d9260383031e0c198501224fdaedefef9c283b43ce588419319b5de88',I,i,'job0/','CURB141'),('SLOPE_INDEPENDENT50','E1_SLOPE','aab6fb4b6bce2f0004d06fa9d78f964efafd470238e36d386113ff9fba955d0b',I,i,'job1/','SLOPE135')]:
  root=T/'staged_sources'/('E1_'+name+'_40050_MOD4V1_SOURCE_V1');root.mkdir(exist_ok=False);records=[];binary=[];missing=[]
  rows=manifest.get('rows',manifest.get('files'));assert isinstance(rows,list)
  for r in rows:
   rel=r.get('relative',r.get('path'));assert rel
   if rel.startswith(prefix):newrel=rel[len(prefix):]
   elif not rel.startswith(('plant/','job0/','job1/','job2/','rank0/','rank1/','rank2/')):newrel='producer/'+rel
   else:continue
   if Path(rel).suffix.lower() in NO:
    binary.append(dict(original_relative=rel,derived_relative=newrel,saved_bytes=r.get('bytes'),saved_SHA=r.get('SHA',r.get('sha256')),binary_not_statted_read_or_hashed=True));continue
   src=base/rel
   try:raw=src.read_bytes()
   except FileNotFoundError:missing.append(dict(relative=rel,expected_SHA=r.get('SHA',r.get('sha256')),path=str(src)));continue
   try:raw.decode('utf-8-sig')
   except UnicodeDecodeError:raise ValueError('Unexpectednontext file:'+rel)
   sha=H(raw);expected=r.get('SHA',r.get('sha256'));assert sha==expected and len(raw)==r['bytes'],rel
   dest=root/'original_exact'/newrel;dest.parent.mkdir(parents=True,exist_ok=True)
   with dest.open('xb') as f:f.write(raw)
   dst=root/newrel;dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as f:f.write(raw)
   records.append(dict(original_relative=rel,relative=newrel,source_input_path=str(src),bytes=len(raw),SHA=sha,AST_SHA=H(ast.dump(ast.parse(raw),include_attributes=False).encode()) if rel.endswith('.py') else None))
  entry='train_host72_backend_admission_v1.py' if 'PROTECTED' in name else 'train_independent_owned_axis_v1.py';helper='curb20_entry_full_checkpoint' if role=='E1_CURB' else 'slope5_full_checkpoint';meta=dict(kind='EXPLICIT_FROZEN_VARIANT_ORIGINAL_EXECUTED_PACKAGE_JOIN_SOURCE_ONLY',variant=name,role=role,original_source_SHA=SHA,upstream_manifest=str(base/('PAYLOAD_MANIFEST.json' if base==P else 'TRAIN_PACKAGE_MANIFEST.json')),upstream_manifest_SHA=H(pm if base==P else tm),selected_prefix=prefix,entry=entry,original_helper=helper,baseline_canonical=baseCanonical,text_count=len(records),binary_metadata_only=binary,missing_text=missing,inputs=records,actual_PT_SSH_SDK_GPU_operations=0)
  with (root/'EXACT_EXECUTED_SOURCE_PACKAGE_JOIN_V1.json').open('x',encoding='utf-8') as f:json.dump(meta,f,indent=2)
  out.append(dict(variant=name,root=str(root),text=len(records),binary_metadata=len(binary),missing_text=missing));print(json.dumps(out[-1],indent=2))
 with (B/'THREE_VARIANT_EXACT_SOURCE_MATERIALIZATION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_ONLY_THREE_VARIANT_MATERIALIZATION',packages=out,actualPT_operations=0),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('SOURCE_JOIN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
  raise
