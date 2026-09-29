"""Public forward model; inputs label hypotheses, never infers correspondences."""
import numpy as np
from kinematics import forward
WIDTH,HEIGHT=1280,960
MARKERS=np.array([[-.09,-.055,-.025],[.08,-.06,.02],[.085,.065,-.03],[-.07,.06,.04],[.015,.01,.075],[-.025,-.015,-.065]])
LABELS=[f'{side}:{j}' for side in ('left','right') for j in range(6)]

def project_poses(poses,marker_ids,side,cal):
    points=np.c_[MARKERS[np.asarray(marker_ids,int)],np.ones(len(marker_ids))]
    T=np.asarray(cal['Y'])@poses@np.asarray(cal['X_'+side]);xyz=np.einsum('nij,nj->ni',T,points)[:,:3]
    if np.any(xyz[:,2]<=0):raise ValueError('negative camera depth')
    xy=xyz[:,:2]/xyz[:,2,None];r2=np.sum(xy*xy,axis=1);p=cal['camera'];scale=1+p['k1']*r2+p['k2']*r2*r2
    return xy*scale[:,None]*[p['fx'],p['fy']]+[640,480]

def project_static(q,marker_ids,side,cal):
    return project_poses(forward(q,side,cal['zeros'][side]),marker_ids,side,cal)

def nominal_times(counters,boots,manifest,cal):
    c0={str(b['id']):b['c0'] for b in manifest['boots']};times=[]
    for counter,boot in zip(counters,boots):
        b=str(boot);c=cal['clocks'][b];s=counter-c0[b];times.append(c['offset']+c['rate']*s+c['curvature']*s*s)
    return np.array(times)

def at_observed_rows(traj,labels,center_times,rows,cal):
    times=np.asarray(center_times)+cal['camera']['readout']*(np.asarray(rows)/960-.5)
    out=np.empty((len(times),2));labels=np.asarray(labels)
    for side in ('left','right'):
        indices=np.array([i for i,l in enumerate(labels) if str(l).startswith(side+':')],int)
        if not len(indices):continue
        marker_ids=[int(str(labels[i]).split(':')[1]) for i in indices]
        out[indices]=project_poses(traj.at(times[indices],side,cal['zeros'][side]),marker_ids,side,cal)
    return out

def predict(traj,labels,counters,boots,manifest,cal):
    center=nominal_times(counters,boots,manifest,cal);rows=np.full(len(center),480.)
    for _ in range(30):
        pixels=at_observed_rows(traj,labels,center,rows,cal)
        if np.max(abs(pixels[:,1]-rows))<1e-7:return pixels
        rows=pixels[:,1]
    raise ValueError('rolling-shutter iteration did not converge')
