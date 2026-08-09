# Session Briefs

Plain-English map for `AMMI Geometric Deep Learning Course - Second Edition (2022)`.

## Session 1: Lecture 1 (Introduction) - Michael Bronstein

Bronstein opens the course by defining geometric deep learning as a unifying program for structured domains, framing the rest of the lectures as answers to one architectural question rather than as isolated model families.

## Session 2: Lecture 2 (Learning in High Dimensions) - Joan Bruna

Bruna explains why high-dimensional learning needs bias, using the failure modes of generic function fitting to motivate the need for geometric and structural constraints.

## Session 3: Lecture 3 (Geometric Priors I) - Taco Cohen

Cohen introduces geometric priors and the invariance/equivariance vocabulary that later lectures keep reusing whenever they ask what a model should preserve under transformation.

## Session 4: Lecture 4 (Geometric Priors II) - Joan Bruna

Bruna deepens the priors discussion by making architectural consequences explicit: good priors reduce sample complexity precisely because they rule out the wrong hypothesis classes.

## Session 5: Lecture 5 (Graphs & Sets) - Petar Veličković

Veličković starts the discrete-domain block by contrasting sets and graphs, showing how the geometry of the domain determines whether aggregation or relational propagation is the key operator.

## Session 6: Lecture 6 (Graphs & Sets II) - Petar Veličković

The second graphs lecture focuses on graph expressivity and the limits of standard message passing, setting up several of the frontier seminars that come later.

## Session 7: Lecture 7 (Grids) - Joan Bruna

Bruna re-reads CNNs through the course blueprint and treats grids as a special structured domain where translation symmetry and convolution line up unusually cleanly.

## Session 8: Lecture 8 (Groups & Homogeneous spaces) - Taco Cohen

Cohen moves from intuitive symmetry talk to groups and homogeneous spaces, giving the course its most explicit algebraic account of equivariant operator design.

## Session 9: Lecture 9 (Manifolds) - Michael Bronstein

Bronstein's manifolds lecture shifts the course into intrinsically curved domains and emphasizes that useful geometry is often about the space itself, not only about its Euclidean embedding.

## Session 10: Lecture 10 (Gauges) - Taco Cohen

Cohen's gauges lecture handles the harder case where one global coordinate frame is unavailable, so the model has to stay consistent across local frames instead.

## Session 11: Lecture 11 (Beyond Groups) - Petar Veličković

Veličković uses the beyond-groups lecture to widen the conceptual aperture of the field and ask what other mathematical objects can carry learnable structural bias.

## Session 12: Lecture 12 (Applications & Trends) - Michael Bronstein

Bronstein closes the main lecture sequence by surveying applications and trends, turning the course from a mathematical tour into a research agenda with visible open edges.

## Session 13: Seminar 1 (Physics-based GNNs) - Francesco Di Giovanni

The physics-based GNN seminar shows the blueprint operating in scientific machine learning, where graph structure and symmetry are tied directly to physical interactions and dynamics.

## Session 14: Seminar 2 (Subgraph GNNs) - Fabrizio Frasca

Frasca's subgraph seminar tackles graph expressivity head-on, arguing that richer computational units are needed when standard neighborhood aggregation cannot see the right structure.

## Session 15: Seminar 3 (Equivariance in ML) - Geordie Williamson

Williamson's equivariance seminar broadens the symmetry discussion and gives the audience another angle on why transformation-aware modeling matters beyond the canonical lecture examples.

## Session 16: Seminar 4 (Neural Sheaf Diffusion) - Cristian Bodnar

Bodnar's neural sheaf diffusion seminar pushes graph learning into a richer local-to-global consistency framework, illustrating what beyond-groups research looks like in practice.

## Session 17: Seminar 5 (AlphaFold) - Russ Bates

The AlphaFold seminar gives the course its clearest flagship application: geometric bias is shown not as elegant theory but as a practical ingredient in a world-changing system.
