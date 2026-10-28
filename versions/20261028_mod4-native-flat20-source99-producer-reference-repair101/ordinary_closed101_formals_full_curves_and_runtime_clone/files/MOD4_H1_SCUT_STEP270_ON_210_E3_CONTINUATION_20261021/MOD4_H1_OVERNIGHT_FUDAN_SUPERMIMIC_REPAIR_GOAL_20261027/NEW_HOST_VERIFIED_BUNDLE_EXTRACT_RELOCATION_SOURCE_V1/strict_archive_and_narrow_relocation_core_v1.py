"""Pure stdlib archive/relocation helpers. Importing never opens runtime archives."""
from pathlib import Path,PurePosixPath
import ast,gzip,hashlib,io,json,os,posixpath,re,stat,tarfile,time
OLD='/home/lc01/Zonglin Li/zonglin2'
SDK='src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1'
TREE_ROOTS=('envs/mod4','compat/glibc240',SDK+'/source',SDK+'/apps',SDK+'/LICENSES')
EXACT_ROOTS=('run-python.sh','run-python-compat.sh')+tuple(SDK+'/'+n for n in ['LICENSE','LICENSE.md','LICENSE.txt','NOTICE','README.md','VERSION','pyproject.toml'])

def digest_file(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def stable(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)

def safe_name(name):
 assert isinstance(name,str) and name and '\\' not in name and not any(ord(c)<32 for c in name),'invalid archive name'
 name=name.rstrip('/');p=PurePosixPath(name);assert not p.is_absolute() and name not in {'.','..'} and all(x not in {'','..','.'} for x in name.split('/')),'noncanonical/escaping archive name'
 assert name in EXACT_ROOTS or any(name==r or name.startswith(r+'/') for r in TREE_ROOTS),'archive path outside the proven input scope'
 return name

def relative_link_target(name,text):
 assert text and '\\' not in text and not text.startswith('/') and not any(ord(c)<32 for c in text),'absolute/invalid symlink denied'
 target=posixpath.normpath(posixpath.join(posixpath.dirname(name),text));assert target not in {'','..','.'} and not target.startswith('../')
 return safe_name(target)

def validate_link_graph(kinds,links):
 for name in kinds:
  parts=PurePosixPath(name).parts
  for i in range(1,len(parts)):assert kinds.get('/'.join(parts[:i])) not in {'symlink','hardlink','file'},'archive member traverses a nondirectory member'
 def resolve(name,seen):
  parts=list(PurePosixPath(name).parts)
  for i in range(1,len(parts)+1):
   prefix='/'.join(parts[:i])
   if prefix in links:
    assert prefix not in seen,'cyclic archive link'
    replaced=links[prefix]+'/'+ '/'.join(parts[i:]) if i<len(parts) else links[prefix]
    return resolve(posixpath.normpath(replaced),seen|{prefix})
  return name
 resolved={name:resolve(target,{name}) for name,target in links.items()}
 for name,target in resolved.items():
  safe_name(target)
  if kinds[name]=='hardlink':assert kinds.get(target)=='file','hardlink must resolve to an archived regular file'
 return resolved

def verify_chunks(paths,rows,expected_archive_SHA,emit):
 assert len(paths)==len(rows)==29
 whole=hashlib.sha256();snapshots=[];total=0
 for i,(p,row) in enumerate(zip(paths,rows)):
  assert p.resolve()==p and not p.is_symlink();before=p.stat();assert stat.S_ISREG(before.st_mode) and before.st_size==row['bytes'];h=hashlib.sha256()
  with p.open('rb') as f:
   while True:
    block=f.read(1024**2)
    if not block:break
    h.update(block);whole.update(block);total+=len(block)
  assert stable(before)==stable(p.stat()) and h.hexdigest()==row['SHA'],'input full chunk SHA/stat mismatch'
  snapshots.append(stable(before));emit(stage='PREEXTRACT_INPUT_CHUNK_FULL_SHA',chunk=i,bytes=row['bytes'],SHA=h.hexdigest())
 assert total==15158703068 and whole.hexdigest()==expected_archive_SHA
 return snapshots

class OrderedChunks(io.RawIOBase):
 def __init__(self,paths,rows,snapshots):self.paths=paths;self.rows=rows;self.snapshots=snapshots;self.index=0;self.file=None;self.h=None;self.whole=hashlib.sha256();self.total=0
 def readable(self):return True
 def readinto(self,buffer):
  if self.index==len(self.paths):return 0
  if self.file is None:
   assert stable(self.paths[self.index].stat())==self.snapshots[self.index];self.file=self.paths[self.index].open('rb');self.h=hashlib.sha256()
  n=self.file.readinto(buffer)
  if n:self.h.update(memoryview(buffer)[:n]);self.whole.update(memoryview(buffer)[:n]);self.total+=n;return n
  assert self.h.hexdigest()==self.rows[self.index]['SHA'] and stable(os.fstat(self.file.fileno()))==self.snapshots[self.index];self.file.close();self.file=None;self.index+=1;return self.readinto(buffer)
 def close(self):
  if self.file:self.file.close();self.file=None
  super().close()

def extract_stream_new(paths,rows,snapshots,dest,logical_input_bytes,expected_archive_SHA,emit):
 assert not dest.exists() and dest.parent.resolve()==dest.parent;dest.mkdir(mode=0o700)
 raw=OrderedChunks(paths,rows,snapshots);buffered=io.BufferedReader(raw,buffer_size=1024**2);kinds={};links={};link_texts={};modes={};mtimes={};sizes={};python_rows={};manifest_hash=hashlib.sha256();regular_bytes=0;members=0;last=0
 try:
  with gzip.GzipFile(fileobj=buffered,mode='rb') as gz:
   with tarfile.open(fileobj=gz,mode='r|') as tf:
    for member in tf:
     name=safe_name(member.name);assert name not in kinds,'duplicate tar member';assert not member.issparse() and not any(k.startswith('GNU.sparse') for k in member.pax_headers),'sparse extension denied'
     assert member.size>=0;path=dest/name;assert path.is_relative_to(dest)
     if member.isdir():kind='dir'
     elif member.isreg():kind='file'
     elif member.issym():kind='symlink'
     elif member.islnk():kind='hardlink'
     else:raise AssertionError('device/FIFO/socket/unknown tar member denied: '+name)
     kinds[name]=kind;modes[name]=member.mode&0o777;mtimes[name]=member.mtime
     for parent in path.parents:
      if parent==dest:break
      assert not parent.is_symlink(),'archive parent unexpectedly a symlink'
     if kind=='dir':path.mkdir(parents=True,exist_ok=True,mode=0o700);assert path.is_dir() and not path.is_symlink()
     elif kind=='file':
      path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);src=tf.extractfile(member);assert src is not None;h=hashlib.sha256();n=0
      with path.open('xb') as out:
       while True:
        block=src.read(1024**2)
        if not block:break
        out.write(block);h.update(block);n+=len(block)
      assert n==member.size;os.chmod(path,modes[name]);os.utime(path,(member.mtime,member.mtime));sizes[name]=n;regular_bytes+=n;assert regular_bytes<=logical_input_bytes,'tar expanded bytes exceed original input footprint'
      if name.endswith('.py'):python_rows[name]=h.hexdigest()
     else:
      assert member.size==0;links[name]=relative_link_target(name,member.linkname) if kind=='symlink' else safe_name(member.linkname)
      if kind=='symlink':link_texts[name]=member.linkname
     record=dict(name=name,kind=kind,size=member.size,mode=modes[name],link_target=links.get(name),SHA=h.hexdigest() if kind=='file' else None);manifest_hash.update((json.dumps(record,sort_keys=True)+chr(10)).encode());members+=1
     if time.monotonic()-last>=20:emit(stage='SAFE_TAR_EXTRACT_NEW_COPY',members=members,regular_bytes=regular_bytes,last_owned_relative_member=name);last=time.monotonic()
   while gz.read(1024**2):pass
  assert raw.index==29 and raw.total==15158703068 and raw.whole.hexdigest()==expected_archive_SHA,'ordered gzip input CRC/full SHA not complete'
 finally:buffered.close()
 resolved=validate_link_graph(kinds,links)
 for name in sorted(links):
  if kinds[name]!='hardlink':continue
  target=dest/resolved[name];path=dest/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);assert target.is_file() and not target.is_symlink() and not path.exists();os.link(target,path);sizes[name]=sizes[resolved[name]]
  if name.endswith('.py'):python_rows[name]=digest_file(target)
 for name in sorted(links):
  if kinds[name]!='symlink':continue
  path=dest/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);assert not path.exists() and not path.is_symlink();os.symlink(link_texts[name],path)
 for name in sorted((x for x in kinds if kinds[x]=='dir'),key=lambda x:len(PurePosixPath(x).parts),reverse=True):os.chmod(dest/name,modes[name]);os.utime(dest/name,(mtimes[name],mtimes[name]))
 assert sum(sizes.values())==logical_input_bytes,'extracted logical regular/hardlink bytes differ from source footprint'
 return dict(members=members,regular_files=sum(x=='file' for x in kinds.values()),hardlinks=sum(x=='hardlink' for x in kinds.values()),relative_symlinks=sum(x=='symlink' for x in kinds.values()),logical_regular_and_hardlink_bytes=sum(sizes.values()),tar_member_metadata_and_payload_SHA=manifest_hash.hexdigest(),python_source_hash_rows=python_rows,ordered_gzip_CRC_and_full_producer_SHA_passed=True,all_members_created_inside_new_copy=True,no_source_ownership_setuid_devices_or_external_links_restored=True)

