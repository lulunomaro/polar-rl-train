"""Patch ONLY new raw-byte derived copies; exact before/after and reverse proof."""
from pathlib import Path
import hashlib,json,difflib,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;ROOT=O.parent;D=O/'derived';LOCK=json.loads((O/'SOURCE.json').read_bytes());R={x['member']:x for x in LOCK['selected']}
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=p.relative_to(O).as_posix(),bytes=len(b),SHA=sha(b))
def save(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
assert (O/'PATCH_PLAN.md').is_file();assert json.loads((O/'HOST_BUILD_01.json').read_bytes())['success']
records=[];all_diff=[]
def begin(m):
 raw=(D/m).read_bytes();assert sha(raw)==R[m]['raw_SHA'];p=O/'before'/m;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(raw)
 codec=R[m]['encoding'];bom=raw.startswith(b'\xef\xbb\xbf');codec='utf-8'if codec=='utf-8-sig'else codec
 text=raw[3:].decode(codec)if bom else raw.decode(codec)
 return raw,text,codec,bom,'\r\n'if b'\r\n'in raw else'\n'
def finish(m,raw,original,text,codec,bom,nl,ops):
 back=text
 for old,new in reversed(ops):assert back.count(new)==1;back=back.replace(new,old,1)
 encode=lambda s:(b'\xef\xbb\xbf'if bom else b'')+s.encode(codec)
 assert encode(back)==raw
 nb=encode(text);p=D/m
 with p.open('wb')as f:f.write(nb)
 diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='before/'+m,tofile='derived/'+m))
 all_diff.append(diff);records.append(dict(member=m,encoding=codec,UTF8_BOM=bom,newline='CRLF'if nl=='\r\n'else'LF',before_bytes=len(raw),before_SHA=sha(raw),after_bytes=len(nb),after_SHA=sha(nb),reverse_operations_restore_original_raw_bytes=True,operations=[dict(old=a,new=b)for a,b in ops]))
m='StandardRobotpp-balance1/application/chassis/chassis_balance.c';raw,t,codec,bom,nl=begin(m);original=t;ops=[]
def ch(a,b):
 global t
 assert t.count(a)==1,(a[:90],t.count(a));t=t.replace(a,b,1);ops.append((a,b))
ch('#include "chassis_balance.h"','#include "chassis_balance.h"'+nl+'#include "mod4_port_bridge.h"')
a='void ChassisConsole(void)'+nl+'{'+nl
b=a+nl.join(['    mdp1_mode port_mode = MDP1_UNSUPPORTED;','    switch (CHASSIS.mode) {','        case CHASSIS_STAND_UP: port_mode = MDP1_STANDUP; break;','        case CHASSIS_FOLLOW_GIMBAL_YAW:','        case CHASSIS_FREE:','        case CHASSIS_SPIN: port_mode = MDP1_NORMAL; break;','        case CHASSIS_OFF:','        case CHASSIS_SAFE: port_mode = MDP1_STOP_MODE; break;','        default: break;','    }','    if (!mdp1_bridge_begin(port_mode)) return;',''])
ch(a,b)
start=t.index('    double joint_pos_l[2], joint_pos_r[2];',t.index('static void ConsoleStandUp(void)'+nl+'{'))
end=t.index('    // 检测设定角度是否超过电机角度限制',start)
old=t[start:end]
new=nl.join(['    float port_qref[4];','    if (!mdp1_bridge_copy_standup_qref(port_qref)) return;','    /* Raw motor-coordinate ref; no implicit zero pose or model->motor guess. */','    if (port_qref[0] < MIN_J0_ANGLE || port_qref[0] > MAX_J0_ANGLE ||','        port_qref[1] < MIN_J1_ANGLE || port_qref[1] > MAX_J1_ANGLE ||','        port_qref[2] < MIN_J2_ANGLE || port_qref[2] > MAX_J2_ANGLE ||','        port_qref[3] < MIN_J3_ANGLE || port_qref[3] > MAX_J3_ANGLE) {','        (void)mdp1_bridge_stop(MDP1_DISABLE);','        return;','    }','    CHASSIS.joint_motor[0].set.pos = port_qref[0];','    CHASSIS.joint_motor[1].set.pos = port_qref[1];','    CHASSIS.joint_motor[2].set.pos = port_qref[2];','    CHASSIS.joint_motor[3].set.pos = port_qref[3];',''])
ch(old,new)
a='void ChassisSendCmd(void)'+nl+'{'+nl
ch(a,a+'    /* No provider/arm = no legacy motor emission. This is not a HW stop proof. */'+nl+'    if (!mdp1_bridge_emit_legacy()) return;'+nl)
ch('    uint8_t cnt;','    static uint8_t cnt = 0; /* Persistent, defined pacing state. */')
ch('if (CHASSIS.joint_motor[i].fdb.state == DM_STATE_DISABLE) {','if (CHASSIS.joint_motor[i].fdb.state == DM_STATE_DISABLE &&'+nl+'                mdp1_bridge_legacy_enable_allowed(i)) {')
finish(m,raw,original,t,codec,bom,nl,ops)
m='StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx';raw,t,codec,bom,nl=begin(m);original=t;ops=[]
newtarget='standard_robot_MOD4_PORT_STAGE1_UNBOUND'
ch('<TargetName>standard_robot</TargetName>','<TargetName>'+newtarget+'</TargetName>')
ch('<targetInfo name="standard_robot"/>','<targetInfo name="'+newtarget+'"/>')
ch('<OutputDirectory>standard_tpye_c\\</OutputDirectory>','<OutputDirectory>mod4_port_stage1\\</OutputDirectory>')
ch('<OutputName>standard_tpye_c</OutputName>','<OutputName>mod4_port_stage1_UNBOUND</OutputName>')
ch('<UpdateFlashBeforeDebugging>1</UpdateFlashBeforeDebugging>','<UpdateFlashBeforeDebugging>0</UpdateFlashBeforeDebugging>')
ch('<UseTargetDll>1</UseTargetDll>','<UseTargetDll>0</UseTargetDll>')
old='<IncludePath>'+ET.fromstring(raw).findtext('./Targets/Target/TargetOption/TargetArmAds/Cads/VariousControls/IncludePath')+'</IncludePath>'
ch(old,old.replace('</IncludePath>',';../application/mod4_port</IncludePath>'))
files=[]
for name,ft in [('mod4_port_gate.c',1),('mod4_port_bridge.c',1),('mod4_port_gate.h',5),('mod4_port_bridge.h',5)]:
 files.extend(['            <File>','              <FileName>'+name+'</FileName>','              <FileType>'+str(ft)+'</FileType>','              <FilePath>..\\application\\mod4_port\\'+name+'</FilePath>','            </File>'])
