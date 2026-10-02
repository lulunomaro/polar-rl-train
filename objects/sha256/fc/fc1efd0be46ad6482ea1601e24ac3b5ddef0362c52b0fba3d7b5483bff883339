% Adapted from Particlela/WBR_simulation, MIT; see UPSTREAM_LICENSE.txt.
% Adds rotor-reflected kinetic energy in relative coordinates.
% 定义力
syms f_l f_r             % 左右轮摩擦力
syms F_ws_l F_ws_r       % 左右腿对轮的水平作用力
syms F_wh_l F_wh_r       % 左右腿对轮的垂直作用力
syms F_bs_l F_bs_r       % 左右腿对身体的水平作用力           
syms F_bh_l F_bh_r       % 左右腿对身体的垂直作用力
% 定义力矩
syms T_wl_l T_wl_r       % 左右轮对腿的力矩
syms T_bl_l T_bl_r       % 左右腿对身体的力矩
% 定义质量，重心位置，转动惯量(对质心的转动惯量)
syms m_w m_l_l m_l_r m_b % 轮子、左右腿、身体的质量
syms R_w                 % 轮子半径
syms R_l                 % 髋关节距离/2
syms l_l l_r             % 左右腿的长度
syms l_w_l l_w_r         % 轮轴到腿质心的距离
syms l_b_l l_b_r         % 髋关节到腿质心的距离
syms l_c phi_c           % 机体质心位置和倾斜角（前倾为正）
syms I_w I_l_l I_l_r I_b % 轮子、左右腿、身体的转动惯量
syms I_zz                % 机体绕垂直轴的转动惯量（用于航向角动力学方程）

% 定义运动学变量(前倾为正)
syms theta_w_l dtheta_w_l ddtheta_w_l % 左轮转角及其一阶、二阶导数
syms theta_w_r dtheta_w_r ddtheta_w_r % 右轮转角及其一阶、二阶导数
syms theta_l_l dtheta_l_l ddtheta_l_l % 左腿转角及其一阶、二阶导数
syms theta_l_r dtheta_l_r ddtheta_l_r % 右腿转角及其一阶、二阶导数
syms theta_b dtheta_b ddtheta_b       % 机体倾斜角及其一阶、二阶导数
% 定义中间变量
syms s ds dd_s                       % 轮轴连线中点水平位移及其一阶、二阶导数
syms phi dphi ddphi                   % 航向角及其一阶、二阶导数
syms S_b dS_b ddS_b                 % 机体水平位移及其一阶、二阶导数
syms h_b dh_b ddh_b                 % 机体垂直绝对高度及其一阶、二阶导数
syms S_l_l dS_l_l ddS_l_l         % 左腿水平位移及其一阶、二阶导数
syms S_l_r dS_l_r ddS_l_r         % 右腿水平位移及其一阶、二阶导数
syms h_l_l dh_l_l ddh_l_l         % 左腿垂直绝对高度及其一阶、二阶导数
syms h_l_r dh_l_r ddh_l_r         % 右腿垂直绝对高度及其一阶、二阶导数
syms phi_w_l phi_w_r phi_b_l phi_b_r         % 腿质心位置与轮轴、髋关节的夹角
syms g                                       % 重力加速度

% ==================== 运动学 ====================
% 腿质心位置与轮轴、髋关节的夹角
phi_w_l = acos((l_w_l^2 + l_l^2 - l_b_l^2)/(2*l_w_l*l_l));
phi_w_r = acos((l_w_r^2 + l_r^2 - l_b_r^2)/(2*l_w_r*l_r));
phi_b_l = acos((l_b_l^2 + l_l^2 - l_w_l^2)/(2*l_b_l*l_l));
phi_b_r = acos((l_b_r^2 + l_r^2 - l_w_r^2)/(2*l_b_r*l_r));

