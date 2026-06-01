# Problem Definition

## Research Question

Recover a two-part articulated object from posed observations captured at two end states of motion. A successful system should infer which object elements belong to the static parent and moving child part, estimate the articulation parameters for either a revolute or prismatic joint, and reconstruct the object consistently across the observed states.

## Why It Matters

Articulated object reconstruction enables digital twins for robotics, AR/VR, and manipulation planning without requiring manual part annotations or 3D supervision.

## Success Criteria

The method should accurately estimate joint axis and motion amount, identify static and moving parts, preserve 3D geometry across the two observed states, and outperform a no-motion/static-object baseline under the same data and evaluation protocol.
