"""2 cm 2.5D costmaps, normal-constrained stair crossings, dynamic obstacle avoidance, and smoothed A*."""
from nav_common import HERE
from pathlib import Path
import heapq
import math
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_dilation, label

def wrap(a):return (a+math.pi)%(2*math.pi)-math.pi

class ElevationMap:
    def __init__(self,course):
        if isinstance(course,Path) or str(course).endswith('.npz'):
            npz_path=Path(course)
            course_name=npz_path.stem
        elif str(course).startswith('mid360:'):
            course_name=str(course).split(':',1)[1]
            npz_path=HERE/'maps/mid360_prior'/f'{course_name}_pcd_nav25d.npz'
        else:
            course_name=str(course)
            npz_path=HERE/'maps/elevation'/f'{course_name}.npz'
        p=np.load(npz_path)
        self.course=course_name;self.npz_path=str(npz_path)
        self.x=p['x'];self.y=p['y'];self.h=p['height'];self.ceiling=p['ceiling']
        self.semantic=p['semantic'];self.res=float(p['resolution']);self.valid=p['valid']
        edge=np.zeros_like(self.valid)
        for axis in (0,1):
            change=np.abs(np.diff(self.h,axis=axis))>=.26
            if axis==0:edge[:-1]|=change;edge[1:]|=change
            else:edge[:,:-1]|=change;edge[:,1:]|=change
        edge|=~self.valid
        edge[[0,-1],:]=True;edge[:,[0,-1]]=True
        self.clearance=distance_transform_edt(~edge)*self.res
        self.blocked=self.clearance<.20
        self.traversable=self._compute_traversable()
        self.cost=1.+1.5*np.clip(.50-self.clearance,0,.50)+2.*(self.semantic==2)
        self._active_blocked=self.blocked
        self._active_cost=self.cost

    def _compute_traversable(self):
        step_edge=np.zeros_like(self.valid)
        for axis in (0,1):
            ch=np.abs(np.diff(self.h,axis=axis))>=.065
            if axis==0:step_edge[:-1]|=ch;step_edge[1:]|=ch
            else:step_edge[:,:-1]|=ch;step_edge[:,1:]|=ch
        step_edge|=~self.valid
        step_edge[[0,-1],:]=True;step_edge[:,[0,-1]]=True
        smooth=~step_edge&(self.ceiling>=.35)
        plat_rad=distance_transform_edt(smooth)*self.res
        lbl,n_comp=label(smooth)
        if n_comp==0:return self.valid&~self.blocked
        max_r=np.zeros(n_comp+1,dtype=np.float32)
        np.maximum.at(max_r,lbl.ravel(),plat_rad.ravel())
        # A genuine robot-standable deck/floor must accommodate >=0.48 m diameter (radius >=0.24 m),
        # eliminating all 10~30 cm guardrails, armor baffles, and arena perimeter wall rims!
        wide_smooth=(lbl>0)&(max_r[lbl]>=.24)&(~self.blocked)
        lbl_w,nw=label(wide_smooth)
        if nw==0:return self.valid&~self.blocked
        counts=np.bincount(lbl_w.ravel());counts[0]=0
        floor_id=int(counts.argmax())
        adj={i:set() for i in range(1,nw+1)}
        H,W=self.h.shape
        for shift in range(1,10):
            for dy,dx in ((shift,0),(0,shift)):
                if dy>=H or dx>=W:continue
                a=lbl_w[:H-dy,:W-dx];b=lbl_w[dy:,dx:]
                ha=self.h[:H-dy,:W-dx];hb=self.h[dy:,dx:]
                ok=(a>0)&(b>0)&(a!=b)&(np.abs(hb-ha)<=.265)
                for u,v in set(zip(a[ok].tolist(),b[ok].tolist())):
                    adj[u].add(v);adj[v].add(u)
        visited={floor_id};stack=[floor_id]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v not in visited:visited.add(v);stack.append(v)
        return binary_dilation(np.isin(lbl_w,list(visited)),iterations=3)&(~self.blocked)

    def is_traversable(self,x,y):
        ix=int(np.clip(round((float(x)-self.x[0])/self.res),0,len(self.x)-1))
        iy=int(np.clip(round((float(y)-self.y[0])/self.res),0,len(self.y)-1))
        return bool(self.traversable[iy,ix])

    def index(self,x,y):
        return (int(np.clip(round((y-self.y[0])/self.res),0,len(self.y)-1)),
                int(np.clip(round((x-self.x[0])/self.res),0,len(self.x)-1)))
    def world(self,node):return (float(self.x[node[1]]),float(self.y[node[0]]))
    def sample(self,x,y):
        x=np.asarray(x);y=np.asarray(y)
        ix=np.rint((x-self.x[0])/self.res).astype(int);iy=np.rint((y-self.y[0])/self.res).astype(int)
        valid=(ix>=0)&(iy>=0)&(ix<len(self.x))&(iy<len(self.y))
        z=self.h[np.clip(iy,0,len(self.y)-1),np.clip(ix,0,len(self.x)-1)]
        return np.where(valid,z,np.nan)
    def sample_ceiling(self,x,y):
        x=np.asarray(x);y=np.asarray(y)
        ix=np.rint((x-self.x[0])/self.res).astype(int);iy=np.rint((y-self.y[0])/self.res).astype(int)
        valid=(ix>=0)&(iy>=0)&(ix<len(self.x))&(iy<len(self.y))
        c=self.ceiling[np.clip(iy,0,len(self.y)-1),np.clip(ix,0,len(self.x)-1)]
        return np.where(valid,c,np.inf)
    def nearest_free(self,node):
        blk=self._active_blocked
        if not blk[node]:return node
        for r in range(1,101):
            lo=np.maximum(np.array(node)-r,0);hi=np.minimum(np.array(node)+r+1,blk.shape)
            free=np.argwhere(~blk[lo[0]:hi[0],lo[1]:hi[1]])
            if len(free):
                free+=lo
                return tuple(free[np.argmin(np.linalg.norm(free-node,axis=1))])
        raise ValueError('No reachable ground near requested point')

    def edge_allowed(self,a,b):
        blk=self._active_blocked
        if blk[b]:return False
        change=float(self.h[b]-self.h[a])
        if not np.isfinite(change) or abs(change)>.255:return False
        if a[0]!=b[0] and a[1]!=b[1]:
            if blk[a[0],b[1]] or blk[b[0],a[1]]:return False
            # Stair crossings use their local horizontal normal, not a corner cut.
            if abs(change)>.065:return False
        if abs(change)>.065:
            perpendicular=(0,1) if a[0]!=b[0] else (1,0)
            for s in (-12,-6,6,12):
                aa=(a[0]+s*perpendicular[0],a[1]+s*perpendicular[1]);bb=(b[0]+s*perpendicular[0],b[1]+s*perpendicular[1])
                if min(*aa,*bb)<0 or max(aa[0],bb[0])>=self.h.shape[0] or max(aa[1],bb[1])>=self.h.shape[1]:return False
                if blk[aa] or blk[bb]:return False
                if abs(float(self.h[bb]-self.h[aa])-change)>.045:return False
        return True

    def line_clear(self,a,b):
        blk=self._active_blocked
        n=max(2,int(math.dist(a,b)*2)+1)
        pts=np.rint(np.linspace(a,b,n)).astype(int)
        if np.any(blk[pts[:,0],pts[:,1]]):return False
        if np.max(np.abs(np.diff(self.h[pts[:,0],pts[:,1]])))>.055:return False
        return True

    def _astar(self,a,b,allow_stairs=True):
        cst=self._active_cost
        frontier=[(0.,a)];dist={a:0.};parent={};closed=set();moves=[(i,j) for i in (-1,0,1) for j in (-1,0,1) if i or j]
        while frontier:
            _,u=heapq.heappop(frontier)
            if u in closed:continue
            if u==b:break
            closed.add(u)
            for dy,dx in moves:
                v=(u[0]+dy,u[1]+dx)
                if min(v)<0 or v[0]>=len(self.y) or v[1]>=len(self.x) or v in closed:continue
                if not self.edge_allowed(u,v):continue
                if not allow_stairs and abs(float(self.h[v]-self.h[u]))>.055:continue
                new=dist[u]+math.hypot(dy,dx)*float(cst[v])+10.*abs(float(self.h[v]-self.h[u]))
                if new<dist.get(v,float('inf')):
                    dist[v]=new;parent[v]=u;heapq.heappush(frontier,(new+math.dist(v,b),v))
        else:raise ValueError('No traversable route; sheer walls remain blocked')
        nodes=[b]
        while nodes[-1]!=a:nodes.append(parent[nodes[-1]])
        nodes.reverse()
        return nodes

    def _smooth(self,nodes):
        smooth=[nodes[0]];i=0
        while i<len(nodes)-1:
            j=len(nodes)-1
            while j>i+1 and not self.line_clear(nodes[i],nodes[j]):j-=1
            smooth.append(nodes[j]);i=j
        return smooth

    def plan(self,start,goal,dynamic_blocked=None):
        if dynamic_blocked is not None and np.any(dynamic_blocked):
            dyn_clr=distance_transform_edt(~dynamic_blocked)*self.res
            self._active_blocked=self.blocked|dynamic_blocked
            self._active_cost=self.cost+3.0*np.clip(.45-dyn_clr,0.,.45)
        else:
            self._active_blocked=self.blocked
            self._active_cost=self.cost
        try:
            a=self.nearest_free(self.index(*start));b=self.nearest_free(self.index(*goal))
            nodes=self._astar(a,b)
            crossings=[i for i in range(1,len(nodes)) if abs(float(self.h[nodes[i]]-self.h[nodes[i-1]]))>.065]
            if not crossings:return [self.world(n) for n in self._smooth(nodes)]
            # Group multi-step double stairs (< 1.3 m apart) into one straight normal corridor!
            groups=[[crossings[0]]]
            for idx in crossings[1:]:
                if idx-groups[-1][-1]<65:groups[-1].append(idx)
                else:groups.append([idx])
            smooth=[a];last=a
            for grp in groups:
                i0,i1=grp[0],grp[-1]
                u,v=nodes[i0-1],nodes[i1]
                normal=np.subtract(nodes[i0],nodes[i0-1])
                corridor=None
                for pre_c in range(42,5,-2):
                    pre=tuple(np.subtract(u,pre_c*normal))
                    if min(pre)<0 or pre[0]>=len(self.y) or pre[1]>=len(self.x):continue
                    if not self.line_clear(pre,u):continue
                    try:approach=self._astar(last,pre,allow_stairs=False)
                    except ValueError:continue
                    for post_c in range(34,5,-2):
                        post_cand=(v[0]+post_c*normal[0],v[1]+post_c*normal[1])
                        if min(post_cand)<0 or post_cand[0]>=len(self.y) or post_cand[1]>=len(self.x):continue
                        if self.line_clear(v,post_cand):
                            corridor=(pre,post_cand,approach);break
                    if corridor is not None:break
                if corridor is None:
                    smooth.extend([nodes[i0-1],nodes[i1]]);last=nodes[i1];continue
                pre,post,approach=corridor
                smooth.extend(self._smooth(approach)[1:]);smooth.append(post);last=post
            smooth.extend(self._smooth(self._astar(last,b,allow_stairs=False))[1:])
            return [self.world(n) for n in smooth]
        finally:
            self._active_blocked=self.blocked
            self._active_cost=self.cost

