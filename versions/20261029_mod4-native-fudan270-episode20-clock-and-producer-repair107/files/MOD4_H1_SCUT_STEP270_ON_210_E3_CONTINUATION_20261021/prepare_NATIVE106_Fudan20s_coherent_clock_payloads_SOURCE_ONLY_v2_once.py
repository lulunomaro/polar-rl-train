from pathlib import Path
import runpy
T=Path(__file__).resolve().parent
P=T/'prepare_NATIVE106_Fudan20s_coherent_clock_payloads_SOURCE_ONLY_once.py'
s=P.read_text('utf8')
s=s.replace("assert not N.exists();R.mkdir(parents=True)","assert N.exists() and not (N/'payloads').exists();R.mkdir(parents=True,exist_ok=True)")
s=s.replace("[('native_iteration','updates'),('world_updates','world_updates'),('policy_updates','policy_updates')]","[('updates','updates'),('world_updates','world_updates'),('policy_updates','policy_updates')]")
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(P)))
