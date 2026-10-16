"""Synthetic dual-arm measurement rig driven by real G1 joint-state recordings.

Not manufacturer-accurate G1 geometry. Transforms act on local column vectors.
Joint values are linearly interpolated before forward kinematics.
"""
import json
import numpy as np
from scipy.spatial.transform import Rotation
AXES=np.array([[0,1,0],[1,0,0],[0,0,1],[0,1,0],[1,0,0],[0,1,0],[0,0,1]],float)
LINKS=np.array([[0,0,-.08],[0,0,-.06],[0,0,-.24],[0,0,-.22],[.045,0,0],[.035,0,0],[.065,0,0]])
BASES={'left':np.array([0.,.22,0.]),'right':np.array([0.,-.22,0.])}

def forward(q,side,zeros=(0.,0.)):
    q=np.atleast_2d(q).astype(float).copy();q[:,1]+=zeros[0];q[:,3]+=zeros[1]
    out=np.broadcast_to(np.eye(4),(len(q),4,4)).copy();out[:,:3,3]=BASES[side]
    for j in range(7):
        step=np.broadcast_to(np.eye(4),(len(q),4,4)).copy()
        step[:,:3,:3]=Rotation.from_rotvec(q[:,j,None]*AXES[j]).as_matrix()
        step[:,:3,3]=np.einsum('nij,j->ni',step[:,:3,:3],LINKS[j]);out=out@step
    return out

class Trajectory:
    def __init__(self,path):
        rows=json.load(open(path));self.times=np.array([r['timestamp'] for r in rows],float)
        state=np.array([r['state'] for r in rows],float)
        if state.shape!=(len(rows),34) or not np.isfinite(state).all() or not np.all(np.diff(self.times)>0):raise ValueError('invalid state trajectory')
        self.q={'left':state[:,:7],'right':state[:,8:15]}

    def joints(self,times,side):
        times=np.atleast_1d(times).astype(float)
        if np.any(times<self.times[0]) or np.any(times>self.times[-1]):raise ValueError('time outside recorded states')
        return np.column_stack([np.interp(times,self.times,self.q[side][:,j]) for j in range(7)])

    def at(self,times,side,zeros=(0.,0.)):
        return forward(self.joints(times,side),side,zeros)
