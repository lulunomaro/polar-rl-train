from pathlib import Path
import ast,json,time
J=Path(__file__).resolve().parent;R=J/'reports';p=J/'resume_missing_Fudan_reference_assets_raw_transport_and_CPU_v2_unused_once.py';s=p.read_text('utf8')
start=s.index('def public_bytes(row):');end=s.index('\ndef main():',start)
new='''def public_bytes(row):
 attempts=[];revision='8204e853dfd2ed06d85a322e1a998c3d20a3be2c'
 for host in ('cdn.jsdelivr.net','fastly.jsdelivr.net'):
  url='https://'+host+'/gh/yly-true/fudan_rl_wheel_leg@'+revision+'/'+row['path']
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'MOD4-pinned-reference-missing-two-v3','Accept':'application/octet-stream'})
   with urllib.request.urlopen(request,timeout=35) as response:
    blocks=[];size=0
    while True:
     block=response.read(256*1024)
     if not block:break
     size+=len(block);assert size<=row['bytes'];blocks.append(block)
    raw=b''.join(blocks)
   assert len(raw)==row['bytes'] and hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()==row['Git_blob_SHA1']
   return raw,attempts+[dict(url=url,transport_mirror_only_primary_pinned_Git_blob_SHA1_matches=True)]
  except BaseException:attempts.append(dict(url=url,error=traceback.format_exc()))
 raise RuntimeError(json.dumps(attempts))
'''
s=s[:start]+new+s[end:]
old="failures=list(R.glob('FUDAN_REFERENCE_CPU_PREPARATION_ORIGINAL_ERROR_*.json'));assert len(failures)==1;error=read(failures[0]);completed=error['transferred'];assert len(completed)==10 and 'IncompleteRead' in error['error']"
new="failures=list(R.glob('FUDAN_REFERENCE_MISSING_ONLY_V2_ORIGINAL_ERROR_*.json'));assert len(failures)==1;error=read(failures[0]);completed=error['transferred'];assert len(completed)==22 and 'TimeoutError' in error['error']"
assert s.count(old)==1;s=s.replace(old,new,1);assert s.count('assert len(missing)==14')==1;s=s.replace('assert len(missing)==14','assert len(missing)==2',1).replace('FUDAN_REFERENCE_MISSING_ONLY_V2_STARTED_ACTUAL.json','FUDAN_REFERENCE_MISSING_ONLY_V3_STARTED_ACTUAL.json').replace('FUDAN_REFERENCE_EXISTING_PARTIAL_FRESH_METADATA_AND_NO_OWN_RUN_ACTUAL.json','FUDAN_REFERENCE_V3_PARTIAL22_FRESH_METADATA_AND_NO_OWN_RUN_ACTUAL.json').replace('FUDAN_REFERENCE_MISSING_ONLY_V2_ORIGINAL_ERROR_\'','FUDAN_REFERENCE_MISSING_ONLY_V3_ORIGINAL_ERROR_\'').replace('known_first10_assets_not_redownloaded=True','known_first22_assets_not_redownloaded=True')
ast.parse(s);out=J/'resume_only_two_missing_Fudan_assets_pinned_mirror_and_CPU_v3_unused_once.py'
with out.open('x',encoding='utf8') as f:f.write(s)
B=J.parent/'H1_STEP270_REWARD_PATH_V1_20261022';t=(B/'same_authorized_session_compressed_transport_v142.py').read_text('utf8');needle='    assert target.name in {';assert t.count(needle)==1;t=t.replace(needle,needle+'\n        '+repr(out.name)+',',1)
with (B/'same_authorized_session_compressed_transport_v143.py').open('x',encoding='utf8') as f:f.write(t)
with (R/'TWO_MISSING_STL_PINNED_TRANSPORT_V3_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),new_entry=str(out),known22completed_only_metadata_no_repeat_download=True,missing_only=['plane/resources/robots/infantry_V4/meshes/r_wheel_Link.STL','plane/resources/robots/infantry_V4/meshes/rf1_Link.STL'],new_transport='pinned CDN byte mirror with exact primary Git blob SHA1 + size + new full SHA256',no_GPU_or_reference_rollout_yet=True,original_V1_V2_network_errors_retained=True),f,indent=2)
print('Prepared missing-onlyV3 for two STL assets;143 exact allowlist')
