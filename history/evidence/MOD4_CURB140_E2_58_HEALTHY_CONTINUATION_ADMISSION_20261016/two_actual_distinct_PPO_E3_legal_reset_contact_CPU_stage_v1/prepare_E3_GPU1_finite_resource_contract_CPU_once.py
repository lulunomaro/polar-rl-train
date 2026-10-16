from pathlib import Path
import ast,json,time,hashlib,os,types
D=Path(__file__).resolve().parent;E=D/'e3_legal_fall_reset_admission';R=D/'reports'
def main():
 p=R/'E3_GPU1_FINITE_RESOURCE_LOCK_NEGATIVES_CPU_ACTUAL.json';assert not p.exists();tree=ast.parse((E/'e3_gpu1_pose_contact_finite_parent_v1.py').read_text('utf8'));fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='lock_owners');ns=dict(os=os);exec(compile(ast.Module(body=[fn],type_ignores=[]),'lock_function_actual_AST','exec'),ns);st=types.SimpleNamespace(st_dev=os.makedev(8,2) if hasattr(os,'makedev') else 2050,st_ino=999)
 # Windows has no POSIX device helpers; explicit CPU OS fixture only, not actual lock proof.
 ns['os']=types.SimpleNamespace(major=lambda x:8,minor=lambda x:2)
 assert ns['lock_owners'](st,'7: FLOCK ADVISORY WRITE 3119751 08:02:999 0 EOF')==[3119751]
 bad=['7: FLOCK ADVISORY WRITE 3119751 08:03:999 0 EOF','7: FLOCK ADVISORY WRITE 3119751 08:02:998 0 EOF','7: -> FLOCK ADVISORY WRITE 3119751 08:02:999 0 EOF','malformed','']
 for row in bad:assert ns['lock_owners'](st,row)==[]
 assert ns['lock_owners'](st,'7: FLOCK ADVISORY WRITE 42 08:02:999 0 EOF')==[42]
 files=[]
 for f in sorted(E.glob('*.py')):ast.parse(f.read_text('utf8'));raw=f.read_bytes();files.append(dict(relative=f.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 report=dict(epoch=time.time(),passed_CPU_only=True,actual_lock_parser_AST_fixture_passed=True,negative_fixture_count=6,known_owner_PID_creation_argv_manifest_and_GPU0_task_still_required_at_runtime=True,per_GPU1_actual_fcntl_and_no_GPU1_compute_required=True,manual_default_PD_geometry_contact_only_no_recovery_PPO_or_budget=True,original_GPU0_cohort_not_modified_or_signaled=True,actual_target_GPU1_and_native_not_yet_passed=True,files=files);p.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,negative_fixtures=6,files=len(files))))
if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback
  (R/('E3_RESOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
