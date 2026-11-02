"""Read-only source/hash/data-shape/link checks. No math/control or unit replay."""
from pathlib import Path
import hashlib,json,re,traceback,csv,math
HERE=Path(__file__).resolve().parent
NAMES=['analyze_odom.py','refine_diagnostic.py','index_diagnostic.py','metrics.json','TIMING_AND_ABLATIONS.json',
 'summary_table.json','summary_table.csv','samples_202.csv','samples_203.csv','samples_205.csv','samples_208.csv','world_paths.csv',
 'analysis_attempt_01.log','refine_attempt_01.log','README.md','ERROR_REPORT.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 data=load(HERE/'metrics.json');inputs=[];producers={};rawlines=0
 for case in data['results']:
  for item in case['inputs']:
   p=Path(item['path']);assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'];inputs.append(item)
  for item in case['producer_hash_checks']:
   p=Path(item['path']);assert sha(p)==item['sha256'];producers[item['path']]=item['sha256']
  tp=next(Path(x['path']) for x in case['inputs'] if x['path'].endswith('trace.jsonl'))
  rows=[json.loads(s) for s in tp.read_bytes().splitlines()];assert len(rows)==800
  for row in rows:
   assert row['ground_truth_before']['finite'] and row['ground_truth']['finite']
   for key in ['estimated14','raw_gyro','encoder4','encoder_rate4','wheel_rate2']:
    assert all(math.isfinite(x) for x in row[key])
  rawlines+=len(rows)
  assert case['timing']['estimate_vs_GT_before_max_s']<1e-10
  assert case['timing']['sample_age_identity_max_s']<1e-10
  assert case['timing']['GT_after_to_next_before_max_xy_m']<1e-10
 skeleton=Path(data['skeleton']['path']);assert sha(skeleton)==data['skeleton']['sha256']
 old=[]
 pairs=[(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables'),
        (HERE.parent/'portable_core_v2_kinematics/MANIFEST.json','deliverables'),(HERE.parent/'portable_mpc_qp_v1/MANIFEST.json','deliverables')]
 for p,key in pairs:
  for item in load(p)[key]:
   q=p.parent/item['path'];assert q.stat().st_size==item['bytes'] and sha(q)==item['sha256'];old.append(str(q))
 for n in ['analysis_attempt_01.log','refine_attempt_01.log']:assert len(load(HERE/n))==4
 assert not (HERE/'analysis_error_01.txt').exists() and not (HERE/'refine_error_01.txt').exists()
 counts={}
 for n in ['samples_202.csv','samples_203.csv','samples_205.csv','samples_208.csv','world_paths.csv']:
  with (HERE/n).open(encoding='utf-8') as f:counts[n]=sum(1 for _ in csv.DictReader(f))
 assert list(counts.values())==[800,800,800,800,3200]
 files=[]
 for n in NAMES:
  p=HERE/n;count=len(p.read_text(encoding='utf-8-sig').splitlines());files.append({'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'line_count':count,'citation':f'{n}#L1-L{count}'})
 index={'name':'ODOM2D_DIAGNOSTIC','status':'SEALED_RECORDED_DATA_ONLY_NO_NEW_PHYSICS','write_scope':str(HERE),
  'files':files,'raw_source_references':inputs,'used_producer_source_hashes':producers,'FK_skeleton_reference':data['skeleton'],
  'producer_provenance_limit':'Only selected used producer files independently hashed; skeleton loader path known but its JSON omitted from original producer SOURCE_MANIFEST',
  'rows_analyzed':rawlines,'csv_rows':counts,'old_primary_hashes_unchanged':old,
  'method':'same queued raw gyro/encoder FK; world yaw est14[1]; body-vy pseudo=-cross(gyro,FKmid)_y; no fitting/truth correction',
  'time_modes':['current GT_before 0..7.99 and active1..7.99 trapezoid','strict packet-time deduplicated0..7.98 yaw age rewind','causal world-velocity ZOH over recorded0..8 control intervals'],
  'preserved_limitations':['10ms D3 age','20-tick boxcar aperture vs end encoder positions','0.5ms qpos/qvel vs cached R/xpos/sensor stage mixing','pseudo-lateral is assumed constraint not independent slip sensor','mixed fullDR, four train cases not holdout qualification'],
  'conclusion':'Geometry-side term helps reveal large drift; forward velocity error remains material; wheel agreement does not prove zero common slip',
  'never_performed':['parent source import/exec','MjData/mj_step/mj_forward','new simulation/plant/controller replay','board/CAN/SSH/Git/installation/training','old sealed unit replay'],
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index log excluded to avoid recursive hashes'}
 dump('INDEX.json',index)
 validation={'raw_rows':rawlines,'raw_artifact_hashes_unchanged':len(inputs),'selected_producer_sources_unchanged':len(producers),
             'old_primary_files_unchanged':len(old),'derived_csv_rows':counts,'new_simulation_steps':0,'failures':0}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{})
 links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,frag=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['README.md','metrics.json','TIMING_AND_ABLATIONS.json','summary_table.csv','INDEX.json','VALIDATION.json']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
