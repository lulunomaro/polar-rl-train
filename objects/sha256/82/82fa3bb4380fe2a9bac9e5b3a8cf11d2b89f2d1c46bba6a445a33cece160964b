function audit_armature()
% Check relative rotor inertia against independently specified cross terms.
here=fileparts(mfilename('fullpath'));
P=jsondecode(fileread(fullfile(here,'mod4_extracted_parameters.json')));
[~,i]=min(abs([P.poses.leg_length_m]-.275));p=P.poses(i);
cb=p.body_com_from_hip_xz_m;
base=[9.81,P.wheel_radius_m,P.track_m/2,p.leg_length_m,p.leg_length_m, ...
    norm(p.leg_com_from_wheel_xz_m),norm(p.leg_com_from_wheel_xz_m), ...
    norm(p.leg_com_from_hip_xz_m),norm(p.leg_com_from_hip_xz_m),norm(cb),atan2(cb(1),cb(2)), ...
    p.wheel_mass_kg,p.left_leg_mass_kg,p.right_leg_mass_kg,p.body_mass_kg,p.wheel_pitch_inertia_kg_m2, ...
    p.leg_pitch_inertia_kg_m2,p.leg_pitch_inertia_kg_m2,p.body_pitch_inertia_kg_m2,p.total_yaw_inertia_kg_m2];
M0=wbr_linear_matrices([base,0,0,0,0]);
Ja=p.leg_active_armature_total_kg_m2;
Mh=wbr_linear_matrices([base,Ja,Ja,0,0]);
expected=zeros(5);expected(1,3)=Ja;expected(1,5)=-Ja;
expected(2,4)=Ja;expected(2,5)=-Ja;
expected(4,3)=-Ja;expected(4,4)=-Ja;expected(4,5)=2*Ja;
hipError=max(abs(Mh-M0-expected),[],'all');
assert(hipError<1e-10,'Leg rotor relative inertia cross terms are wrong.');
Jw=p.wheel_armature_kg_m2;
Mw=wbr_linear_matrices([base,0,0,Jw,Jw]);
expectedRow=[Jw/P.wheel_radius_m,Jw/P.wheel_radius_m,-Jw/P.wheel_radius_m,-Jw/P.wheel_radius_m,0];
wheelError=max(abs(Mw(3,:)-M0(3,:)-expectedRow));
assert(wheelError<1e-10,'Wheel rotor relative inertia cross terms are wrong.');
status=struct('pass',true,'leg_cross_term_max_error',hipError,'wheel_force_row_cross_term_max_error',wheelError, ...
    'scope','Rotor inertia algebra only. Armature numerical values remain provisional hardware estimates.');
fid=fopen(fullfile(here,'results','armature_audit.json'),'w','n','UTF-8');c=onCleanup(@()fclose(fid));fprintf(fid,'%s\n',jsonencode(status,'PrettyPrint',true));
disp(status);
end
