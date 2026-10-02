"""First import only: create honest archive-time commits and annotated tags efficiently."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

R=Path(__file__).resolve().parents[1]
NAME='lulunomaro';EMAIL='mhxiaoyao233@gmail.com'

def main():
    if (R/'.git').exists():raise RuntimeError('First import already initialized; refuse to rewrite history')
    subprocess.run(['git','init','-b','main',str(R)],check=True,capture_output=True)
    for k,v in [('user.name',NAME),('user.email',EMAIL),('core.autocrlf','false'),('core.longpaths','true')]:
        subprocess.run(['git','-C',str(R),'config',k,v],check=True)
    proc=subprocess.Popen(['git','-C',str(R),'fast-import','--quiet','--date-format=raw'],stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    pipe=proc.stdin;marks={};counter=0;parent=None;commit_count=0;tag_count=0
    def write(text):pipe.write(text.encode('utf8'))
    def blob(file):
        nonlocal counter
        raw=file.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in marks:return marks[sha]
        counter+=1;mark=counter
        write(f'blob\nmark :{mark}\ndata {len(raw)}\n');pipe.write(raw);write('\n')
        marks[sha]=mark;return mark
    def commit(title,files):
        nonlocal counter,parent,commit_count
        prepared=[(f.relative_to(R).as_posix(),blob(f)) for f in files]
        counter+=1;mark=counter;timestamp=int(time.time())
        message=title.encode('utf8')
        write(f'commit refs/heads/main\nmark :{mark}\nauthor {NAME} <{EMAIL}> {timestamp} +0800\n')
        write(f'committer {NAME} <{EMAIL}> {timestamp} +0800\ndata {len(message)}\n')
        pipe.write(message);write('\n')
        if parent:write(f'from :{parent}\n')
        for path,ref in prepared:write(f'M 100644 :{ref} {json.dumps(path,ensure_ascii=False)}\n')
        write('\n');parent=mark;commit_count+=1
    def tag(name,description):
        nonlocal tag_count
        message=description.encode('utf8');timestamp=int(time.time())
        write(f'tag {name}\nfrom :{parent}\ntagger {NAME} <{EMAIL}> {timestamp} +0800\ndata {len(message)}\n')
        pipe.write(message);write('\n');tag_count+=1
    # Archive policy and provenance are available from the beginning. Source directories
    # are added as explicit version commits; individual evidence records follow them.
    bootstrap=[R/p for p in ('.gitignore','.gitattributes','README.md','CURRENT_STATE.md')]
    bootstrap += list((R/'archive_tools').glob('*.py'))+list((R/'docs').glob('*.md'))
    bootstrap += [p for p in (R/'provenance').iterdir() if p.is_file()]
    bootstrap += [R/'history/stages.json']
    commit('建立 polar-rl-train：补建历史证据规则、归档范围与来源索引\n\n真实提交时间为归档时间；原试验日期独立记录。不启动或干预训练。',bootstrap)
    stages=json.loads((R/'history/stages.json').read_text(encoding='utf8'))
    inventory=json.loads((R/'provenance/capture_inventory.json').read_text(encoding='utf8'))
    all_entries=inventory['entries'];written_objects=set()
    for s in stages:
        values=[e for e in all_entries if e['stage_id']==s['id'] and e['captured']]
        files=[R/e['repository_path'] for e in values]
        for e in values:
            if e['object_path'] not in written_objects:
                written_objects.add(e['object_path']);files.append(R/e['object_path'])
        files += [R/'history/stages'/f'{s["id"]}.json',R/'history/stages'/f'{s["id"]}.summary.json']
        summary=json.loads(files[-1].read_text(encoding='utf8'))
        commit('归档版本：'+s['name']+' ('+s['site']+')\n\n修复/试验范围：'+summary['repair_context']+
               '\n原目录：'+s['original_root']+'\n当时源码只按保存的运行快照证明；未知作者和缺失历史不补造。',files)
        tag('version-'+s['id'],'目录归档快照：'+s['original_root']+'\n\n'+summary['repair_context']+
            '\n捕获/索引文件：'+str(s['files_captured'])+'/'+str(s['files_indexed'])+'\n非原始历史 Git 标签；此为现在的只读收集版本。')
    events=[json.loads(line) for line in (R/'history/experiments.jsonl').read_text(encoding='utf8').splitlines()]
    for e in events:
        files=[R/e['record_path']]
        diff=e.get('comparison_to_captured_current',{}).get('diff_path')
        if diff:files.append(R/diff)
        fields=e.get('observed_fields',{})
        bools={k:v for k,v in fields.items() if isinstance(v,bool)}
        detail=('\n原试验日期：'+e['historical_date']+' ('+e['date_basis']+')\n证据：'+e['primary_evidence']+
                '\n版本证据：'+e['version_evidence']['level']+'\n范围：'+e['repair_context']+
                '\n原结果布尔值（非统一毕业结论）：'+json.dumps(bools,ensure_ascii=False)[:1700]+
                '\n此为现在补建的证据提交；部署、因果和作者不由文件名推断。')
        commit(e['title'][:160]+' ['+e['kind']+']\n'+detail,files)
        tag(e['tag'],e['title']+'\n'+detail)
    final=[R/'history/INDEX.md',R/'history/VERSIONS.md',R/'history/experiments.jsonl']
    final += [p for p in (R/'project').rglob('*') if p.is_file()]
    commit('完成历史索引与当前项目固定源码副本\n\n保留失败/否决/被证伪主张，按保存证据打标签；权重与大型轨迹仅外部索引。',final)
    tag('archive-20261003-initial','初次本机/目标机历史归档完成。\n'+str(len(stages))+'个目录版本、'+str(len(events))+'条证据记录；提交时间保持真实归档时间。')
    write('done\n');pipe.close();rc=proc.wait()
    err=proc.stderr.read().decode('utf8',errors='replace')
    if rc:raise RuntimeError('git fast-import failed: '+err)
    subprocess.run(['git','-C',str(R),'reset','--mixed','HEAD'],check=True,capture_output=True)
    subprocess.run(['git','-C',str(R),'remote','add','origin','https://github.com/lulunomaro/polar-rl-train.git'],check=True)
    print(json.dumps({'commits':commit_count,'annotated_tags':tag_count,'shared_git_blobs':len(marks)}))

if __name__=='__main__':main()
