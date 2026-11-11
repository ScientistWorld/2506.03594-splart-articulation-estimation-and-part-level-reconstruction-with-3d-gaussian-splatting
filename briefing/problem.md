# Problem Definition

## Research Question

Reconstruct a two-part articulated object (a static parent and one moving child part) and estimate its joint from observations of the object at two end states of its motion, without 3D labels, part annotations or category priors. The joint type (revolute or prismatic) is known. A solution must say which parts of the reconstruction are static and which move, estimate the joint (axis, pivot for revolute joints, and the motion amount from state 0 to state 1), and produce a part-level reconstruction that renders correctly at new viewpoints and at new articulation states between, and slightly beyond, the two observed ones.

## Why It Matters

Articulated digital twins (doors, drawers, lids, levers, sliders) are needed for robot manipulation and AR/VR. Capturing an object twice with a camera is cheap; annotating parts and joints, or scanning with 3D sensors, is not.

## Observations Per Scene

For each of the two states, independently:

- 20 posed RGB images (48 x 48, white background) with known intrinsics and world-to-camera extrinsics; each state has its own cameras on the upper hemisphere;
- a sparse, noisy, coloured point cloud of the visible surface (380 to 600 points plus a few floaters), sampled independently per state: there is no point correspondence between the states, point order is random and the counts differ.

Objects come in many shapes and random poses, colours and textures; some families appear only in the held-out test scenes. Ground-truth answers for the train scenes are visible; those of the test scenes are not.

## Success Criteria

A good method recovers the joint accurately on most scenes (axis within 5 degrees; revolute: pivot line within 0.05 and rotation within 10 degrees; prismatic: translation within 0.05, in scene units where objects have radius about 0.6), and its static/mobile reconstruction renders the object correctly at unseen views and articulation states, with correct part segmentation and part geometry.
