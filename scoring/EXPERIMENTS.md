# Experiment Overview

Both experiments are scored on the same 26 held-out scenes (and reported on the 18 visible train scenes). Each scene shows a two-part articulated object at two end states of its joint through posed RGB images and a sparse, noisy, uncorresponded point cloud per state.

## articulation_estimation (weight 0.6)

Establishes whether a method recovers the joint of the object — its axis, where a rotation axis passes, and how far the part moves between the two states — reliably across many object shapes, including object families never seen during development. The success rate under fixed error thresholds is the headline number; the truncated error averages measure how precise the recovered joints are.

## part_reconstruction (weight 0.4)

Establishes whether the method's output is a usable part-level digital twin: rendered at unseen viewpoints and at unseen articulation states (interpolated and slightly extrapolated), it must look like the object, place depth correctly and label static versus moving pixels correctly, and its static and moving geometry must match the true surfaces. A scene whose joint estimate fails contributes worst values, so reconstruction quality only counts where the articulation is right.
