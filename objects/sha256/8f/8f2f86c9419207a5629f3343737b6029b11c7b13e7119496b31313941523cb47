function [summary,traces]=simulate_gas_height(P)
% One reduced vertical DOF along exact CAD linkage; no lift-off/contact rig.
poses=P.poses; L=[poses.leg_length_m];
[~,ix]=min(abs(L-.275)); Lnom=L(ix);
dt=.002;t=(0:dt:15)';n=numel(t);
refs=Lnom+ .02*sin(2*pi*.6*(t-5)).*blend((t-5)/1).*blend((13-t)/1);
refdot=gradient(refs,dt);refacc=gradient(refdot,dt);
configs=[300 300;500 500;700 700;300 700;700 300];
rows=struct([]);traces=struct();
for useI=[0,1]
    for c=1:size(configs,1)
        forces=configs(c,:);z=zeros(n,1);zd=zeros(n,1);z(1)=Lnom;
        tau=zeros(n,4);actualGas=zeros(n,2);sat=false(n,1);integral=0;failed=false;
        for k=1:n-1
            if z(k)<L(1) || z(k)>L(end) || ~isfinite(z(k)),failed=true;z(k+1:end)=z(k);break;end
            [J,g,meff,qgas]=interp_pose(poses,z(k));
            virtualGravity=J(1:2,:)'\g;
            qrate=J(1:2,:)\[zd(k);0];gasSlope=J(3,:)*(J(1:2,:)\[1;0]);
            gasNow=forces-3500*qgas-3*J(3,:)*qrate;
            nominalGas=500-3500*qgas;
            error=refs(k)-z(k);
            desiredIntegral=integral+dt*error;
            forceCommand=2*virtualGravity(1)-2*gasSlope*nominalGas+meff*refacc(k) ...
                +4000*error+350*(refdot(k)-zd(k))+useI*3000*integral;
            cap=motor_limit(P.motor_parameters.leg_motor,qrate);
            angleTorque=J(2,:)'*virtualGravity(2);
            lower=-inf;upper=inf;
            for j=1:2
                a=J(1,j)/2;b=angleTorque(j);
                limits=sort([(-cap(j)-b)/a,(cap(j)-b)/a]);
                lower=max(lower,limits(1));upper=min(upper,limits(2));
            end
            actualForce=min(max(forceCommand,lower),upper);
            sat(k)=abs(actualForce-forceCommand)>1e-7;
            if ~sat(k) || sign(error)~=sign(forceCommand-actualForce),integral=desiredIntegral;end
            motor=J(1,:)'*actualForce/2+angleTorque;
            tau(k,:)=[motor',motor'];actualGas(k,:)=gasNow;
            zdd=(actualForce+gasSlope*sum(gasNow)-2*virtualGravity(1))/meff;
            zd(k+1)=zd(k)+dt*zdd;z(k+1)=z(k)+dt*zd(k+1);
        end
        tau(end,:)=tau(end-1,:);actualGas(end,:)=actualGas(end-1,:);
        name=sprintf('gas_%d_%d_integral_%d',forces(1),forces(2),useI);
        row=struct('name',name,'spring_left_n',forces(1),'spring_right_n',forces(2),'integral_enabled',logical(useI), ...
            'bounded_in_cad_range',~failed,'height_rms_error_mm',1000*sqrt(mean((z-refs).^2)), ...
            'stand_max_error_mm',1000*max(abs(z(t<=5)-refs(t<=5))), ...
            'final_stand_bias_mm',1000*mean(z(t>=14)-refs(t>=14)), ...
            'peak_motor_torque_nm',max(abs(tau),[],1),'motor_saturation_fraction',mean(sat), ...
            'min_leg_length_m',min(z),'max_leg_length_m',max(z));
        if isempty(rows),rows=row;else,rows(end+1)=row;end
        traces.(name)=struct('t',t,'leg_length',z,'reference',refs,'torque',tau,'gas_force',actualGas);
    end
end
summary=struct('cases',rows,'nominal_leg_length_m',Lnom,'kp_n_m',4000,'kd_n_s_m',350,'ki_n_m_s',3000, ...
    'scope','One vertical DOF from full-MJCF kinetic energy and CAD Jacobian; ideal pitch regulation, no wheel separation/roll/roof/thermal validation.', ...
    'reference_force_compensation_n',500,'force_uncertainty_is_not_known_to_controller',true);
end
function [J,g,meff,q]=interp_pose(poses,L)
axis=[poses.leg_length_m];
J=zeros(3,2);for i=1:3,for j=1:2,val=arrayfun(@(p)p.virtual_jacobian(i,j),poses);J(i,j)=interp1(axis,val,L,'linear');end;end
g=zeros(2,1);for i=1:2,val=arrayfun(@(p)p.static_gravity_motor_torque_nm(i),poses);g(i)=interp1(axis,val,L,'linear');end
meff=interp1(axis,[poses.effective_vertical_inertia_kg],L,'linear');
q=interp1(axis,[poses.gas_slide_m],L,'linear');
end
function cap=motor_limit(p,omega)
cap=max(0,min(p.peak_torque_nm,p.envelope_intercept_nm-p.envelope_slope_nm_s_rad*abs(omega)));
end
function y=blend(x)
x=max(0,min(1,x));y=x.^2.*(3-2*x);
end
