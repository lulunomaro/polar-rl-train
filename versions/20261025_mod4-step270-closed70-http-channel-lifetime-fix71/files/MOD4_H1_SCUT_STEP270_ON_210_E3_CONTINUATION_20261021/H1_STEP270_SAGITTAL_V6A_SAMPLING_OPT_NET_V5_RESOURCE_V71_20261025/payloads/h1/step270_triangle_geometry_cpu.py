"""Exact candidate static triangles; no scene, collider, material or GPU created.

Environment origins are explicit inputs to be matched to the actual SDK later.
The lower floor remains z=0 and the platform top is .270m above it. No ramp.
The face groups identify each real top surface for a future contact/query audit.
"""
import numpy as np

def generate(origins_xy,*,height=.270,edge_x=1.1,depth=.8,width=1.2):
    origins=np.asarray(origins_xy,dtype=np.float64)
    if origins.ndim!=2 or origins.shape[1]!=2 or not len(origins) or not np.isfinite(origins).all():raise ValueError('Invalid actual environment origins')
    if height<.270 or depth<=0 or width<=0 or edge_x<=0:raise ValueError('Invalid 270mm step geometry')
    a=origins.min(0)-2.5;b=origins.max(0)+2.5
    vertices=[[a[0],a[1],0],[b[0],a[1],0],[b[0],b[1],0],[a[0],b[1],0]]
    faces=[[0,1,2],[0,2,3]];groups=[]
    cube=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,4,7],[0,7,3],[1,2,6],[1,6,5],[0,1,5],[0,5,4],[3,7,6],[3,6,2]],dtype=np.int64)
    for i,(ox,oy) in enumerate(origins):
        x0=ox+edge_x;x1=x0+depth;y0=oy-width/2;y1=oy+width/2;base=len(vertices);first=len(faces)
        vertices.extend([[x0,y0,0],[x1,y0,0],[x1,y1,0],[x0,y1,0],[x0,y0,height],[x1,y0,height],[x1,y1,height],[x0,y1,height]])
        faces.extend((cube+base).tolist());groups.append(dict(env=i,top_faces=[first+2,first+3],front_faces=[first+4,first+5],bounds=[[x0,y0,0],[x1,y1,height]]))
    return np.asarray(vertices,dtype=np.float32),np.asarray(faces,dtype=np.int64),groups
