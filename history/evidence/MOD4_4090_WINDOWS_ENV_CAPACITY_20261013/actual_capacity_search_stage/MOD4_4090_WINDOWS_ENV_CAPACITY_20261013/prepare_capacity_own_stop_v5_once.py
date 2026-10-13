from pathlib import Path
import shutil,zipfile,json,time,hashlib
D=Path(__file__).resolve().parent;q=D/'template_v5_own_stop';assert not q.exists();shutil.copytree(D/'template_v4_capacity_guard',q)
p=q/'temporary_worker.py';s=p.read_text(encoding='utf8');needle='        def native_capacity_fault_check():\n';assert s.count(needle)==1
s=s.replace(needle,needle+"            if Path(args.stop_after_save).exists():\n                raise RuntimeError('Own native prePPO admission stopped by resident-headroom guardian; source checkpoint preserved')\n")
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
p=q/'temporary_parent.py';s=p.read_text(encoding='utf8');needle="                if phase != 'train' and (rss >= 19000000000 or peakhard >= 62000000000):";assert s.count(needle)==1
s=s.replace(needle,"                if phase != 'train' and peakrss * 1.25 + 536870912 >= 20000000000 and not stop.exists():\n                    atomic(stop, dict(epoch=time.time(), reason='actual_native_initial_peak_headroom_insufficient', peak_RSS_bytes=peakrss, original_25percent_plus512MiB_margin_unchanged=True, no_PPO=True, no_kill=True))\n"+needle)
compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
z=D/'CAPACITY_COMPONENTS_TEMPLATE_V5_OWN_STOP.zip';assert not z.exists()
with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED) as f:
 for p in sorted(q.iterdir()):
  if p.is_file():f.write(p,p.name)
s=(D/'deploy_capacity_intermediate_guarded_v4_once.py').read_text(encoding='utf8').replace('benchmark_v4_20261013','benchmark_v5_20261013').replace('CAPACITY_COMPONENTS_TEMPLATE_V4_GUARDED.zip','CAPACITY_COMPONENTS_TEMPLATE_V5_OWN_STOP.zip')
p=D/'deploy_capacity_intermediate_ownstop_v5_once.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/CAPACITY_OWN_STOP_V5_PREPARED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),template=str(z),bytes=z.stat().st_size,sha256=hashlib.sha256(z.read_bytes()).hexdigest(),only_newscope_native_accepts_own_STOP_before_PPO=True,initial_peak_headroom_guard_checked_earlier_not_lowered=True,no_oldscope_hotpatch_or_signal=True,new_native_own_overflow_guard_reused=True,GPU_future_pass=False),indent=2),encoding='utf8')
