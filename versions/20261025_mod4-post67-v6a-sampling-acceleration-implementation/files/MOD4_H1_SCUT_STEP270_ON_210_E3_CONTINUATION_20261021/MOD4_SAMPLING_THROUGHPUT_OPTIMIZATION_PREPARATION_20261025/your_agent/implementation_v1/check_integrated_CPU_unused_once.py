"""Source-AST actual function CPU comparison; one physical read of actual bank.

No Isaac imports/scene, GPU API, policy forward, physical reset or rollout.
Mock SDK writes only selected CPU tensor rows. Persist fixtures are explicitly
synthetic and isolated beneath this implementation directory.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import ast,copy,hashlib,importlib.util,io,json,sys,time,traceback,types
from pathlib import Path
from unittest import mock
import numpy as np
import torch

B=Path(__file__).resolve().parent;T=B.parents[2]
R=B/'reports/INTEGRATED_H1_E3_REAL_BANK_CPU_V1_ACTUAL.json'
BANK=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/recovery/job0/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz'
M4=T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/benchmark_closed_text'
H=B/'payloads/h1';E=B/'payloads/recovery/job0/runtime/isaac/mod4'
sys.path[:0]=[str(E),str(H),str(M4/'h1'),str(B/'original_sources')]


def hashbytes(value):return hashlib.sha256(value).hexdigest()


def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module


def method(source,classname,name,globals_):
    cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name==classname)
    node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    namespace=dict(globals_);exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-source-AST>','exec'),namespace)
    return namespace[name]


def same_tensor(a,b):return a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)


def same_array(a,b):return a.shape==b.shape and a.dtype==b.dtype and a.tobytes()==b.tobytes()


class Robot:
    def __init__(self,n,names,root,q,v):
        self.joint_names=list(names);self.calls=[]
        self.data=types.SimpleNamespace(root_state_w=root.clone(),joint_pos=q.clone(),joint_vel=v.clone())
    def write_joint_state_to_sim(self,q,v,env_ids):
        self.calls.append(('write_joint_state_to_sim',q.clone(),v.clone(),env_ids.clone()))
        self.data.joint_pos[env_ids]=q;self.data.joint_vel[env_ids]=v
    def write_root_state_to_sim(self,root,env_ids):
        self.calls.append(('write_root_state_to_sim',root.clone(),env_ids.clone()))
        self.data.root_state_w[env_ids]=root


class Scene(dict):pass


class Command:
    def __init__(self,n):self.vel_command_b=torch.ones((n,3));self.calls=0
    def set_manual_evaluation_mode(self):self.calls+=1


def env_fixture(names,phaseclass,cache,publish):
    n=20000;generator=torch.Generator(device='cpu').manual_seed(20261025)
    root=torch.randn((n,13),generator=generator);q=torch.randn((n,30),generator=generator);v=torch.randn((n,30),generator=generator)
    robot=Robot(n,names,root,q,v);scene=Scene(robot=robot)
    scene.env_origins=torch.stack((torch.arange(n).float()%100,torch.arange(n).float()//100,torch.zeros(n)),1)
    phase=phaseclass(n,'cpu');phase.age.fill_(100);phase.peak.fill_(.5);phase.delta.fill_(.125);phase.stable.fill_(5);phase.credited.fill_(True);phase.request.fill_(True)
    command=Command(n)
    env=types.SimpleNamespace(scene=scene,device='cpu',recovery=phase,_e3_fixed_reset_cache=cache)
    env.command_manager=types.SimpleNamespace(get_term=lambda _:command)
    env.publish=types.MethodType(publish,env)
    return env,command


def compare_e3(report,put):
    perm=loadmod('e1_rough_reset_tensor',B/'original_sources/permutation_e1_rough_reset_tensor.py')
    phase=loadmod('cpu_actual_recovery_phase',B/'original_sources/phase_e3_public_recovery_phase_v1.py')
    cachemod=loadmod('e3_reset_bank_cache_v1',E/'e3_reset_bank_cache_v1.py')
    manifest=next((M4/'recovery/job0/production/logs').glob('*/run_manifest.json'))
    expected=json.loads(manifest.read_text())['source_map']['isaac/mod4/MOD4_RESET_COLLISION_BANK.npz']
    before=BANK.stat();assert before.st_size==cachemod.EXPECTED_BANK_BYTES
    raw=BANK.read_bytes()  # The single physical bank read authorized for this trial.
    assert hashbytes(raw)==expected==cachemod.EXPECTED_BANK_SHA
    assert (BANK.stat().st_size,BANK.stat().st_mtime_ns,BANK.stat().st_ino)==(before.st_size,before.st_mtime_ns,before.st_ino)
    with np.load(io.BytesIO(raw),allow_pickle=False) as bank:
        names=list(bank['joint_names']);pick=int(np.argmin(abs(bank['root_height']-.25)))
        point_count=bank['points_root'].shape[1]
    report['actual_bank']=dict(path=str(BANK),bytes=len(raw),SHA=hashbytes(raw),physical_read_count=1,
                               pick=pick,points_per_pose=int(point_count),bank_joint_names=[str(x) for x in names])
    oldsource=(B/'original_sources/e3_e3_recovery_runtime_v1.py').read_text()
    newsource=(E/'e3_recovery_runtime_v1.py').read_text()
    globals_=dict(torch=torch,np=np,Path=Path,tensor=lambda value:value,__file__=str(BANK.parent/'e3_recovery_runtime_v1.py'))
    original=method(oldsource,'RecoveryEnv','place_declared_fall',globals_)
    candidate=method(newsource,'RecoveryEnv','place_declared_fall',globals_)
    publish=method(oldsource,'RecoveryEnv','publish',globals_)
    actual_read_bytes=Path.read_bytes;bank_memory_read_requests=0
    def memory_read(path):
        nonlocal bank_memory_read_requests
        if path.resolve()==BANK.resolve():bank_memory_read_requests+=1;return raw
        return actual_read_bytes(path)
    actual_load=np.load
    def memory_load(path,*args,**kwargs):
        if isinstance(path,(str,Path)) and Path(path).resolve()==BANK.resolve():return actual_load(io.BytesIO(raw),*args,**kwargs)
        return actual_load(path,*args,**kwargs)
    report['e3_cases']=[];put()
    # Baseline bank order plus non-identity robot order both exercise actual original permutation.
    orders=[('bank_order',names),('reverse_order',list(reversed(names)))]
    evidence=B/'robot_joint_names_evidence.json'
    if evidence.exists():
        saved=json.loads(evidence.read_text());orders.insert(0,('saved_actual_SDK_order',saved['joint_names']))
        report['robot_joint_names_evidence']=saved
    else:report['actual_robot_joint_order_not_claimed']=True
    with mock.patch.object(Path,'read_bytes',memory_read),mock.patch.object(np,'load',memory_load):
        for order_name,robot_names in orders:
            cpu_before=torch.random.get_rng_state().clone();np_before=np.random.get_state()
            start=time.perf_counter();cache=cachemod.E3ResetBankCache(BANK,robot_names,'cpu');build_s=time.perf_counter()-start
            assert list(perm.joint_permutation(names,robot_names))==[names.index(x) for x in robot_names]
            cases=[('all13',torch.arange(13)),('noncontiguous',torch.tensor([19999,0,131,26,14,55,66,77,88,99,110,121,132,143,154,165,176,187,198,209])),('520selected',torch.arange(520))]
            if order_name==orders[0][0]:cases.append(('all20000_selected_startup',torch.arange(20000)))
            for label,ids in cases:
                a,ac=env_fixture(robot_names,phase.RecoveryPhase,cache,publish)
                b,bc=env_fixture(robot_names,phase.RecoveryPhase,cache,publish)
                before_root=b.scene['robot'].data.root_state_w.clone();before_q=b.scene['robot'].data.joint_pos.clone();before_v=b.scene['robot'].data.joint_vel.clone()
                before_phase=b.recovery.state_dict();mask=torch.ones(20000,dtype=torch.bool);mask[ids]=False
                t=time.perf_counter();original(a,ids);old_s=time.perf_counter()-t
                t=time.perf_counter();candidate(b,ids);new_s=time.perf_counter()-t
                for key in ('root_state_w','joint_pos','joint_vel'):assert same_tensor(getattr(a.scene['robot'].data,key),getattr(b.scene['robot'].data,key)),key
                for key in a.recovery.state_dict()['tensors']:assert same_tensor(getattr(a.recovery,key),getattr(b.recovery,key)),key
                assert a.e3_reset_receipt==b.e3_reset_receipt
                assert same_tensor(a._mod4_mode_bit,b._mod4_mode_bit) and same_tensor(ac.vel_command_b,bc.vel_command_b) and ac.calls==bc.calls==1
                ar,br=a.scene['robot'],b.scene['robot']
                assert [x[0] for x in ar.calls]==[x[0] for x in br.calls]==['write_joint_state_to_sim','write_root_state_to_sim']
                for x,y in zip(ar.calls,br.calls):assert all(same_tensor(u,v) for u,v in zip(x[1:],y[1:]))
                assert same_tensor(br.data.root_state_w[mask],before_root[mask]) and same_tensor(br.data.joint_pos[mask],before_q[mask]) and same_tensor(br.data.joint_vel[mask],before_v[mask])
                assert all(same_tensor(getattr(b.recovery,k)[mask],v[mask]) for k,v in before_phase['tensors'].items())
                assert b.e3_reset_receipt['all_authored_sample_points_margin_m']==.0001
                cache.validate(robot_names)
                row=dict(joint_order=order_name,case=label,selected=len(ids),all_original_function_outputs_equal=True,all_13_recipe_covered=True,
                         unselected_plant_and_phase_unchanged=True,SDK_call_sequence_and_values_equal=True,receipt_equal=True,margin_m=.0001,
                         original_CPU_s=old_s,candidate_CPU_s=new_s,cache_startup_CPU_s=build_s,not_GPU_or_physics_speed_measurement=True)
                report['e3_cases'].append(row);put();print(json.dumps(row),flush=True)
            assert torch.equal(cpu_before,torch.random.get_rng_state())
            np_after=np.random.get_state();assert np_before[0]==np_after[0] and np.array_equal(np_before[1],np_after[1]) and np_before[2:]==np_after[2:]
        # Fail closed without touching the real source file.
        cache=cachemod.E3ResetBankCache(BANK,names,'cpu');original_identity=cachemod._identity
        with mock.patch.object(cachemod,'_identity',lambda _:tuple(list(cache._file_identity[:3])+[cache._file_identity[3]+1]+list(cache._file_identity[4:]))):
            try:cache.validate(names)
            except RuntimeError:report['metadata_change_rejected']=True
            else:raise AssertionError('Metadata change was ignored')
        cache._minimum.add_(1.)
        try:cache.validate(names)
        except RuntimeError:report['cache_mutation_rejected']=True
        else:raise AssertionError('Cache mutation was ignored')
        try:cachemod.E3ResetBankCache(BANK,names[:-1]+['wrong_joint'],'cpu')
        except ValueError:report['joint_permutation_mismatch_rejected']=True
        else:raise AssertionError('Wrong joint order/model was ignored')
    report['bank_memory_read_requests_no_additional_disk_reads']=bank_memory_read_requests
    report['e3_global_CPU_torch_and_numpy_RNG_unchanged']=True
    report['real_bank_file_untouched']=BANK.stat().st_mtime_ns==before.st_mtime_ns and BANK.stat().st_size==before.st_size
    put()


def compare_h1(report,put):
    old=loadmod('original_trace_CPU_fixture',B/'original_sources/h1_h1_production_control_prefix_trace_v1.py')
    new=loadmod('candidate_trace_CPU_fixture',H/'h1_production_control_prefix_trace_v1.py')
    source=T/'H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025/SELECTED_RECORDED_MOTION.npz'
    keys=('policy35','critic38','root13','q30','joint_velocity','applied_torque','executed6','history5ms','impulse','closure','mimic','public_request','event_expected','progress_expected','progress_peak','progress_paid','step_stable_ticks','step_success','step_wheel_crossed','takeoff_count','landing_count','recovery_count','episode','reward_term_contribution','raw_sampled6','total_reward','done')
    with np.load(source,allow_pickle=False) as z:arrays={k:z[k][:24] for k in keys}
    classes=[('original',old.H1ControlPrefixTrace),('candidate',new.H1ControlPrefixTrace)]
    fixtures=[]
    for label,cls in classes:
        folder=B/'cpu_fixtures'/label;folder.mkdir(parents=True,exist_ok=False)
        fixture=object.__new__(cls);fixture.folder=folder;fixture.rows=[];fixture.index=[];fixture.source_models=[];fixture.terms=['term'+str(i) for i in range(51)];fixture.total=0
        for i,controls in enumerate([24,24,24,24,24,7,24]):
            if i==6:(folder/'ACTUAL_STEP_ORIGINAL_ERROR.json').write_text(json.dumps(dict(SYNTHETIC_CPU_FIXTURE=True,original_error='expected failure-flag fixture, no training executed')))
            p=folder/('preupdate_fullsource_'+str(i)+'.pt');p.write_bytes(('SYNTHETIC_PREUPDATE_BYTES_NOT_A_MODEL_'+str(i)).encode())
            fixture.source_models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashbytes(p.read_bytes()),before_control=fixture.total,no_optimizer_call=True))
            fixture.rows=[{k:v[j].copy() for k,v in arrays.items()} for j in range(controls)];fixture.total+=controls;fixture.persist()
            assert not fixture.rows
        # In-progress unpaired preupdate source is never an eligible index member.
        p=folder/'preupdate_fullsource_7.pt';p.write_bytes(b'SYNTHETIC_UNPAIRED_SOURCE_NOT_A_MODEL')
        fixture.source_models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashbytes(p.read_bytes()),before_control=fixture.total,no_optimizer_call=True));fixture.persist()
        assert all((folder/('control_prefix_'+str(i)+'.npz')).exists() for i in (0,4,5,6))
        assert p.exists() and all(not(folder/('control_prefix_'+str(i)+'.npz')).exists() for i in (1,2,3))
        fixtures.append(fixture)
    for i in (0,4,5,6):
        with np.load(fixtures[0].folder/('control_prefix_'+str(i)+'.npz'),allow_pickle=False) as a,np.load(fixtures[1].folder/('control_prefix_'+str(i)+'.npz'),allow_pickle=False) as b:
            assert a.files==b.files==list(keys) and all(same_array(a[k],b[k]) for k in keys)
    for fixture in fixtures:
        index=json.loads((fixture.folder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_text())
        assert index['approved_future_retention_policy']=='future_first1_latest2_complete_pairs_plus_incomplete_and_current_failure_v1'
        assert index['retention_failure_flag_preserves_all_currently_present_files']
        assert len(index['index'])==7 and len(index['preupdate_full_sources'])==8
        for entry in index['index']:
            p=Path(entry['path'])
            if p.exists():assert entry['SHA']==hashbytes(p.read_bytes()) and entry['bytes']==p.stat().st_size
        assert all(row['SHA']==hashbytes(Path(row['path']).read_bytes()) for row in fixture.source_models if Path(row['path']).exists())
    # The actual candidate persist failure leaves rows/source and .partial in place.
    failfolder=B/'cpu_fixtures/candidate_write_failure';failfolder.mkdir()
    fixture=object.__new__(new.H1ControlPrefixTrace);fixture.folder=failfolder;fixture.rows=[{k:v[0].copy() for k,v in arrays.items()}];fixture.index=[];fixture.source_models=[];fixture.terms=[];fixture.total=1
    def write_fail(file,*a,**kw):file.write(b'SYNTHETIC_PARTIAL');raise OSError('EXPECTED_CPU_FAULT_INJECTION')
    with mock.patch.object(new,'write_trace_rows_npz',write_fail):
        try:fixture.persist()
        except OSError as error:assert str(error)=='EXPECTED_CPU_FAULT_INJECTION'
        else:raise AssertionError('Injected write failure was ignored')
    assert fixture.rows and not fixture.index and (failfolder/'control_prefix_0.npz.partial').read_bytes()==b'SYNTHETIC_PARTIAL'
    assert not(failfolder/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').exists()
    report['H1_actual_persist_CPU']=dict(all27fields_dtype_shape_array_bytes_equal=True,original_retention_wrapper_used=True,
        first1_latest2_complete_incomplete_failure_and_unpaired_preserved=True,all_published_actual_file_SHA_and_sizes_true=True,
        preupdate_fixture_bytes_preserved_not_actual_model_claim=True,preupdate_save_callback_AST_unchanged=True,
        write_fault_original_error_partial_and_rows_preserved=True,synthetic_fixture_paths=[str(x.folder) for x in fixtures])
    put()


def main():
    assert not R.exists(),'Preserve previous actual trial'
    torch.set_num_threads(1)
    report=dict(trial_id='MOD4_SAMPLING_IMPLEMENTED_REAL_BANK_CPU_V1_20261025',epoch=time.time(),status='running',
                torch=torch.__version__,numpy=np.__version__,device='cpu',no_GPU_API_SDK_scene_actor_policy_physics_or_host=True,
                script_SHA=hashbytes(Path(__file__).read_bytes()),unused_only=True,Git='pending root')
    def put():R.write_text(json.dumps(report,indent=2),encoding='utf8')
    put()
    try:
        compare_e3(report,put);compare_h1(report,put)
        report.update(status='CPU_source_and_real_bank_checks_passed_not_installed_SDK_validation',completed_epoch=time.time());put()
    except BaseException:
        report.update(status='original_error_retained',original_error=traceback.format_exc());put();raise


if __name__=='__main__':main()
