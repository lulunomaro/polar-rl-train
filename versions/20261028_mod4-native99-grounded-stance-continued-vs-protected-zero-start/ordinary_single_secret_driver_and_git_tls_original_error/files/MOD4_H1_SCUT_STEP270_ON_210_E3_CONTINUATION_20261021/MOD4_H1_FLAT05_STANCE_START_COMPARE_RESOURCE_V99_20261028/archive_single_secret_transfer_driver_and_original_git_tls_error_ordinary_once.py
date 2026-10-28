from pathlib import Path
import runpy,hashlib,subprocess,json,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
old=runpy.run_path(str(N/'archive_proven72_bundle_terminal_and_transfer_start_ordinary_once.py'),run_name='prior_ordinary_definitions_only');s=old['s']
for a,b in [('ordinary_proven72_bundle_terminal_and_transfer_start','ordinary_single_secret_driver_and_git_tls_original_error'),('PROVEN72_BUNDLE_TRANSFER_START_ORDINARY_GIT_NOTE.md','SINGLE_SECRET_DRIVER_TLS_ERROR_ORDINARY_GIT_NOTE.md'),('ORDINARY_PROVEN72_TRANSFER_START_CAPTURE_STARTED_ACTUAL.json','ORDINARY_SINGLE_SECRET_DRIVER_CAPTURE_STARTED_ACTUAL.json')]:
 assert s.count(a)==1;s=s.replace(a,b,1)
ns={'__name__':'driver_ordinary_definitions_only','__file__':old['ns']['__file__'],'same_sha_entries':{}};exec(compile(s,ns['__file__'],'exec'),ns)
def git(*args,input=None):
 p=subprocess.run(['git','-c','http.sslBackend=openssl','-C',str(G),*args],input=input,capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode().rstrip('\r\n')
ns['git']=git
def main():
 assert git('rev-parse','HEAD')=='6e9bd173868233a3234ca8962c3cd6c635140cb7' and len(git('tag','--list').splitlines())==1470 and not git('status','--porcelain')
 B=L/'NEW_HOST_PROVEN72_RUNTIME_TRANSFER_AND_RELOCATION_SOURCE_V1';index=B/'FROZEN_SERIAL_HOSTS_SINGLE_SECRET_TRANSFER_DRIVER_INDEX_V1.json';assert hashlib.sha256(index.read_bytes()).hexdigest()=='334181a163be2ac0426ab5d7404e71e2d30c2f00f422945b6b1ce8b1478e632b'
 files=[index,B/'drive_runtime_chunks_serial_hosts_single_secret_bounded_once_v1.py',B/'upload_verified_F_runtime_batch_to86_four_channels_stdin_once_v2.py',B/'derive_single_transport_four_SFTP_channel_upload_once_v2.py',B/'FROZEN_SINGLE_TRANSPORT_UPLOAD4_SOURCE_INDEX_V2.json',Path(__file__)]
 assert hashlib.sha256(files[1].read_bytes()).hexdigest()=='c71b0ab7512c67eab07d393b293a7f5a773bb8bfe5ee84d51a540fab3d60a10c'
 ns['prior'](G/'versions/20261028_mod4-native99-grounded-stance-continued-vs-protected-zero-start/ordinary_proven72_bundle_terminal_and_transfer_start/ORDINARY_CAPTURE_INDEX.json')
 for row in ns['prior_entries'].values():ns['same_sha_entries'].setdefault(row['SHA'],row)
 ns['run_stage']('fudan',[R],files,'''Ordinary source handoff append, no new tag/trial. Preserve original Git schannel TLS failure from first ordinary capture after its commit existed. Existing6e9bd173 objects were pushed and all1470tagobjects/peels/newblobs verified; no re-record/re-tag. This supplement uses per-command verified OpenSSL TLS backend, no globalconfiguration change or certificate verification bypass. All originalfalse/error retained.

NEW single-secret runtime transfer driver FROZEN/UNUSED at capture. Source-downloadT128/128 boundedrequests/64MiBwindow andtargetoneTransportatmost4SFTPchannels, originalremotePRE/VERIFY exact. Firstchunk0 alreadytriplehostverified andskipped. Driverstart1 alternating source72finallyclose then86finallyclose, no parallelSSH. RootoneSTDINcredentialmemory/StringIO only, neverargv/disk/output, max1800total with480reservebeforeoriginal240+240pair. Independentartifactpaths512MiBmax/perfilefullSHA/oldpartialerrorsretained, stop/join onfirstfailure/no automaticretry. Native99originalworker/save/owner/accountcontinue independently, noGPU/model/ledgeraction. Not all29chunks/unpack/SDK/adaptedtrainingready from thissource. Futureactualdriverlogs/terminal andrelocation sources explicitlypendingordinaryappendafterfreeze; sourcehandoff is concreteandreviewed, notruntime result. All1470oldtags/peels kept. Fullsource/errors/reports, binaryindexesonlyexistingproducer, no host/GPU/model/contentqueries forGit. PostGit verification conversationonly, no filechasingHEAD.''','Preserve bounded single-secret runtime migration driver and original Git TLS failure')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'ORDINARY_SINGLE_SECRET_DRIVER_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_no_retag=True),f,indent=2)
  raise