% (4) 航向角 phi 及其一阶、二阶导数
phi = -R_w/(2*R_l)*(theta_w_l - theta_w_r) + 1/(2*R_l)*(-l_l*sin(theta_l_l) + l_r*sin(theta_l_r));
dphi = -R_w/(2*R_l)*(dtheta_w_l - dtheta_w_r) - l_l/(2*R_l)*cos(theta_l_l)*dtheta_l_l + l_r/(2*R_l)*cos(theta_l_r)*dtheta_l_r;
ddphi = -R_w/(2*R_l)*(ddtheta_w_l - ddtheta_w_r) - l_l/(2*R_l)*cos(theta_l_l)*ddtheta_l_l + l_r/(2*R_l)*cos(theta_l_r)*ddtheta_l_r ...
        + l_l/(2*R_l)*sin(theta_l_l)*dtheta_l_l^2 - l_r/(2*R_l)*sin(theta_l_r)*dtheta_l_r^2;

% (5) 身体水平位移 S_b 及其一阶、二阶导数
S_b = R_w/2*(theta_w_l + theta_w_r) + 1/2*(l_l*sin(theta_l_l) + l_r*sin(theta_l_r)) + l_c*sin(theta_b + phi_c);
dS_b = R_w/2*(dtheta_w_l + dtheta_w_r) + l_l/2*cos(theta_l_l)*dtheta_l_l + l_r/2*cos(theta_l_r)*dtheta_l_r + l_c*cos(theta_b + phi_c)*dtheta_b;
ddS_b = R_w/2*(ddtheta_w_l + ddtheta_w_r) + l_l/2*cos(theta_l_l)*ddtheta_l_l + l_r/2*cos(theta_l_r)*ddtheta_l_r ...
        - l_l/2*sin(theta_l_l)*dtheta_l_l^2 - l_r/2*sin(theta_l_r)*dtheta_l_r^2 - l_c*sin(theta_b + phi_c)*dtheta_b^2 + l_c*cos(theta_b + phi_c)*ddtheta_b;

% (6) 身体垂直绝对高度 h_b 及其一阶、二阶导数
h_b = 1/2*(l_l*cos(theta_l_l) + l_r*cos(theta_l_r)) + l_c*cos(theta_b + phi_c);
dh_b = -l_l/2*sin(theta_l_l)*dtheta_l_l - l_r/2*sin(theta_l_r)*dtheta_l_r - l_c*sin(theta_b + phi_c)*dtheta_b;
ddh_b = -l_l/2*sin(theta_l_l)*ddtheta_l_l - l_r/2*sin(theta_l_r)*ddtheta_l_r - l_l/2*cos(theta_l_l)*dtheta_l_l^2 ...
        - l_r/2*cos(theta_l_r)*dtheta_l_r^2 - l_c*cos(theta_b + phi_c)*dtheta_b^2 - l_c*sin(theta_b + phi_c)*ddtheta_b;

% (7) 腿部水平位移 S_l_i 及其一阶、二阶导数 (基于左右侧拆分)
S_l_l = R_w*theta_w_l + l_w_l*sin(theta_l_l - phi_w_l);
S_l_r = R_w*theta_w_r + l_w_r*sin(theta_l_r - phi_w_r);
dS_l_l = R_w*dtheta_w_l + l_w_l*cos(theta_l_l - phi_w_l)*dtheta_l_l;
dS_l_r = R_w*dtheta_w_r + l_w_r*cos(theta_l_r - phi_w_r)*dtheta_l_r;
ddS_l_l = R_w*ddtheta_w_l + l_w_l*cos(theta_l_l - phi_w_l)*ddtheta_l_l - l_w_l*sin(theta_l_l - phi_w_l)*dtheta_l_l^2;
ddS_l_r = R_w*ddtheta_w_r + l_w_r*cos(theta_l_r - phi_w_r)*ddtheta_l_r - l_w_r*sin(theta_l_r - phi_w_r)*dtheta_l_r^2;

% (8) 腿部垂直绝对高度 h_l_i 及其一阶、二阶导数 (基于左右侧拆分)
h_l_l = h_b - l_b_l*cos(theta_l_l + phi_b_l) - l_c*cos(theta_b + phi_c);
h_l_r = h_b - l_b_r*cos(theta_l_r + phi_b_r) - l_c*cos(theta_b + phi_c);
dh_l_l = dh_b + l_b_l*sin(theta_l_l + phi_b_l)*dtheta_l_l + l_c*sin(theta_b + phi_c)*dtheta_b;
dh_l_r = dh_b + l_b_r*sin(theta_l_r + phi_b_r)*dtheta_l_r + l_c*sin(theta_b + phi_c)*dtheta_b;
ddh_l_l = ddh_b + l_b_l*sin(theta_l_l + phi_b_l)*ddtheta_l_l + l_b_l*cos(theta_l_l + phi_b_l)*dtheta_l_l^2 ...
        + l_c*sin(theta_b + phi_c)*ddtheta_b + l_c*cos(theta_b + phi_c)*dtheta_b^2;