class WaypointFollower:
    """Segment-aligned path follower: aligns in place at corners, then drives straight through stairs."""
    def __init__(self,path,speed=1.):
        pts=[tuple(map(float,p)) for p in path]
        clean=[pts[0]] if pts else []
        for p in pts[1:]:
            if math.dist(clean[-1],p)>.06:clean.append(p)
        self.path=clean;self.index=min(1,len(clean)-1);self.speed=speed;self.done=False;self.aligning=False

    def command(self,x,y,yaw):
        if not self.path:
            self.done=True;return 0.,0.
        while self.index<len(self.path)-1:
            target=self.path[self.index]
            prev=self.path[self.index-1] if self.index>0 else (x,y)
            seg_x,seg_y=target[0]-prev[0],target[1]-prev[1]
            seg_len=math.hypot(seg_x,seg_y)
            along=((x-prev[0])*seg_x+(y-prev[1])*seg_y)/max(seg_len,1e-4)
            cross=abs(-(x-prev[0])*seg_y+(y-prev[1])*seg_x)/max(seg_len,1e-4)
            if math.dist((x,y),target)<.24 or (along>=seg_len-.10 and cross<.32):
                self.index+=1;self.aligning=False
            else:
                break
        target=self.path[self.index]
        dist=math.dist((x,y),target)
        if self.index==len(self.path)-1 and dist<.28:
            self.done=True;return 0.,0.
        error=wrap(math.atan2(target[1]-y,target[0]-x)-yaw)
        near_final=(self.index==len(self.path)-1 and dist<.70)
        if not near_final and abs(error)>.62:self.aligning=True
        elif near_final or abs(error)<.16:self.aligning=False
        wz=float(np.clip(2.4*error,-1.2,1.2))
        if self.aligning:
            return 0.,wz
        return float(self.speed*max(.40,math.cos(error))),wz
