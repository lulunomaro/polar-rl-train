#include "sh2_control.h"
#include <string.h>
#include <stddef.h>
static int overlap(const void *a,size_t n,const void *b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if(!a||!b||!n||!m){return 0;}if(x>UINTPTR_MAX-n||y>UINTPTR_MAX-m){return 1;}return x<y+m&&y<x+n;}
static int same_geometry(const ctk_geometry *a,const ctk_geometry *b){unsigned side,pin,axis;for(side=0;side<2;side++){for(pin=0;pin<8;pin++){for(axis=0;axis<2;axis++){if(a->pin[side][pin][axis]!=b->pin[side][pin][axis]){return 0;}}}}return a->track_m==b->track_m&&a->rolling_radius_m==b->rolling_radius_m&&a->fd_epsilon_rad==b->fd_epsilon_rad&&a->circle_clearance_m==b->circle_clearance_m&&a->min_triangle_height_m==b->min_triangle_height_m&&a->branch_area_min_m2==b->branch_area_min_m2;}
static pc3_status fail(pc3_estimator *e,sh2_controller *c,sh2_result *out,pc3_status code){if(out){memset(out,0,sizeof(*out));}if(e){if(e->fault==PC3_OK){e->fault=code;}e->armed=0;}if(c&&c->fault==PC3_OK){c->fault=code;}return code;}
pc3_status sh2_configure_gyro_only(pc3_estimator_config *out,const ctk_geometry *g,const float offset[3]){pc3_status code=pc3_estimator_configure(out,g,offset);if(code!=PC3_OK){return code;}out->accel_correction=0;out->accel_reference=PC3_ACCEL_WHEEL_MIDPOINT;return pc3_estimator_config_validate(out);}
pc3_status sh2_estimate_and_step(pc3_estimator *e,sh2_controller *c,const pc3_packet *p,float forward,float yaw,uint64_t now,sh2_result *out){
 pc3_estimate estimate;pc3_status code;
 if(!out){return fail(e,c,NULL,PC3_ARGUMENT);}if(overlap(out,sizeof(*out),e,e?sizeof(*e):0u)||overlap(out,sizeof(*out),c,c?sizeof(*c):0u)||overlap(out,sizeof(*out),p,p?sizeof(*p):0u)||overlap(e,e?sizeof(*e):0u,c,c?sizeof(*c):0u)||overlap(e,e?sizeof(*e):0u,p,p?sizeof(*p):0u)||overlap(c,c?sizeof(*c):0u,p,p?sizeof(*p):0u)){
  if(e){memset(e,0,sizeof(*e));}if(c){memset(c,0,sizeof(*c));}memset(out,0,sizeof(*out));return PC3_ALIAS;
 }
 memset(out,0,sizeof(*out));if(!e||!c||!p){return fail(e,c,out,PC3_ARGUMENT);}if(e->fault!=PC3_OK||c->fault!=PC3_OK){return fail(e,c,out,PC3_LATCHED);}
 if(e->config.accel_correction!=0||e->config.accel_reference!=PC3_ACCEL_WHEEL_MIDPOINT||e->arm_mode!=PC3_ARM_SUPPORTED_UPRIGHT||!same_geometry(&e->config.geometry,&c->geometry)){return fail(e,c,out,PC3_CONFIGURATION);}
 code=pc3_estimator_update(e,p,now,&estimate);if(code!=PC3_OK){return fail(e,c,out,code);}code=sh2_controller_step(c,&estimate,forward,yaw,now,out);if(code!=PC3_OK){return fail(e,c,out,code);}return PC3_OK;
}
