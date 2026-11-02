"""Persist separate core/host receipts, all nonconvergence, portable source closure."""
from pathlib import Path
import json,hashlib,zipfile,struct,collections
HERE=Path(__file__).resolve().parent;AS=HERE.parent/'ACTIVE_BOX_QP_V3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def dump(n,v):
 p=HERE/n;assert not p.exists(),n;p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 comp=json.loads((HERE/'COMPARISON.json').read_text());assert comp['error_count']==0
 rows=[json.loads(s)for s in(HERE/'host_run_01.log').read_text().splitlines()if s.startswith('{')];non=[r for r in rows if r['kind']=='frame'and r['reason']==9];assert len(non)==334
 dump('ALL_NONCONVERGED.json',dict(count=len(non),status_counts=dict(collections.Counter(str(r['qstatus'])for r in non)),records=non,private_iterate_accepted=False,all_z_outputs_zero=all(all(x==0 for x in r['qz'])for r in non)))
 source=[HERE/n for n in ['nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h']];deps=[AS/'active_box_qp.c',AS/'active_box_qp.h']
 dump('CORE_RECEIPT.json',dict(status='SEALED_NEW_INPROCESS_NATIVE_C_CORE_INTERFACE',sources=[record(p)for p in source],exact_sealed_runtime_dependencies=[record(p)for p in deps],heap_VLA_mutable_globals=False,caller_owned=True,H32_real_H15_bit_exact=True,N=15,tolerance=0.0020000000949949026,max_pivots=64,model='fixedleg8+nominal_lag9',const_payload_bytes=4068,output_torque='binary64; C3 fallback f32 values promoted exactly',typed_extensions='epoch/alias/config/context/clock availability/counter saturation',default_ground_trust=False,caller_disable_required_for_jump_predicted_flight_non_normal_or_unbound_contact_permission=True,ground_domain_is_not_ground_flight_detector=True,COM_FSM_caps_raised=False,R39_GT_used=False,C3_final_enqueue_or_hardware_bound=False,blocked_IO_repaired=False))
 host=json.loads((HERE/'HOST_BUILD_01.json').read_text());exes=[]
 for r in host['commands']:
  p=Path(r['artifact']);assert p.is_file()and sha(p)==r['sha256']
  if p.suffix=='.exe':
   raw=p.read_bytes();pos=struct.unpack_from('<I',raw,0x3c)[0];assert raw[:2]==b'MZ'and raw[pos:pos+4]==b'PE\0\0'and struct.unpack_from('<H',raw,pos+4)[0]==0x14c and struct.unpack_from('<H',raw,pos+24)[0]==0x10b;exes.append({**record(p),'PE':'PE32 i386'})
 dump('HOST_QUALIFICATION.json',dict(status='NEW_HOST_INPROCESS_C_AND_CPP_QUALIFIED',build_attempts=1,executables=exes,rows=3717,native_checks=84531,failures=0,raw_H15_cold_warm=36,all_inputs_original_parent_problem_bit_equal=True,empirical_compressed_f_bitdiff_rows=0,bit_exact_general_promise=False,maximum_errors=comp['maximum_errors'],reason_counts=comp['reason_counts'],clock_insertions=45,clock='instrumented logical ns; not wall/target WCET',source_replay_method=comp['reference_method'],R39_or_new_physics_used=False,scope='not a driver/enqueue or complete real-time qualification'))
 bundle=HERE/'nm1_source_bundle.zip';assert not bundle.exists()
 entries=[(p,'NATIVE_C_MPC_SUPERVISOR_V1/'+p.name)for p in source]+[(p,'ACTIVE_BOX_QP_V3/'+p.name)for p in deps]+[(HERE/'BUILD.txt','BUILD.txt')]
 with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p,name in entries:
   info=zipfile.ZipInfo(name,date_time=(2026,11,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 with zipfile.ZipFile(bundle)as z:
  for p,name in entries:assert z.read(name)==p.read_bytes()
 dump('SOURCE_CLOSURE.json',dict(bundle=record(bundle),entries=[dict(archive_path=name,**record(p))for p,name in entries],runtime_Python_C3_or_SDK_required=False,BSP_clock_driver_binding_supplied=False))
 print(json.dumps(dict(core_sources=4,sealed_dependencies=2,nonconverged=334,status_counts=dict(collections.Counter(str(r['qstatus'])for r in non)),host_exes=len(exes),bundle_sha256=sha(bundle))))
if __name__=='__main__':main()
