#include "pc2_sensor_chain.h"
#include <stddef.h>
#include <string.h>
#define PC2_CHAIN_MAGIC 0x53324331u
static int overlap(const void *a,size_t na,const void *b,size_t nb){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<=y?y-x<na:x-y<nb;}
static pc3_status failure(pc2_sensor_chain *s,pc2_sensor_chain_result *out,pc3_status code){
 memset(out,0,sizeof(*out));s->fault=code;s->estimator.armed=0u;
 if(s->estimator.fault==PC3_OK)s->estimator.fault=code;
 if(s->balance.fault==PC3_OK)s->balance.fault=code;
 return code;
}
pc3_status pc2_sensor_chain_init(pc2_sensor_chain *s,const pc3_estimator_config *config,pc3_arm_mode prior,uint32_t heading){
 pc2_sensor_chain next;pc3_status status;
 if(!s||!config)return PC3_ARGUMENT;
 if(overlap(s,sizeof(*s),config,sizeof(*config)))return PC3_ALIAS;
 memset(&next,0,sizeof(next));pc3_estimator_reset(&next.estimator);
 status=pc3_estimator_arm(&next.estimator,config,prior);if(status!=PC3_OK)return status;
 status=pc2_balance_init(&next.balance,&config->geometry,heading);if(status!=PC3_OK)return status;
 next.magic=PC2_CHAIN_MAGIC;*s=next;return PC3_OK;
}
pc3_status pc2_sensor_chain_step(pc2_sensor_chain *s,const pc3_packet *packet,float forward,float yaw,uint64_t now,pc2_sensor_chain_result *out){
 pc2_sensor_chain_result result;pc3_status status;
 if(!s||!packet||!out)return PC3_ARGUMENT;
 if(overlap(s,sizeof(*s),packet,sizeof(*packet))||overlap(s,sizeof(*s),out,sizeof(*out))||overlap(out,sizeof(*out),packet,sizeof(*packet)))return PC3_ALIAS;
 memset(out,0,sizeof(*out));
 if(s->magic!=PC2_CHAIN_MAGIC)return PC3_NOT_INITIALIZED;
 if(s->fault!=PC3_OK)return PC3_LATCHED;
 memset(&result,0,sizeof(result));
 status=pc3_estimator_update(&s->estimator,packet,now,&result.estimate);
 if(status!=PC3_OK)return failure(s,out,status);
 status=pc2_balance_step(&s->balance,&s->estimator.config.geometry,&result.estimate,forward,yaw,now,&result.control);
 if(status!=PC3_OK)return failure(s,out,status);
 *out=result;return PC3_OK;
}