group=nl.join(['        <Group>','          <GroupName>mod4_port_stage1_unbound</GroupName>','          <Files>',*files,'          </Files>','        </Group>',''])
ch('      </Groups>',group+'      </Groups>')
parsed=ET.fromstring(t);assert len(parsed.findall('./Targets/Target/Groups/Group/Files/File'))==169
assert parsed.findtext('./Targets/Target/TargetOption/TargetArmAds/Cads/uC99')=='1'
finish(m,raw,original,t,codec,bom,nl,ops)
new=[]
for name in ('mod4_port_gate.c','mod4_port_gate.h','mod4_port_bridge.c','mod4_port_bridge.h'):
 src=O/'new_code'/name;dst=D/'StandardRobotpp-balance1/application/mod4_port'/name;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb')as f:f.write(src.read_bytes())
 assert sha(dst.read_bytes())==sha(src.read_bytes());new.append(rec(dst))
with(O/'PORT_NARROW.patch').open('x',encoding='utf-8',newline='')as f:f.write('\n'.join(all_diff))
# Every one of the other 389 inherited payloads remains byte-exact.
changed={r['member']for r in records};unchanged=[]
for m,r in R.items():
 if m not in changed:assert sha((D/m).read_bytes())==r['raw_SHA'];unchanged.append(m)
save('PATCH_RECEIPT.json',dict(status='ACTUAL_DERIVED_NARROW_PATCH_SAVED_NOT_TARGET_COMPILED',plan=rec(O/'PATCH_PLAN.md'),source_lock=rec(O/'SOURCE.json'),patch=rec(O/'PORT_NARROW.patch'),changed=records,new_sources=new,inherited_unchanged_count=len(unchanged),inherited_unchanged=unchanged,derived_project_file_count=169,automatic_flash_before_debug=False,TargetDll_flash_disabled=True,manual_external_flash_not_a_hardware_interlock=True,old_original_paths_written=False,full_target_builds=0,physical_MOD4_binding=False))
print(json.dumps(dict(status='PATCHED_NEW_DERIVED_PROJECT_ONLY',modified_original_files=len(records),new_C_header_files=len(new),unchanged_originals=len(unchanged),derived_project_members=169,patch=rec(O/'PORT_NARROW.patch'),receipt=rec(O/'PATCH_RECEIPT.json')),indent=2))
