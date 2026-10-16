# Dual-arm unlabeled visual calibration

This task uses a synthetic measurement rig driven by real G1 joint-state recordings. It is not manufacturer-accurate robot geometry. The two supplied helper modules define the authoritative forward model. Transform matrices act on local column vectors, with metres/radians/seconds/pixels as units.

`states.json` is ordered and contains timestamp plus a 34-element state vector. `kinematics.Trajectory` uses columns 0..6 for the left arm and 8..14 for the right arm. Joint values are linearly interpolated in time BEFORE forward kinematics. Each arm has two unknown constant encoder-zero offsets, added to zero-based joint indices 1 and 3, each in [-0.18,0.18] radians. Their physical effects are inside the chain, not extra mounting rotations. The bases are fixed at (0,+0.22,0) and (0,-0.22,0).

Each arm carries the same six asymmetric noncoplanar markers defined by `camera_model.MARKERS`. Each arm's own rigid target-to-flange mount is unknown (`X_left`, `X_right`), with arbitrary rotation and translation norm <=0.25m. The common robot-base-to-camera transform Y has arbitrary rotation and translation norm <=3.5m. For side s and its marker p:

`z = Y A_s(t, zeros_s) X_s [p;1]`.

Positive depth is required. The camera model is `u=640+fx*x*(1+k1*r2+k2*r2^2)`, `v=480+fy*y*(1+k1*r2+k2*r2^2)`, with x=z_x/z_z, y=z_y/z_z, r2=x*x+y*y. Image size 1280x960. fx/fy are independently in [750,1250], k1 in [-0.18,0.18], k2 in [-0.06,0.06]. Principal point, skew and tangential distortion are fixed as above.

For each manifest boot, set s=counter-c0. Nominal time is `t0=offset+rate*s+curvature*s*s`. offset is within 1.25s of host_hint; rate in [0.90,1.10], curvature in [-0.003,0.003]. Clocks are strictly increasing. Rolling shutter exposes row v at `t=t0+readout*(v/960-0.5)` with unknown readout in [0.008,0.035]s. All center and exposure times must remain inside the state record.

Each nominal capture time shows only a subset of the 12 possible (arm,marker) identities, at most once per identity. Observation order is arbitrary and provides no marker/arm identity. Occlusion changes the visible subset between frames. There are no persistent point-track IDs. Packet IDs are arbitrary opaque IDs only. The same counter can occur on multiple detections from one image.

Inlier pixel noise is independent Gaussian sigma<=0.30 pixels per component. Between 0% and 36% of unique packets are clutter/outliers. Up to 44% of scheduled frames may be dropped, including contiguous burst loss. New adversarial records may retain true detections as close as 3 pixels to the nearest other marker projection. Clutter may form a second coherent moving target constellation. It may lie close to a correct projection; a large nearest-neighbor rejection margin is NOT guaranteed. Across a record, true detections outnumber clutter. For identifiability, every retained true point is at least 3 pixels from the other 11 correct noiseless projections at its nominal capture time. Entire campaigns have sufficient motion and all marker identities represented jointly. Inliers are inside the image. Random/burst frame loss and exact retransmissions also occur.

`camera.bin`: header `<4sI`, magic `G1UA`, packet count. Each 25-byte packet is `<IBd2fI`: packet ID u32, boot u8, counter f64, u/v float32, CRC32 u32 over the preceding 21 bytes. Exact identical duplicates must be deduplicated; conflicting duplicates, bad CRC, bad magic/length or nonfinite counters/pixels are malformed. They require nonzero exit and no output file.

A campaign directory contains `campaign.json` with `{"records":["capture_37",...]}` and those child directories. Each child has its own states.json, manifest.json and camera.bin. Record order and names carry no geometric meaning. Packet IDs and boot IDs are local to a record: reuse across different records is legal, and conflicts are checked ONLY within a record. State timestamps and host hints are local to their own record, not a global timeline. Initially the same rig (X_left, X_right, Y, zeros, fx, fy, k1, k2 and readout) is shared across every record. A record may subsequently have one unknown physical mounting slip on either arm. Camera parameters, Y and encoder offsets remain shared and fixed. Clocks and associations are record-specific. Each campaign is independent of other campaigns.

