"""Forward-only, frozen fixture constructor; privileged labels never enter inputs."""
import json,struct,zlib,sys,shutil,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'environment'))
from kinematics import Trajectory
from camera_model import LABELS,predict,project_static,nominal_times
HEADER=struct.Struct('<4sI');PAYLOAD=struct.Struct('<IBd2f');PACKET=struct.Struct('<IBd2fI')
assert PAYLOAD.size==21 and PACKET.size==25

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(obj,separators=(',',':')))

def make_case(name,episode,n,boots,drop,outliers,burst,seed,public=False,start_index=0,min_separation=5, shared=None, visible=None):
    folder=ROOT/('environment/public' if public else 'tests/cases')/name;folder.mkdir(parents=True,exist_ok=True)
    source=ROOT/f'tools/sources/episode_{episode}.json';raw=json.loads(source.read_text())[start_index:start_index+n]; origin=raw[0]['timestamp']; raw=[dict(r,timestamp=r['timestamp']-origin) for r in raw]
    save(folder/'states.json',[{'timestamp':r['timestamp'],'state':r['state']} for r in raw]);traj=Trajectory(folder/'states.json');rng=np.random.default_rng(seed)
    answer={}
    for side in ('left','right'):
        X=np.eye(4);X[:3,:3]=Rotation.random(random_state=rng).as_matrix();X[:3,3]=rng.uniform(-.07,.07,3);answer['X_'+side]=X.tolist()
    answer['zeros']={s:rng.uniform(-.12,.12,2).tolist() for s in ('left','right')}
    Y=np.eye(4);Y[:3,:3]=Rotation.random(random_state=rng).as_matrix()
    center=np.vstack([traj.at(traj.times,s,answer['zeros'][s])[:,:3,3] for s in ('left','right')]).mean(axis=0)
    Y[:3,3]=np.array([0,0,rng.uniform(1.5,1.85)])-Y[:3,:3]@center;answer['Y']=Y.tolist()
    answer['camera']={'fx':float(rng.uniform(850,1150)),'fy':float(rng.uniform(850,1150)),'k1':float(rng.uniform(-.15,.15)),
                      'k2':float(rng.uniform(-.045,.045)),'readout':float(rng.uniform(.014,.032))}
    if shared is not None:
        import copy
        for key in ('X_left','X_right','zeros','Y','camera'):answer[key]=copy.deepcopy(shared[key])
    labels=np.arange(1,boots+1);edges=np.linspace(1,traj.times[-1]-1,boots+1)
    clocks={};metadata=[];frames=[]
    for k,boot in enumerate(labels):
        boot=int(boot);start=float(edges[k]+.2);stop=float(edges[k+1]-.35)
        times=np.arange(start,stop,.095);keep=rng.random(len(times))>drop
        if burst and len(times)>30:keep[len(times)//3:len(times)//3+8]=False
        rate=float(rng.uniform(.93,1.07));curvature=float(rng.uniform(-.0025,.0025));c0=float(rng.uniform(20,400))
        clocks[str(boot)]={'offset':start,'rate':rate,'curvature':curvature}
        metadata.append({'id':boot,'c0':c0,'host_hint':float(start+rng.uniform(-1,1))})
        for t in times[keep]:
            s=2*(t-start)/(rate+np.sqrt(rate*rate+4*curvature*(t-start)));frames.append((boot,float(c0+s)))
    manifest={'boots':metadata};answer['clocks']=clocks
    all_boots=np.repeat([f[0] for f in frames],12).tolist();all_counters=np.repeat([f[1] for f in frames],12).tolist();all_labels=LABELS*len(frames)
    points=predict(traj,all_labels,all_counters,all_boots,manifest,answer).reshape(-1,12,2)
    true_labels=[];counters=[];packet_boots=[];clean=[];frame_indices=[];minimum_separation=float('inf')
    for fi,((boot,counter),uv) in enumerate(zip(frames,points)):
        dist=np.linalg.norm(uv[:,None,:]-uv[None,:,:],axis=2);np.fill_diagonal(dist,np.inf)
        valid=(dist.min(axis=1)>=min_separation)&(uv[:,0]>15)&(uv[:,0]<1265)&(uv[:,1]>15)&(uv[:,1]<945)
        if visible is not None:valid &= np.isin(np.arange(12),visible)
        candidates=np.flatnonzero(valid)
        if len(candidates)<2:continue
        chosen=rng.choice(candidates,min(len(candidates),int(rng.integers(3,6))),replace=False)
        for marker in chosen:
            true_labels.append(LABELS[marker]);counters.append(counter);packet_boots.append(boot);clean.append(uv[marker]);frame_indices.append(fi)
            minimum_separation=min(minimum_separation,float(dist[marker].min()))
    clean=np.array(clean);assert len(clean)>100
    ids=rng.permutation(np.arange(1000,1000+len(clean))).tolist();count=round(outliers*len(clean));bad=set(rng.choice(len(clean),count,replace=False).tolist())
    if burst and count:
        first=len(clean)//2-count//4;bad=set(range(first,first+count//2))
        while len(bad)<count:bad.add(int(rng.integers(len(clean))))
    answer['associations']={};packets=[];min_clutter=float('inf');visibility={l:0 for l in LABELS}
    for i,(uv,c,b,pid,identity,fi) in enumerate(zip(clean,counters,packet_boots,ids,true_labels,frame_indices)):
        measured=uv+rng.normal(0,.24,2);label=identity
        if i in bad:
            label=None
            for attempt in range(100):
                shift=np.array([65.,-55.]) if burst and attempt==0 else rng.choice([-1,1],2)*rng.uniform(40,150,2)
                measured=uv+shift
                if np.linalg.norm(points[fi]-measured,axis=1).min()>=30:break
            else:raise AssertionError('cannot make separated clutter')
            min_clutter=min(min_clutter,float(np.linalg.norm(points[fi]-measured,axis=1).min()))
        else:visibility[label]+=1
        answer['associations'][str(pid)]=label
        payload=PAYLOAD.pack(pid,b,c,*measured);packet=payload+struct.pack('<I',zlib.crc32(payload));packets.append(packet)
        if burst and rng.random()<.05:packets.append(packet)
    assert min(v for v in visibility.values() if v)>5,visibility
    rng.shuffle(packets);(folder/'camera.bin').write_bytes(HEADER.pack(b'G1UA',len(packets))+b''.join(packets));save(folder/'manifest.json',manifest);save(folder/'answer.json',answer)
    probes={}
    for side in ('left','right'):
        q=traj.q[side][rng.integers(0,len(traj.times),144)]+rng.uniform(-.15,.15,(144,7));m=rng.integers(0,6,144)
        probes[side]={'q':q.tolist(),'markers':m.tolist(),'pixels':project_static(q,m,side,answer).tolist()}
    dc=[];db=[];dl=[]
    for boot in labels:
        cs=[c for c,b in zip(counters,packet_boots) if b==boot];assert len(cs)>30
        dc.extend(rng.uniform(min(cs),max(cs),60).tolist());db.extend([int(boot)]*60);dl.extend(rng.choice(LABELS,60).tolist())
    private={'ids':ids,'boots':packet_boots,'counters':counters,'original_labels':true_labels,
             'times':nominal_times(counters,packet_boots,manifest,answer).tolist(),'probes':probes,
             'dynamic_counters':dc,'dynamic_boots':db,'dynamic_labels':dl,'dynamic_pixels':predict(traj,dl,dc,db,manifest,answer).tolist(),
             'source_episode':episode,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'outlier_fraction':outliers,'drop_fraction':drop,'burst':burst,
             'minimum_inlier_separation_px':minimum_separation,'minimum_clutter_separation_px':min_clutter if bad else None,'inliers_per_identity':visibility}
    if not public:save(folder/'private.json',private)
    print(name,'episode',episode,'points',len(ids),'clutter',count,'min separation',round(minimum_separation,2),flush=True)


# Campaigns use independent trajectories but one shared physical rig.
def campaign(name,episodes,seed,public=False):
    folder=ROOT/('environment/public' if public else 'tests/cases')/name
    records=[];shared=None
    for i,(ep,visible) in enumerate(zip(episodes,[[0,1,2],[9,10,11],[3,4,5,6,7,8]])):
        rec=f"capture_{[37,12,84][i]}"
        make_case(name+'/'+rec,ep,810,1 if i<2 else 2,.18+.05*i,.12+.03*i,False,seed+17*i,public=public,shared=shared,visible=visible)
        answer=json.loads((folder/rec/'answer.json').read_text())
        if shared is None:shared={k:answer[k] for k in ('X_left','X_right','Y','zeros','camera')}
        records.append(rec)
    save(folder/'campaign.json',{'records':records[::-1]})
    answers={r:json.loads((folder/r/'answer.json').read_text()) for r in records}
    save(folder/'answer.json',{'shared':shared,'records':{r:{k:answers[r][k] for k in ('clocks','associations')} for r in records}})

campaign('example_a',[0,0,0],106111,True)
campaign('example_b',[0,0,0],106102,True)
campaign('campaign_a',[1,2,3],106111)
campaign('campaign_b',[3,1,2],106113)
# A state-convention witness forces actual state use at the campaign level.
src=ROOT/'tests/cases/campaign_a';dst=ROOT/'tests/cases/state_witness'
shutil.copytree(src,dst,dirs_exist_ok=True)
delta=.47;D=np.eye(4);D[:3,:3]=Rotation.from_rotvec([0,-delta,0]).as_matrix()
for rec in json.loads((dst/'campaign.json').read_text())['records']:
    f=dst/rec;rows=json.loads((f/'states.json').read_text())
    for row in rows:row['state'][0]+=delta;row['state'][8]+=delta
    save(f/'states.json',rows)
    a=json.loads((f/'answer.json').read_text());a['Y']=(np.array(a['Y'])@D).tolist();save(f/'answer.json',a)
    p=json.loads((f/'private.json').read_text())
    for side in ('left','right'):
        for q in p['probes'][side]['q']:q[0]+=delta
    save(f/'private.json',p)
a=json.loads((dst/'answer.json').read_text());a['shared']['Y']=(np.array(a['shared']['Y'])@D).tolist();save(dst/'answer.json',a)
