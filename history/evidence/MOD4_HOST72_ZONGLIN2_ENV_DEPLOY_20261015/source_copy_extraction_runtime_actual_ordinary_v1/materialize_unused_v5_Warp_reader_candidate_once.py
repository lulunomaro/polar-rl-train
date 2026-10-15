from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent
p=D/'payload/validate_owned_Lab_headless_GPU_PhysX_v4.py';s=p.read_text()
s=s.replace('v4','v5').replace('V4','V5')
s=s.replace("livestream=0,extra_args=[","livestream=0,enable_crashreporter=False,extra_args=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false',")
old="body=view.create_rigid_body_view('/World/OwnedLabProbeBox');initial=body.get_transforms().clone()"
new="body=view.create_rigid_body_view('/World/OwnedLabProbeBox')\n import warp as wp\n def tensor(x):return x.clone() if isinstance(x,torch.Tensor) else wp.to_torch(x).clone()\n initial=tensor(body.get_transforms())"
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('pose=body.get_transforms().clone();vel=body.get_velocities().clone()','pose=tensor(body.get_transforms());vel=tensor(body.get_velocities())')
s=s.replace('no_tiny_CUDA_replay=True','no_tiny_CUDA_replay=True,original_V4_Warp_array_reader_error_preserved=True,read_only_Warp_to_Torch_then_clone=True,crashreporter_disabled_and_dump_preservation_requested=True')
q=p.with_name('validate_owned_Lab_headless_GPU_PhysX_v5_warp_reader.py');assert not q.exists();compile(s,str(q),'exec');q.write_text(s)
v=dict(epoch=time.time(),source=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),changes='Only new owned V5 probe converts actual Warp array with wp.to_torch; disables crashreporter and preserves inherited dumps. Original V4 reader error/source retained.',
 earlier_outer_PowerShell_parse_failure_no_file_or_network=True,earlier_runner_source_FileNotFound_before_auth_network_GPU=True,
 no_previous_GPU_phase_or_SDK_source_replayed_or_modified=True)
with (D/'reports/UNUSED_V5_WARP_READER_MATERIALIZED_AFTER_OUTER_PARSE_FAILURE_ACTUAL.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
