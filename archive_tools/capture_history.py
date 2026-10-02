"""Read-only, content-addressed capture of existing RL work; writes a ZIP to stdout.

Checkpoints are indexed, never deserialized. Credentials are redacted before any
captured text leaves the host. A moving file is explicitly marked as moving.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import time
import zipfile

TEXT = {'.py','.md','.json','.jsonl','.yaml','.yml','.toml','.txt','.csv','.tsv',
        '.sh','.bat','.ps1','.m','.xml','.urdf','.usda','.html','.css','.js','.cfg','.ini','.svg',
        '.diff','.sha256','.tag','.out','.mtl','.obj'}
BINARY = {'.usd','.usdc','.stl','.hf','.png','.jpg','.jpeg','.pdf'}
SKIP_DIR = {'.git','.venv','venv','node_modules','__pycache__','.playback','.staging',
            'wandb','tensorboard','.ssh','.aws','.azure','.config','site-packages'}
OMIT_SUFFIX = {'.pt','.pth','.onnx','.npz','.npy','.zip','.tar','.gz','.7z','.mp4','.avi','.pyc'}
SECRET = re.compile(r"(?i)(\b[\w]*(?:password|passwd|api_key|access_token|client_secret|ssh_pass|github_token)[\w]*\s*(?:=|:)\s*)([\"'])(.*?)(\2)")
QUOTED_SECRET = re.compile(r'''(?i)((["'])[^"'\n]*(?:password|passwd|api_key|access_token|client_secret|ssh_pass|github_token|auth_token)[^"'\n]*\2\s*:\s*)(["'])(.*?)\3''')
LONG_TOKEN = re.compile(r'''(?i)(\b(?:token|secret|authorization)\s*=\s*)(["'])([^"'\n]{16,})\2''')
CLI_PASSWORD = re.compile(r'''(?i)((?:sshpass\s+-p|--password|--passwd|\s-pw)\s+)(?:["'][^"']*["']|[^\s;]+)''')
TOKEN = re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})\b')
PRIVATE_KEY = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----',re.S)
AUTH_URL = re.compile(r'(https?://)[^\s/@:]+:[^\s/@]+@')
PASSWORD_TEXT = re.compile(r'(密码\s*[:：=]\s*)[^\s,，;；]+')


def redact(text):
    count = 0
    for pattern, replacement in ((SECRET,r'\1\2[REDACTED]\4'),(TOKEN,'[REDACTED_GITHUB_TOKEN]'),
                                 (QUOTED_SECRET,r'\1\3[REDACTED]\3'),(LONG_TOKEN,r'\1\2[REDACTED]\2'),
                                 (CLI_PASSWORD,r'\1[REDACTED]'),
                                 (PRIVATE_KEY,'[REDACTED_PRIVATE_KEY]'),(AUTH_URL,r'\1[REDACTED]@'),
                                 (PASSWORD_TEXT,r'\1[REDACTED]')):
        text, n = pattern.subn(replacement,text); count += n
    return text,count


def selected_roots(site,workspace):
    if site=='remote':
        candidates=Path('/home/egde/rl_candidates')
        roots=[p for p in candidates.iterdir() if p.is_dir()]
        project=Path('/home/egde/fangzhen_linux')
        roots += [project/p for p in ('isaac','train','logs','runs4090','incoming','sim2sim_mod4') if (project/p).is_dir()]
        roots += [project]  # root files only; its selected children are captured separately
    else:
        roots=[p for p in workspace.iterdir() if p.is_dir() and
               (p.name.lower().startswith(('mod4','remote_rl_audit','matlab_mod4','chassis_mod4')) or
                p.name=='rmuc2026_training')]
        roots += [workspace]  # historical loose scripts and documents, not unrelated downloads
    return sorted(set(roots),key=str)


def capture(site,workspace,output,supplement=False):
    started=time.time();entries=[];roots=[];seen=set();errors=[]
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for root in selected_roots(site,workspace):
            if root.name in ('mjcf','fangzhen_linux'):
                walk=[(str(root),[],[p.name for p in root.iterdir() if p.is_file()])]
            else:walk=os.walk(root,followlinks=False)
            stage=root.name if root.name not in ('mjcf','fangzhen_linux') else root.name+'_root_files'
            roots.append({'stage':stage,'root':str(root)})
            for directory,dirs,files in walk:
                dirs[:]=[d for d in dirs if d not in SKIP_DIR]
                for name in sorted(files):
                    file=Path(directory)/name
                    if file.is_symlink():continue
                    try:before=file.stat()
                    except OSError as exc:errors.append({'file':str(file),'error':type(exc).__name__});continue
                    relative=str(file.relative_to(root)).replace('\\','/')
                    ext=file.suffix.lower()
                    backup=any(marker in name.lower() for marker in ('.py.','.json.','.sh.','.yaml.','.m.','.xml.'))
                    if supplement and ext not in {'.usdc','.stl','.hf','.diff','.sha256','.tag','.out','.mtl','.obj'} and not backup:
                        continue
                    item={'site':site,'stage':stage,'relative_path':relative,'source_path':str(file),
                          'bytes':before.st_size,'mtime_epoch':before.st_mtime,'captured':False}
                    entries.append(item)
                    if name.lower().startswith(('.env','id_rsa','id_ed25519')) or ext in ('.pem','.key','.kdbx'):
                        item['omission']='credential_or_private_key_path';continue
                    if ext in OMIT_SUFFIX or name.startswith('events.out.tfevents'):
                        item['omission']='large_binary_checkpoint_or_trace_index_only';continue
                    if ext not in TEXT|BINARY|{'.log'} and not backup and name not in ('LICENSE','NOTICE','Dockerfile','Makefile'):
                        item['omission']='outside_archival_file_types';continue
                    # Avoid importing unrelated top-level personal files.
                    if root.name=='mjcf' and not any(x in name.lower() for x in
                            ('mod4','scut','reward','train','probe','repair','audit','rl_','isaac','mujoco')):
                        item['omission']='unrelated_loose_file';continue
                    limit=50_000_000 if ext=='.usd' else 8_000_000 if ext in BINARY else 5_000_000
                    try:
                        if before.st_size>limit:
                            if ext!='.log':item['omission']='large_artifact_index_only';continue
                            with file.open('rb') as f:
                                head=f.read(32_768);f.seek(max(0,before.st_size-524_288));tail=f.read(524_288)
                            raw=head+b'\n\n[ARCHIVE EXCERPT: intervening bytes omitted; not a complete log]\n\n'+tail
                            item['capture_kind']='head_32KiB_tail_512KiB_log_excerpt'
                            item['original_sha256']=None
                        else:
                            raw=file.read_bytes();item['original_sha256']=hashlib.sha256(raw).hexdigest()
                            item['capture_kind']='complete_file'
                        after=file.stat();item['stable_during_read']=(before.st_mtime_ns==after.st_mtime_ns and before.st_size==after.st_size)
                        item['redactions']=0
                        binary=ext in BINARY and not (ext=='.usd' and raw.lstrip().startswith(b'#usda'))
                        if not binary:
                            encoding='utf-8-sig'
                            try:text=raw.decode(encoding)
                            except UnicodeDecodeError:
                                try:encoding='gb18030';text=raw.decode(encoding)
                                except UnicodeDecodeError:encoding='utf-8-replacement';text=raw.decode('utf8',errors='replace')
                            text,count=redact(text);raw=text.encode('utf8');item['redactions']=count;item['source_encoding']=encoding
                        digest=hashlib.sha256(raw).hexdigest();object_path=f'objects/sha256/{digest[:2]}/{digest}'
                        if object_path not in seen:
                            archive.writestr(object_path,raw);seen.add(object_path)
                        item.update(captured=True,object_sha256=digest,object_path=object_path,captured_bytes=len(raw),binary=binary)
                    except OSError as exc:
                        item['omission']='read_error';errors.append({'file':str(file),'error':type(exc).__name__})
        manifest={'schema_version':1,'site':site,'started_epoch':started,'completed_epoch':time.time(),
                  'read_only_source_capture':True,'roots':roots,'entries':entries,'errors':errors,
                  'unique_objects':len(seen),'notes':['Retrospective evidence capture, not reconstructed original Git commits.',
                     'Missing source snapshots and author identities are unknown, not guessed.',
                     'Weights and binary traces are indexed; existing recorded hashes may be resolved separately.',
                     'Log excerpts and moving files are explicitly marked; live results may change after capture.']}
        archive.writestr(f'provenance/capture_{site}.json',json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--site',choices=['local','remote'],required=True)
    p.add_argument('--supplement',action='store_true',help='Capture additional backup and asset types only')
    p.add_argument('--workspace',type=Path,default=Path.cwd());p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open('wb') as output:capture(a.site,a.workspace.resolve(),output,a.supplement)
    else:capture(a.site,a.workspace.resolve(),sys.stdout.buffer,a.supplement)