ddh_l_r = ddh_b + l_b_r*sin(theta_l_r + phi_b_r)*ddtheta_l_r + l_b_r*cos(theta_l_r + phi_b_r)*dtheta_l_r^2 ...
        + l_c*sin(theta_b + phi_c)*ddtheta_b + l_c*cos(theta_b + phi_c)*dtheta_b^2;

% (9) 轮轴连线中点水平位移 s 及其一阶、二阶导数
s = R_w/2*(theta_w_l + theta_w_r);
ds = R_w/2*(dtheta_w_l + dtheta_w_r);
dd_s = R_w/2*(ddtheta_w_l + ddtheta_w_r);

% ==================== 动力学 ====================

% 1. 轮 (Wheel)
% (1) 轮平动方程 (基于左右侧拆分)
eq1 = m_w * R_w * ddtheta_w_l == f_l - F_ws_l;
eq2 = m_w * R_w * ddtheta_w_r == f_r - F_ws_r;

% (2) 轮转动方程 (基于左右侧拆分)
eq3 = I_w * ddtheta_w_l == T_wl_l - f_l * R_w;
eq4 = I_w * ddtheta_w_r == T_wl_r - f_r * R_w;

% 2. 腿 (Leg)
% (3) 腿水平平动方程 (基于左右侧拆分)
eq5 = m_l_l * ddS_l_l == F_ws_l - F_bs_l;
eq6 = m_l_r * ddS_l_r == F_ws_r - F_bs_r;

% (4) 腿垂直平动方程 (基于左右侧拆分)
eq7 = m_l_l * ddh_l_l == F_wh_l - F_bh_l - m_l_l * g;
eq8 = m_l_r * ddh_l_r == F_wh_r - F_bh_r - m_l_r * g;

% (5) 腿转动方程 (基于左右侧拆分)
eq9 = I_l_l * ddtheta_l_l == F_wh_l*l_w_l*sin(theta_l_l - phi_w_l) - F_ws_l*l_w_l*cos(theta_l_l - phi_w_l) +...
                             F_bh_l*l_b_l*sin(theta_l_l + phi_b_l) - F_bs_l*l_b_l*cos(theta_l_l + phi_b_l) - T_wl_l + T_bl_l;
eq10 = I_l_r * ddtheta_l_r == F_wh_r*l_w_r*sin(theta_l_r - phi_w_r) - F_ws_r*l_w_r*cos(theta_l_r - phi_w_r) +...
                              F_bh_r*l_b_r*sin(theta_l_r + phi_b_r) - F_bs_r*l_b_r*cos(theta_l_r + phi_b_r) - T_wl_r + T_bl_r;

% 3. 机体 (Body)
% (6) 机体水平平动方程
eq11 = m_b * ddS_b == F_bs_l + F_bs_r;

% (7) 机体垂直平动方程
eq12 = m_b * ddh_b == F_bh_l + F_bh_r - m_b * g;

% (8)  机体转动方程
eq13 = I_b * ddtheta_b == -(T_bl_l + T_bl_r) - (F_bs_l + F_bs_r)*l_c*cos(theta_b + phi_c) + (F_bh_l + F_bh_r)*l_c*sin(theta_b + phi_c);

% 4. 旋转 (Rotation/Yaw)
% (9) 航向角动力学方程
eq14 = I_zz * ddphi == (-f_l + f_r)*R_l;

% 5. 支持力关系
% (10)
eq15 = F_wh_l == F_wh_r;