Some records may show just one arm and a strict subset of its markers for the entire capture; other records provide complementary marker subsets. No individual record is guaranteed to identify every rig parameter or contain all identities. The campaign jointly has sufficient excitation and contains all identities. There is no unknown camera relocation between records.

Mount regimes: Within each record, order unique frames by the listed manifest boot order, then increasing counter within each boot. Frame indices are zero-based in that order. There are zero or one slips per record, strictly between 40% and 80% of its frames. The first 40% are stable. At the slip, exactly one arm changes its rigid target-to-flange transform; it stays constant afterwards. The initial transform equals the campaign shared X for that arm. The other arm and the camera do not change. All transforms obey the same bounds as above. The event is not marked in the data. Occlusion and clutter alone do not count as slips.

Clutter may follow the same kinematics with an alternative fixed mount and persist across a true mounting change.

## Required output schema

The following key sets are mandatory and exact. Every listed key is required; extra keys are rejected in every object below, including nested objects. JSON object key order is irrelevant.

| Object | Exact required keys |
| --- | --- |
| Top-level output | `shared`, `records` |
| `shared` | `X_left`, `X_right`, `Y`, `zeros`, `camera` |
| `shared.zeros` | `left`, `right` |
| `shared.camera` | `fx`, `fy`, `k1`, `k2`, `readout` |
| `records` | Exactly the record names in the input `campaign.json` records array |
| `records[NAME]` | `clocks`, `associations`, `segments` |
| `records[NAME].clocks` | Exactly the decimal string representations of that record's manifest boot IDs |
| `records[NAME].clocks[BOOT_ID]` | `offset`, `rate`, `curvature` |
| `records[NAME].associations` | Exactly the decimal string representations of all unique packet IDs in that record, after deduplication |
| Each object in `records[NAME].segments` | `start_frame`, `X_left`, `X_right` |

`segments` is an array of one or two objects, as determined by the mount regimes. `start_frame` must be a JSON integer (not a boolean or a floating-point value). Mount and camera transforms are numeric 4-by-4 arrays; each encoder-zero entry is a numeric two-element array. Camera and clock values are finite numbers subject to the bounds below and above. Association values are `null` or one of `left:0` through `left:5` and `right:0` through `right:5`. Record, boot and packet namespaces are local as specified above. Array dimensions, numeric bounds and geometric checks remain required in addition to these key sets.

The first segment starts at frame 0 and uses the shared initial mounts. For a record with a slip, the second segment starts at the first affected frame and specifies both post-event mounts. Segment count must match the number of physical regimes; the transition tolerance is 3 retained frames.

Transforms must be proper rigid transforms to 1e-5 and satisfy the bounds above. Duplicate assigned identity within one local (boot,counter) is forbidden. Output must not exist if ANY record has malformed binary input, including a malformed last record. If the requested output path already exists, remove the stale output before validation; a failed invocation must not leave it behind.

Grading checks EVERY record with the ONE shared calibration: >=95% correct inlier identities; clutter rejection precision and recall >=0.90; static held-out projection error P95 <=2 pixels on each arm in each regime; dynamic held-out projection error P95 <=2 pixels; clock RMSE <=0.060s and maximum <=0.180s; positive clock derivative and valid exposure domain. Static probes use recorded configurations perturbed by <=0.15 radians. Parameter equality is not required. Hidden cases use different source episodes, clocks, camera orientations, visibility and clutter.

Only `/app/calibrate.py` is submitted. Each complete campaign invocation has a 240-second ceiling with 2 CPUs and 4 GB RAM. Corrupt inputs must be rejected within 15 seconds without producing output.