def python_rows_digest(rows):
 h=hashlib.sha256()
 for name,digest in sorted(rows.items()):h.update((name+'\0'+digest+'\n').encode())
 return h.hexdigest()

def narrow_relocate_new_copy(dest,binding,python_rows,save_original):
 assert binding['source_prefix']==OLD;changed=[];finder_names=[]
 for row in binding['finders']:
  rel=Path(row['path']).relative_to(OLD).as_posix();p=dest/rel;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA'] and raw==row['UTF8'].encode();assert raw.count(OLD.encode())==1
  oldtree=ast.parse(raw);mapping=next(x for x in oldtree.body if isinstance(x,ast.AnnAssign) and isinstance(x.target,ast.Name) and x.target.id=='MAPPING');value=ast.literal_eval(mapping.value);assert len(value)==1 and next(iter(value.values())).startswith(OLD+'/'+SDK+'/source/')
  new=raw.replace(OLD.encode(),str(dest).encode());assert new.replace(str(dest).encode(),OLD.encode())==raw;ast.parse(new);save_original(rel,raw);p.write_bytes(new);changed.append(dict(path=rel,kind='exact_single_editable_MAPPING_prefix',old_SHA=row['SHA'],new_SHA=hashlib.sha256(new).hexdigest(),inverse_bytes_equal=True));finder_names.append(rel)
 for key,name in [('run_python','run-python.sh'),('run_python_compat','run-python-compat.sh')]:
  p=dest/name;row=binding[key];assert digest_file(p)==row['SHA'] and p.read_bytes()==row['UTF8'].encode() and p.stat().st_mode&stat.S_IXUSR
 bin_changes=[];unhandled=[];wrapper=str(dest/'run-python.sh').encode();assert b' ' not in wrapper and len(wrapper)+2<=127
 pattern=re.compile(rb'#!'+re.escape(OLD.encode())+rb'/envs/mod4/bin/python(?:3(?:\.12)?)?([ \t]+[^\r\n]*)?\r?\n')
 for p in sorted((dest/'envs/mod4/bin').iterdir()):
  if p.is_symlink() or not p.is_file():continue
  with p.open('rb') as f:first=f.readline(4096)
  if not first.startswith(b'#!') or OLD.encode() not in first:continue
  m=pattern.fullmatch(first)
  if not m:unhandled.append(dict(path=p.relative_to(dest).as_posix(),first_line_UTF8=first.decode('utf8','replace'),reason='not a source-prefix Python console-script shebang; unchanged'));continue
  assert not m.group(1),'unexpected interpreter argument requires explicit source decision'
  raw=p.read_bytes();new=b'#!'+wrapper+b'\n'+raw[len(first):];assert new.split(b'\n',1)[1]==raw.split(b'\n',1)[1];ast.parse(raw);ast.parse(new);rel=p.relative_to(dest).as_posix();save_original(rel,raw);p.write_bytes(new);bin_changes.append(dict(path=rel,old_SHA=hashlib.sha256(raw).hexdigest(),new_SHA=hashlib.sha256(new).hexdigest(),only_first_line_changed=True,script_body_SHA=hashlib.sha256(raw[len(first):]).hexdigest(),new_interpreter='copied relative run-python.sh -> copied glibc240 loader'))
 before={name:digest for name,digest in python_rows.items() if name not in finder_names and not name.startswith('envs/mod4/bin/')};after={name:digest_file(dest/name) for name in before};assert after==before,'SDK/vendor Python source changed beyond declared five editable finders'
 for name in ['home','cache','config','tmp','state','state/runtime','home/.local/share']:(dest/name).mkdir(parents=True,exist_ok=True,mode=0o700)
 return dict(exact_five_editable_finder_changes=changed,bin_Python_shebang_changes=bin_changes,unhandled_other_prefix_shebangs_left_unchanged=unhandled,two_original_relative_launchers_byte_unchanged=True,unchanged_SDK_and_vendor_Python_files=len(before),unchanged_SDK_and_vendor_Python_rows_SHA=python_rows_digest(before),historical_conda_and_direct_url_metadata_unchanged=True,no_ELF_SDK_runtime_or_existing_environment_bytes_patched=True,not_SDK_CUDA_or_application_runtime_admission=True)