syms J_h_l J_h_r J_w_l J_w_r real;
eq3 = lhs(eq3)+J_w_l*(ddtheta_w_l-ddtheta_l_l) == rhs(eq3);
eq4 = lhs(eq4)+J_w_r*(ddtheta_w_r-ddtheta_l_r) == rhs(eq4);
eq9 = lhs(eq9)+J_h_l*(ddtheta_l_l-ddtheta_b)+J_w_l*(ddtheta_l_l-ddtheta_w_l) == rhs(eq9);
eq10 = lhs(eq10)+J_h_r*(ddtheta_l_r-ddtheta_b)+J_w_r*(ddtheta_l_r-ddtheta_w_r) == rhs(eq10);
eq13 = lhs(eq13)+J_h_l*(ddtheta_b-ddtheta_l_l)+J_h_r*(ddtheta_b-ddtheta_l_r) == rhs(eq13);

elim_vars = [f_l f_r F_ws_l F_ws_r F_wh_l F_wh_r F_bs_l F_bs_r F_bh_l F_bh_r];

elim_eqs = [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq12, eq15];

elim_solve = solve(elim_eqs, elim_vars);

eq_sub = subs([eq9, eq10, eq11, eq13, eq14], elim_vars, [elim_solve.f_l, elim_solve.f_r, elim_solve.F_ws_l, elim_solve.F_ws_r, ...
    elim_solve.F_wh_l, elim_solve.F_wh_r, elim_solve.F_bs_l, elim_solve.F_bs_r, elim_solve.F_bh_l, elim_solve.F_bh_r]);

% ==================== 小角度近似与线性化 ====================
% 目标形式：A_orig * ddTheta = B_u * U + B_x * X_sub + B_offset

% 1) 定义向量
ddTheta = [ddtheta_w_l; ddtheta_w_r; ddtheta_l_l; ddtheta_l_r; ddtheta_b];
U = [T_wl_l; T_wl_r; T_bl_l; T_bl_r];
X_sub = [theta_l_l; theta_l_r; theta_b];

% 2) 将方程写成残差形式 F = 0
F = lhs(eq_sub(:)) - rhs(eq_sub(:));

% 3) 以偏置点(零角度、零角速度、零输入、零加速度)做一阶泰勒线性化
aux_vars = [dtheta_w_l; dtheta_w_r; dtheta_l_l; dtheta_l_r; dtheta_b];
Z = [ddTheta; U; X_sub; aux_vars];
Z0 = sym(zeros(size(Z)));

F0 = subs(F, Z, Z0);
J0 = subs(jacobian(F, Z), Z, Z0);
F_lin = simplify(F0 + J0 * (Z - Z0));

% 4) 仅保留题设需要的变量组(忽略角速度项)
F_lin_sub = simplify(subs(F_lin, aux_vars, sym(zeros(size(aux_vars)))));

% 5) 提取矩阵项（先得到左侧形式：A*ddTheta + Bu_l*U + Bx_l*X_sub + c_l = 0）
A_orig = simplify(jacobian(F_lin_sub, ddTheta));
Bu_l = simplify(jacobian(F_lin_sub, U));
Bx_l = simplify(jacobian(F_lin_sub, X_sub));

zero_dd = sym(zeros(size(ddTheta)));
zero_u = sym(zeros(size(U)));
zero_x = sym(zeros(size(X_sub)));
c_l = simplify(subs(F_lin_sub, [ddTheta; U; X_sub], [zero_dd; zero_u; zero_x]));

% 6) 转换为题设形式：A_orig*ddTheta = B_u*U + B_x*X_sub + B_offset
B_u = simplify(-Bu_l);
B_x = simplify(-Bx_l);
B_offset = simplify(-c_l);

% 腿质心位于腿上且机体质心位于腿间时的特殊情况验证
test_A_orig = simplify(subs(A_orig, [phi_c, l_b_r, l_b_l], [0, l_r-l_w_r, l_l-l_w_l]));
test_B_u = simplify(subs(B_u, [phi_c, l_b_r, l_b_l], [0, l_r-l_w_r, l_l-l_w_l]));
test_B_x = simplify(subs(B_x, [phi_c, l_b_r, l_b_l], [0, l_r-l_w_r, l_l-l_w_l]));
test_B_offset = simplify(subs(B_offset, [phi_c, l_b_r, l_b_l], [0, l_r-l_w_r, l_l-l_w_l]));