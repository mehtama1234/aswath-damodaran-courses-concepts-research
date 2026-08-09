#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


THEMES: list[dict[str, Any]] = [
    {
        "id": "geometric-deep-learning-starts-by-rejecting-unstructured-learning",
        "name": "Geometric Deep Learning Starts By Rejecting Unstructured Learning",
        "summary": "The opening block argues that modern machine learning needs explicit structural bias. Geometry is introduced as the language for deciding what kind of structure a domain contains and how a model should respect it.",
        "lenses": ["inductive-bias", "high-dimensional-learning", "representation"],
        "evidence_sessions": [1, 2, 3, 12],
        "subthemes": [
            {
                "name": "High-dimensional learning breaks down without good priors",
                "summary": "The introduction and high-dimensional lecture explain why generic learning becomes sample-hungry and unstable when structure is ignored.",
                "evidence_sessions": [1, 2],
            },
            {
                "name": "Geometric priors are the repair strategy, not a decorative add-on",
                "summary": "The first priors lectures turn structure into a design principle: the model should be built around the transformations and relations that define the data.",
                "evidence_sessions": [3, 4],
            },
            {
                "name": "The course treats geometric deep learning as a unifying blueprint",
                "summary": "The field is presented as an umbrella view across graphs, grids, groups, manifolds, and newer application domains rather than as one narrow architecture family.",
                "evidence_sessions": [1, 12],
            },
        ],
    },
    {
        "id": "symmetry-is-the-central-language-for-encoding-structure",
        "name": "Symmetry Is The Central Language For Encoding Structure",
        "summary": "A core claim of the course is that invariance and equivariance are the right abstractions for deciding what information a model should preserve and how it should transform.",
        "lenses": ["symmetry", "equivariance", "group-theory"],
        "evidence_sessions": [3, 4, 8, 10, 15],
        "subthemes": [
            {
                "name": "Invariance and equivariance formalize what should stay fixed or transform predictably",
                "summary": "The priors block gives the course its control vocabulary: which transformations should leave predictions unchanged, and which should move them in rule-bound ways.",
                "evidence_sessions": [3, 4],
            },
            {
                "name": "Groups and homogeneous spaces make global symmetry computational",
                "summary": "The groups lecture translates algebraic symmetry into practical model construction, showing how familiar convolution is only one special case.",
                "evidence_sessions": [8],
            },
            {
                "name": "Later talks push symmetry beyond textbook global actions",
                "summary": "The seminar and late-lecture material widens the picture from standard group actions to more local, approximate, or abstract forms of structured equivariance.",
                "evidence_sessions": [10, 11, 15],
            },
        ],
    },
    {
        "id": "domains-differ-so-the-operators-have-to-differ",
        "name": "Domains Differ, So The Operators Have To Differ",
        "summary": "The middle lectures show that there is no single universal operator. Sets, graphs, and grids each impose different locality, aggregation, and weight-sharing constraints.",
        "lenses": ["sets", "graphs", "grids"],
        "evidence_sessions": [5, 6, 7],
        "subthemes": [
            {
                "name": "Sets require permutation-invariant aggregation",
                "summary": "Set learning starts from the idea that ordering is accidental, so the architecture has to treat reordering as irrelevant.",
                "evidence_sessions": [5],
            },
            {
                "name": "Graphs require relation-aware locality and message passing",
                "summary": "Graph lectures show how relational neighborhoods become the unit of computation and why expressivity is tied to how information is propagated.",
                "evidence_sessions": [5, 6],
            },
            {
                "name": "Grids recover classical convolution as one structured special case",
                "summary": "The grids lecture re-anchors CNN intuitions inside the broader course blueprint by treating images as a particularly regular geometric domain.",
                "evidence_sessions": [7],
            },
        ],
    },
    {
        "id": "manifolds-and-local-frames-generalize-euclidean-intuition",
        "name": "Manifolds And Local Frames Generalize Euclidean Intuition",
        "summary": "The advanced geometry block moves beyond flat ambient spaces. Manifolds and gauge structure are used to show how learning changes when there is no single global coordinate system.",
        "lenses": ["manifolds", "gauges", "local-geometry"],
        "evidence_sessions": [9, 10, 11],
        "subthemes": [
            {
                "name": "Manifolds turn curved spaces into first-class learning domains",
                "summary": "The manifolds lecture reframes geometry as an intrinsic property of the data domain rather than an afterthought on top of Euclidean coordinates.",
                "evidence_sessions": [9],
            },
            {
                "name": "Gauge equivariance replaces one global frame with compatible local ones",
                "summary": "The gauges lecture handles cases where local reference frames matter and consistency across them is the real design constraint.",
                "evidence_sessions": [10],
            },
            {
                "name": "Beyond-groups thinking asks what other organizing structures matter",
                "summary": "The late lecture signals that useful inductive bias may come from objects more general than classical groups, forcing the field to keep expanding its toolkit.",
                "evidence_sessions": [11],
            },
        ],
    },
    {
        "id": "the-frontier-is-measured-by-working-applications-not-only-theory",
        "name": "The Frontier Is Measured By Working Applications, Not Only Theory",
        "summary": "The course ends by showing the blueprint under pressure in active research settings. Scientific machine learning, expressive graph models, sheaf methods, and protein structure prediction all test whether geometric bias pays off in practice.",
        "lenses": ["applications", "research-frontier", "scientific-ml"],
        "evidence_sessions": [12, 13, 14, 15, 16, 17],
        "subthemes": [
            {
                "name": "Applications and trends turn the blueprint into a research agenda",
                "summary": "The final lecture takes stock of where the framework has already worked and where the next conceptual bottlenecks lie.",
                "evidence_sessions": [12],
            },
            {
                "name": "Scientific and expressive graph variants push beyond vanilla message passing",
                "summary": "Physics-based GNNs, subgraph methods, and sheaf diffusion each extend the graph toolkit to handle stronger inductive requirements.",
                "evidence_sessions": [13, 14, 16],
            },
            {
                "name": "Equivariance and protein structure show the payoff of getting geometry right",
                "summary": "The late seminar pair uses abstract equivariance and AlphaFold to show that the course is ultimately about usable intelligence on structured domains, not isolated mathematical elegance.",
                "evidence_sessions": [15, 17],
            },
        ],
    },
]


CONCEPTS: list[dict[str, Any]] = [
    {
        "slug": "geometric-deep-learning-blueprint",
        "name": "Geometric deep learning blueprint",
        "theme_id": THEMES[0]["id"],
        "theme_name": THEMES[0]["name"],
        "summary": "Geometric deep learning is presented as a single organizing question: what symmetries, relations, and geometric constraints define the data domain, and how should the model honor them?",
        "why_it_matters": "This is the course's master frame. It turns a long list of architectures into one reusable design logic.",
        "core_idea": "Instead of memorizing separate families of models, the course teaches a blueprint for moving from domain structure to inductive bias to operator design.",
        "lenses": ["blueprint", "inductive-bias", "unification"],
        "strongest_sessions": [1, 12],
        "subtheme_refs": [
            THEMES[0]["subthemes"][2]["name"],
            THEMES[4]["subthemes"][0]["name"],
        ],
        "broader_patterns": [
            "Architecture choices are only defensible when tied back to domain structure.",
            "The field keeps expanding because new domains expose new geometric constraints.",
        ],
        "applied_uses": [
            "Choosing whether a problem is better framed as a set, graph, grid, manifold, or hybrid domain.",
            "Explaining why CNNs, GNNs, and equivariant models are related rather than unrelated inventions.",
        ],
        "analytical_frames": [
            {"title": "Design Question", "text": "What transformations and relations define the domain?"},
            {"title": "Modeling Question", "text": "Which operator respects that structure while staying learnable?"},
        ],
    },
    {
        "slug": "inductive-bias-in-high-dimensions",
        "name": "Inductive bias in high dimensions",
        "theme_id": THEMES[0]["id"],
        "theme_name": THEMES[0]["name"],
        "summary": "Learning in high dimensions needs prior structure because data alone is rarely enough to identify useful functions.",
        "why_it_matters": "It explains why the rest of the course exists. Without this problem, there is no need for geometric deep learning.",
        "core_idea": "The curse is not just computational scale. It is the mismatch between the number of possible functions and the amount of supervision available.",
        "lenses": ["high-dimensions", "sample-complexity", "bias"],
        "strongest_sessions": [1, 2],
        "subtheme_refs": [THEMES[0]["subthemes"][0]["name"]],
        "broader_patterns": [
            "Data efficiency comes from bias, not from optimism about unlimited samples.",
            "Useful priors shrink the search space toward functions the world actually contains.",
        ],
        "applied_uses": [
            "Motivating symmetry-aware or locality-aware design in real tasks.",
            "Defending structured architectures against generic fully-connected baselines.",
        ],
        "analytical_frames": [
            {"title": "Failure Mode", "text": "Unstructured models can fit too much with too little guidance."},
            {"title": "Repair", "text": "Inject domain assumptions so the learner searches a narrower, better function class."},
        ],
    },
    {
        "slug": "geometric-priors",
        "name": "Geometric priors",
        "theme_id": THEMES[0]["id"],
        "theme_name": THEMES[0]["name"],
        "summary": "A geometric prior says that the data live on a structured domain and that the hypothesis class should be organized around that structure.",
        "why_it_matters": "This concept is the bridge from abstract motivation to actual architecture design.",
        "core_idea": "The prior is not merely a regularizer. It is the decision to build the model around transformations, neighborhoods, or coordinate relationships that the problem naturally contains.",
        "lenses": ["priors", "structure", "model-design"],
        "strongest_sessions": [3, 4],
        "subtheme_refs": [THEMES[0]["subthemes"][1]["name"], THEMES[1]["subthemes"][0]["name"]],
        "broader_patterns": [
            "The strongest priors improve both generalization and interpretability.",
            "Bad priors fail when they import the wrong geometry into the task.",
        ],
        "applied_uses": [
            "Choosing neighborhood systems for graphs or local charts for manifolds.",
            "Testing whether an architecture is aligned with the real symmetries of the data.",
        ],
        "analytical_frames": [
            {"title": "Source", "text": "Priors come from what is stable under transformation in the domain."},
            {"title": "Tradeoff", "text": "Too little prior wastes data; too much prior can hard-code the wrong world."},
        ],
    },
    {
        "slug": "symmetry-invariance-and-equivariance",
        "name": "Symmetry, invariance, and equivariance",
        "theme_id": THEMES[1]["id"],
        "theme_name": THEMES[1]["name"],
        "summary": "Symmetry is the course's preferred language for telling a model what should stay unchanged and what should transform predictably.",
        "why_it_matters": "It is the conceptual core behind CNNs, group-equivariant models, and much of the later geometry block.",
        "core_idea": "Invariance asks for unchanged outputs under a transformation, while equivariance asks for outputs that transform in a controlled corresponding way.",
        "lenses": ["symmetry", "invariance", "equivariance"],
        "strongest_sessions": [3, 4, 15],
        "subtheme_refs": [THEMES[1]["subthemes"][0]["name"], THEMES[4]["subthemes"][2]["name"]],
        "broader_patterns": [
            "The right symmetry can dramatically reduce sample complexity.",
            "Abstract equivariance often becomes valuable only when it is tied back to a domain task.",
        ],
        "applied_uses": [
            "Image recognition under translation or rotation.",
            "Scientific prediction where physical laws are coordinate-independent.",
        ],
        "analytical_frames": [
            {"title": "Invariance", "text": "The answer should not change when the input is transformed."},
            {"title": "Equivariance", "text": "The answer should change in a rule-bound way that mirrors the input transformation."},
        ],
    },
    {
        "slug": "sets-and-permutation-invariance",
        "name": "Sets and permutation invariance",
        "theme_id": THEMES[2]["id"],
        "theme_name": THEMES[2]["name"],
        "summary": "Set learning begins by refusing to treat order as meaningful when the domain itself does not care about order.",
        "why_it_matters": "It is one of the cleanest examples of matching architecture to domain geometry.",
        "core_idea": "If reordering elements should not matter, the aggregation rule has to be permutation invariant.",
        "lenses": ["sets", "aggregation", "permutation-invariance"],
        "strongest_sessions": [5],
        "subtheme_refs": [THEMES[2]["subthemes"][0]["name"]],
        "broader_patterns": [
            "Simple domain assumptions can radically constrain valid architectures.",
            "Aggregation is not an implementation detail; it is the mathematical heart of the model class.",
        ],
        "applied_uses": [
            "Point clouds, bags of instances, and unordered collections.",
            "Any task where indexing is accidental rather than meaningful.",
        ],
        "analytical_frames": [
            {"title": "Constraint", "text": "Permutation of inputs should not alter the representation or prediction."},
            {"title": "Design Consequence", "text": "Pooling and aggregation become first-class architectural choices."},
        ],
    },
    {
        "slug": "graph-message-passing",
        "name": "Graph message passing",
        "theme_id": THEMES[2]["id"],
        "theme_name": THEMES[2]["name"],
        "summary": "Graph neural learning treats nodes, edges, and neighborhoods as the basic geometry of computation.",
        "why_it_matters": "Graphs are the course's most flexible structured domain and the staging ground for many later applications.",
        "core_idea": "Representation learning on graphs is built from local information exchange, with expressivity determined by how messages are formed, aggregated, and updated.",
        "lenses": ["graphs", "message-passing", "locality"],
        "strongest_sessions": [5, 6],
        "subtheme_refs": [THEMES[2]["subthemes"][1]["name"], THEMES[4]["subthemes"][1]["name"]],
        "broader_patterns": [
            "Graph structure is both a source of power and a bottleneck for expressivity.",
            "Many later graph variants are attempts to fix what plain message passing misses.",
        ],
        "applied_uses": [
            "Molecules, social networks, physical interaction systems, and knowledge graphs.",
            "Problems where relations matter at least as much as attributes.",
        ],
        "analytical_frames": [
            {"title": "Locality", "text": "Information is exchanged through neighborhoods rather than through one flat vector."},
            {"title": "Expressivity", "text": "The architecture is judged by which graph distinctions it can and cannot represent."},
        ],
    },
    {
        "slug": "convolution-on-grids",
        "name": "Convolution on grids",
        "theme_id": THEMES[2]["id"],
        "theme_name": THEMES[2]["name"],
        "summary": "The grids lecture recasts familiar image convolution as one especially regular case of geometric deep learning.",
        "why_it_matters": "It prevents students from treating CNNs as the default model for everything. They become one domain-matched answer among many.",
        "core_idea": "Grid domains support strong forms of translation symmetry and weight sharing, which makes convolution natural rather than arbitrary.",
        "lenses": ["grids", "cnn", "translation"],
        "strongest_sessions": [7],
        "subtheme_refs": [THEMES[2]["subthemes"][2]["name"], THEMES[1]["subthemes"][1]["name"]],
        "broader_patterns": [
            "The regularity of images hides how special the grid case really is.",
            "The broader field generalizes convolution by loosening what counts as a neighborhood or symmetry.",
        ],
        "applied_uses": [
            "Image and signal tasks on regular lattices.",
            "Explaining how CNN intuitions map into graph or group settings.",
        ],
        "analytical_frames": [
            {"title": "Why It Works", "text": "The grid gives a stable notion of nearby pixels and translation-consistent filters."},
            {"title": "What It Teaches", "text": "Classical deep learning already contains geometry when the domain makes it obvious."},
        ],
    },
    {
        "slug": "groups-and-homogeneous-spaces",
        "name": "Groups and homogeneous spaces",
        "theme_id": THEMES[1]["id"],
        "theme_name": THEMES[1]["name"],
        "summary": "Groups and homogeneous spaces formalize global transformation structure so equivariant operators can be defined with precision.",
        "why_it_matters": "This is where the course moves from intuition about symmetry to a deeper operator-design toolkit.",
        "core_idea": "A domain may be acted on by a symmetry group, and that action can be used to define how features and filters should transform.",
        "lenses": ["groups", "homogeneous-spaces", "equivariant-operators"],
        "strongest_sessions": [8],
        "subtheme_refs": [THEMES[1]["subthemes"][1]["name"]],
        "broader_patterns": [
            "Convolution is generalized by replacing translation with broader group action.",
            "The math matters because it tells you exactly what consistency condition the model must satisfy.",
        ],
        "applied_uses": [
            "Rotation-aware or pose-aware prediction tasks.",
            "Systems where transformations form a clean algebraic family.",
        ],
        "analytical_frames": [
            {"title": "Algebraic Layer", "text": "The group tells you how transformations compose."},
            {"title": "Geometric Layer", "text": "The homogeneous space tells you where those transformations act."},
        ],
    },
    {
        "slug": "manifolds-for-learning",
        "name": "Manifolds for learning",
        "theme_id": THEMES[3]["id"],
        "theme_name": THEMES[3]["name"],
        "summary": "Manifolds describe domains that are locally Euclidean but globally curved, forcing models to respect intrinsic rather than ambient geometry.",
        "why_it_matters": "It opens the door to non-flat domains without collapsing back into naive coordinate tricks.",
        "core_idea": "What matters is not just where the data are embedded, but what the domain looks like from the inside.",
        "lenses": ["manifolds", "intrinsic-geometry", "curvature"],
        "strongest_sessions": [9],
        "subtheme_refs": [THEMES[3]["subthemes"][0]["name"]],
        "broader_patterns": [
            "Coordinate choices can hide the real invariants of the problem.",
            "Many structured domains demand local reasoning stitched into a global object.",
        ],
        "applied_uses": [
            "Shape analysis, geometric computer vision, and learning on curved spaces.",
            "Domains where global Euclidean assumptions distort the real topology or metric structure.",
        ],
        "analytical_frames": [
            {"title": "Local View", "text": "Each patch looks Euclidean enough for familiar operations."},
            {"title": "Global View", "text": "The overall domain can still be curved, stitched, or topologically nontrivial."},
        ],
    },
    {
        "slug": "gauge-equivariance",
        "name": "Gauge equivariance",
        "theme_id": THEMES[3]["id"],
        "theme_name": THEMES[3]["name"],
        "summary": "Gauge equivariance handles problems where local frames matter but no single global frame is valid.",
        "why_it_matters": "It is one of the most conceptually advanced points in the course and shows why local consistency can replace global symmetry.",
        "core_idea": "Features can be represented relative to local coordinate frames as long as the model transforms them consistently under changes of gauge.",
        "lenses": ["gauges", "local-frames", "equivariance"],
        "strongest_sessions": [10],
        "subtheme_refs": [THEMES[3]["subthemes"][1]["name"], THEMES[1]["subthemes"][2]["name"]],
        "broader_patterns": [
            "Local geometric structure can be more important than any one global coordinate system.",
            "Advanced equivariant design is often about compatibility between overlapping local descriptions.",
        ],
        "applied_uses": [
            "Directional features on surfaces or manifolds.",
            "Domains where tangent-space information matters.",
        ],
        "analytical_frames": [
            {"title": "Problem", "text": "There is no globally preferred frame."},
            {"title": "Solution", "text": "Use local frames and enforce transformation consistency across them."},
        ],
    },
    {
        "slug": "beyond-groups",
        "name": "Beyond groups",
        "theme_id": THEMES[3]["id"],
        "theme_name": THEMES[3]["name"],
        "summary": "Beyond-groups thinking asks what other mathematical objects might carry useful inductive bias when classical symmetry groups are not enough.",
        "why_it_matters": "It keeps the course from ending in a closed textbook. The field is explicitly left open-ended.",
        "core_idea": "The right organizing structure for a task may be partial, local, combinatorial, or otherwise richer than a clean global group action.",
        "lenses": ["generalization", "structure", "future-directions"],
        "strongest_sessions": [11],
        "subtheme_refs": [THEMES[3]["subthemes"][2]["name"]],
        "broader_patterns": [
            "Mathematical elegance is useful, but only if it survives contact with messy domains.",
            "The frontier often advances by relaxing assumptions that used to define the field.",
        ],
        "applied_uses": [
            "Motivating research into sheaves, higher-order structure, and nonstandard relational systems.",
            "Recognizing when forcing a problem into a group template is too restrictive.",
        ],
        "analytical_frames": [
            {"title": "Field Pressure", "text": "Real domains often violate the assumptions of clean global symmetry."},
            {"title": "Research Response", "text": "Look for wider structural languages that still yield learnable operators."},
        ],
    },
    {
        "slug": "physics-based-gnns",
        "name": "Physics-based GNNs",
        "theme_id": THEMES[4]["id"],
        "theme_name": THEMES[4]["name"],
        "summary": "Physics-based graph models use graph structure and symmetry constraints to learn dynamics and interactions in scientific systems.",
        "why_it_matters": "This seminar shows how the course blueprint cashes out in scientific machine learning rather than staying at the level of abstract operator theory.",
        "core_idea": "The graph is not just a convenient data structure. It becomes a scaffold for encoding particles, interactions, conservation structure, and physical bias.",
        "lenses": ["physics", "gnn", "scientific-ml"],
        "strongest_sessions": [13],
        "subtheme_refs": [THEMES[4]["subthemes"][1]["name"]],
        "broader_patterns": [
            "Scientific domains reward architectures that respect known structure.",
            "Geometric bias often improves extrapolation where naive black-box learning fails.",
        ],
        "applied_uses": [
            "Molecular simulation, n-body systems, and learned physical dynamics.",
            "Prediction problems where invariances and relational interactions are known ahead of time.",
        ],
        "analytical_frames": [
            {"title": "Scientific Prior", "text": "Encode physical interaction structure directly in the computational graph."},
            {"title": "Payoff", "text": "Better faithfulness, sample efficiency, and extrapolation under structural constraints."},
        ],
    },
    {
        "slug": "subgraph-gnns",
        "name": "Subgraph GNNs",
        "theme_id": THEMES[4]["id"],
        "theme_name": THEMES[4]["name"],
        "summary": "Subgraph methods try to increase graph expressivity by letting the model reason on richer local structures than plain node neighborhoods alone.",
        "why_it_matters": "This seminar makes the limitations of vanilla message passing concrete and shows one route toward stronger graph representations.",
        "core_idea": "If standard neighborhood aggregation cannot distinguish certain structures, explicitly constructed subgraphs can carry the missing information.",
        "lenses": ["expressivity", "subgraphs", "graph-learning"],
        "strongest_sessions": [14],
        "subtheme_refs": [THEMES[4]["subthemes"][1]["name"]],
        "broader_patterns": [
            "Graph research often advances by finding exactly what message passing cannot see.",
            "Expressivity improvements usually come with computational tradeoffs.",
        ],
        "applied_uses": [
            "Tasks that need richer motif or pattern detection than ordinary local aggregation provides.",
            "Benchmark settings where Weisfeiler-Lehman-like limitations matter.",
        ],
        "analytical_frames": [
            {"title": "Limitation", "text": "Plain message passing can collapse distinct structures into the same representation."},
            {"title": "Workaround", "text": "Augment the computational unit from neighborhoods to structured subgraphs."},
        ],
    },
    {
        "slug": "neural-sheaf-diffusion",
        "name": "Neural sheaf diffusion",
        "theme_id": THEMES[4]["id"],
        "theme_name": THEMES[4]["name"],
        "summary": "Neural sheaf diffusion imports a richer topological and local-consistency language into graph learning.",
        "why_it_matters": "It is one of the clearest examples of the field moving beyond conventional graph and group language without abandoning structure.",
        "core_idea": "Instead of only diffusing scalar information on a graph, sheaf methods allow locally attached feature spaces and consistency maps between them.",
        "lenses": ["sheaves", "diffusion", "topology"],
        "strongest_sessions": [16],
        "subtheme_refs": [THEMES[4]["subthemes"][1]["name"], THEMES[3]["subthemes"][2]["name"]],
        "broader_patterns": [
            "The field is widening toward more expressive local-to-global consistency frameworks.",
            "Advanced geometry often appears first as a way to repair representation bottlenecks.",
        ],
        "applied_uses": [
            "Graph problems where scalar diffusion loses important structured information.",
            "Research on richer topological or fibered data domains.",
        ],
        "analytical_frames": [
            {"title": "Classical Diffusion", "text": "Information moves on a graph with one shared feature space."},
            {"title": "Sheaf View", "text": "Each local region can carry its own feature structure with maps enforcing compatibility."},
        ],
    },
    {
        "slug": "alphafold-and-geometric-bias",
        "name": "AlphaFold and geometric bias",
        "theme_id": THEMES[4]["id"],
        "theme_name": THEMES[4]["name"],
        "summary": "AlphaFold stands in the course as a flagship example of what happens when geometry and relational bias are aligned with a scientifically important problem.",
        "why_it_matters": "It is the most legible proof to a broad audience that geometric inductive bias is not niche theory. It changes what models can do in the world.",
        "core_idea": "Protein structure prediction rewards models that reason over relational structure, constraints, and geometry rather than over tokens alone.",
        "lenses": ["biology", "protein-structure", "applications"],
        "strongest_sessions": [17],
        "subtheme_refs": [THEMES[4]["subthemes"][2]["name"]],
        "broader_patterns": [
            "High-impact breakthroughs often come from combining scale with the right structured bias.",
            "Geometry matters most when the target object is itself geometric.",
        ],
        "applied_uses": [
            "Explaining why structure-aware architectures matter in biology and chemistry.",
            "Showing students a concrete success case for the broader course philosophy.",
        ],
        "analytical_frames": [
            {"title": "Problem Structure", "text": "Proteins are relational and geometric objects, not flat sequences alone."},
            {"title": "Lesson", "text": "When the inductive bias matches the domain, capability jumps can be dramatic."},
        ],
    },
]


SESSION_ASSIGNMENTS: dict[int, tuple[str, str]] = {
    1: (THEMES[0]["id"], THEMES[0]["subthemes"][2]["name"]),
    2: (THEMES[0]["id"], THEMES[0]["subthemes"][0]["name"]),
    3: (THEMES[1]["id"], THEMES[1]["subthemes"][0]["name"]),
    4: (THEMES[0]["id"], THEMES[0]["subthemes"][1]["name"]),
    5: (THEMES[2]["id"], THEMES[2]["subthemes"][0]["name"]),
    6: (THEMES[2]["id"], THEMES[2]["subthemes"][1]["name"]),
    7: (THEMES[2]["id"], THEMES[2]["subthemes"][2]["name"]),
    8: (THEMES[1]["id"], THEMES[1]["subthemes"][1]["name"]),
    9: (THEMES[3]["id"], THEMES[3]["subthemes"][0]["name"]),
    10: (THEMES[3]["id"], THEMES[3]["subthemes"][1]["name"]),
    11: (THEMES[3]["id"], THEMES[3]["subthemes"][2]["name"]),
    12: (THEMES[4]["id"], THEMES[4]["subthemes"][0]["name"]),
    13: (THEMES[4]["id"], THEMES[4]["subthemes"][1]["name"]),
    14: (THEMES[4]["id"], THEMES[4]["subthemes"][1]["name"]),
    15: (THEMES[4]["id"], THEMES[4]["subthemes"][2]["name"]),
    16: (THEMES[4]["id"], THEMES[4]["subthemes"][1]["name"]),
    17: (THEMES[4]["id"], THEMES[4]["subthemes"][2]["name"]),
}


SESSION_BRIEFS: dict[int, str] = {
    1: "Bronstein opens the course by defining geometric deep learning as a unifying program for structured domains, framing the rest of the lectures as answers to one architectural question rather than as isolated model families.",
    2: "Bruna explains why high-dimensional learning needs bias, using the failure modes of generic function fitting to motivate the need for geometric and structural constraints.",
    3: "Cohen introduces geometric priors and the invariance/equivariance vocabulary that later lectures keep reusing whenever they ask what a model should preserve under transformation.",
    4: "Bruna deepens the priors discussion by making architectural consequences explicit: good priors reduce sample complexity precisely because they rule out the wrong hypothesis classes.",
    5: "Veličković starts the discrete-domain block by contrasting sets and graphs, showing how the geometry of the domain determines whether aggregation or relational propagation is the key operator.",
    6: "The second graphs lecture focuses on graph expressivity and the limits of standard message passing, setting up several of the frontier seminars that come later.",
    7: "Bruna re-reads CNNs through the course blueprint and treats grids as a special structured domain where translation symmetry and convolution line up unusually cleanly.",
    8: "Cohen moves from intuitive symmetry talk to groups and homogeneous spaces, giving the course its most explicit algebraic account of equivariant operator design.",
    9: "Bronstein's manifolds lecture shifts the course into intrinsically curved domains and emphasizes that useful geometry is often about the space itself, not only about its Euclidean embedding.",
    10: "Cohen's gauges lecture handles the harder case where one global coordinate frame is unavailable, so the model has to stay consistent across local frames instead.",
    11: "Veličković uses the beyond-groups lecture to widen the conceptual aperture of the field and ask what other mathematical objects can carry learnable structural bias.",
    12: "Bronstein closes the main lecture sequence by surveying applications and trends, turning the course from a mathematical tour into a research agenda with visible open edges.",
    13: "The physics-based GNN seminar shows the blueprint operating in scientific machine learning, where graph structure and symmetry are tied directly to physical interactions and dynamics.",
    14: "Frasca's subgraph seminar tackles graph expressivity head-on, arguing that richer computational units are needed when standard neighborhood aggregation cannot see the right structure.",
    15: "Williamson's equivariance seminar broadens the symmetry discussion and gives the audience another angle on why transformation-aware modeling matters beyond the canonical lecture examples.",
    16: "Bodnar's neural sheaf diffusion seminar pushes graph learning into a richer local-to-global consistency framework, illustrating what beyond-groups research looks like in practice.",
    17: "The AlphaFold seminar gives the course its clearest flagship application: geometric bias is shown not as elegant theory but as a practical ingredient in a world-changing system.",
}


SESSION_DISCUSSIONS: dict[int, str] = {
    1: "This opening lecture matters because it refuses to define the field by a single architecture. Bronstein instead frames geometric deep learning as a translation problem between domain structure and model structure, which gives the entire course its coherence.",
    2: "The high-dimensional lecture is where the course justifies its own existence. Bruna makes it clear that geometry is not an optional sophistication layer; it is the answer to why unrestricted learning becomes statistically fragile.",
    3: "Geometric Priors I gives the course its control vocabulary. Once invariance and equivariance are in place, later lectures can ask much sharper questions about what exactly a model should do under transformation.",
    4: "The second priors lecture sharpens the tradeoff between expressivity and bias. The discussion is useful because it stops structure from sounding like dogma and instead presents it as disciplined restriction in service of generalization.",
    5: "The graphs-and-sets lecture marks the transition from motivation into operator design. It shows that the field becomes concrete only when the geometry of the domain dictates what aggregation is allowed.",
    6: "Graphs & Sets II is a pressure test for plain message passing. The discussion is valuable because several later frontier methods make sense only after you see where ordinary graph models fail to distinguish structure.",
    7: "The grids lecture repositions convolution inside a broader conceptual map. That is important pedagogically because it stops CNN intuition from dominating domains where grid assumptions do not hold.",
    8: "The groups lecture is the course's most explicit statement that symmetry can be operationalized mathematically. It connects the intuitive desire for structured behavior to a formal recipe for operator construction.",
    9: "The manifolds lecture matters because it breaks the habit of assuming the ambient Euclidean space tells the whole story. Bronstein keeps returning attention to intrinsic geometry and local structure.",
    10: "Gauge equivariance is the point where the course becomes genuinely local. The key discussion is not only about symmetry, but about compatibility between overlapping local descriptions when no single frame is privileged.",
    11: "Beyond Groups keeps the course intellectually open. Instead of declaring the job finished with groups, the lecture asks what other structures deserve to play the same organizing role for harder domains.",
    12: "Applications & Trends is less a recap than a positioning statement. It shows where the blueprint has worked, where the theory is still incomplete, and why the field remains an active research frontier.",
    13: "The physics-based GNN seminar is the course's scientific credibility check. It demonstrates that structure-aware graph modeling is not just elegant abstraction, but a usable tool for systems governed by known interaction laws.",
    14: "Subgraph GNNs are discussed as an expressivity repair strategy. The seminar matters because it makes the limitations of vanilla message passing concrete rather than merely theoretical.",
    15: "The equivariance seminar broadens the audience's intuition for when transformation-aware learning is worth the complexity. It reinforces symmetry as a durable design idea rather than a one-lecture curiosity.",
    16: "Neural sheaf diffusion pushes the frontier into richer local-to-global consistency frameworks. It is a good example of how the field expands when classical graph primitives no longer feel expressive enough.",
    17: "The AlphaFold seminar functions as the capstone application. It shows why the course is ultimately about matching inductive bias to domain reality well enough to unlock otherwise unreachable performance.",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def esc(value: Any) -> str:
    return html.escape(str(value))


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def first_sentence(text: str, limit: int = 240) -> str:
    cleaned = compact(text)
    if not cleaned:
        return "Transcript text is not available for this session."
    sentence = cleaned[:limit]
    for index, char in enumerate(cleaned[:limit], 1):
        if index >= 80 and char in ".!?":
            sentence = cleaned[:index]
            break
    return sentence[:limit].rstrip()


def format_duration(seconds: int | None) -> str:
    if not seconds:
        return "-"
    minutes, remainder = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m {remainder}s"


def render_inline(text: str) -> str:
    text = esc(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def load_markdown_sections(path: Path) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = ""
    current_lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        elif line.startswith("# "):
            continue
        else:
            current_lines.append(line)
    if current_title:
        sections.append((current_title, current_lines))
    return sections


def render_markdown_lines(lines: list[str]) -> str:
    parts: list[str] = []
    in_list = False
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            parts.append(f"<p>{render_inline(' '.join(item.strip() for item in para if item.strip()))}</p>")
            para = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            parts.append("</ul>")
            in_list = False

    for raw in lines:
        line = raw.rstrip()
        if not line:
            flush_para()
            close_list()
            continue
        if line.startswith("- "):
            flush_para()
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{render_inline(line[2:].strip())}</li>")
            continue
        close_list()
        para.append(line)

    flush_para()
    close_list()
    return "".join(parts)


def session_briefs_markdown(title: str, sessions: list[dict[str, Any]]) -> str:
    lines = ["# Session Briefs", "", f"Plain-English map for `{title}`.", ""]
    for item in sessions:
        lines.extend(
            [
                f"## {item['session_label']}",
                "",
                item["brief"],
                "",
            ]
        )
    return "\n".join(lines)


def course_thesis_markdown(summary: dict[str, Any]) -> str:
    return f"""# Course Thesis

AMMI Geometric Deep Learning Course - Second Edition (2022) teaches geometric deep learning as a design discipline rather than a bag of architectures. The course begins with a statistical problem: in high dimensions, generic learning is too unconstrained to generalize well. It then offers a structural answer: inject the right geometric prior, define what should be invariant or equivariant, and choose operators that match the true domain.

That logic lets the course move cleanly across very different spaces. Sets, graphs, grids, groups, homogeneous spaces, manifolds, and gauges are not taught as disconnected technical chapters. They are treated as different answers to the same question: what geometry does this domain have, and what computation should that geometry permit?

The later seminars matter because they stop the course from feeling closed or purely mathematical. Physics-based GNNs, subgraph methods, neural sheaf diffusion, and AlphaFold all show the same blueprint under real pressure. The point of geometric deep learning is not elegance alone. It is that the right structural bias can unlock data efficiency, stronger generalization, and qualitatively better scientific or engineering performance.

This synthesis is grounded in {summary['videos']} transcript-backed sessions and {summary['total_words']:,} transcript words.

## Argument Spine

1. High-dimensional learning needs inductive bias.
2. Geometric priors encode that bias by respecting transformations and relations in the domain.
3. Symmetry, invariance, and equivariance are the central control language for structured learning.
4. Different domains require different operators: sets, graphs, and grids are not interchangeable.
5. Manifolds, gauges, and beyond-group ideas generalize the field beyond flat global coordinates.
6. The frontier is judged by working applications in science and complex structured prediction, not by abstraction alone.
"""


def build_analysis(course_root: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = load_json(course_root / "raw-material/youtube/course-manifest.json")
    summary = load_json(course_root / "raw-material/youtube/summary.json")
    transcript_index = load_json(course_root / "raw-material/youtube/transcript-index.json")

    theme_lookup = {theme["id"]: theme for theme in THEMES}
    sessions: list[dict[str, Any]] = []
    record_lookup = {int(record["index"]): record for record in transcript_index}
    for index in sorted(record_lookup):
        record = record_lookup[index]
        theme_id, subtheme_name = SESSION_ASSIGNMENTS[index]
        theme = theme_lookup[theme_id]
        text_path = course_root / record["clean_txt"]
        transcript_glimpse = first_sentence(text_path.read_text(encoding="utf-8", errors="ignore"))
        short_title = record["title"].split(" - ", 1)[1] if " - " in record["title"] else record["title"]
        sessions.append(
            {
                **record,
                "short_title": short_title,
                "session_label": f"Session {index}: {short_title}",
                "theme_id": theme_id,
                "theme_name": theme["name"],
                "subtheme_name": subtheme_name,
                "summary": transcript_glimpse,
                "brief": SESSION_BRIEFS[index],
                "discussion": SESSION_DISCUSSIONS[index],
            }
        )

    evidence_map = {
        "concepts": {
            concept["slug"]: [
                {
                    "session": session_index,
                    "title": next(item["session_label"] for item in sessions if item["index"] == session_index),
                    "url": next(item["url"] for item in sessions if item["index"] == session_index),
                    "word_count": next(item["word_count"] for item in sessions if item["index"] == session_index),
                }
                for session_index in concept["strongest_sessions"]
            ]
            for concept in CONCEPTS
        }
    }

    concepts = []
    for concept in CONCEPTS:
        concepts.append(
            {
                **concept,
                "site_page": f"site/concepts/{concept['slug']}.html",
            }
        )

    analysis_dir = course_root / "analysis"
    write_json(
        analysis_dir / "themes-and-subthemes.json",
        {
            "course": {
                "slug": manifest["slug"],
                "title": manifest["title"],
                "instructor": manifest["instructor"],
                "transcript_count": summary["available_transcripts"],
                "total_words": summary["total_words"],
                "coverage_note": "Theme map is built from the full 17-session transcript corpus captured on August 9, 2026 after excluding the unrelated trailing playlist item.",
            },
            "themes": THEMES,
        },
    )
    write_json(analysis_dir / "concepts.json", concepts)
    write_json(analysis_dir / "sessions.json", sessions)
    write_json(
        analysis_dir / "discussions.json",
        [
            {
                "session": item["index"],
                "title": item["session_label"],
                "theme": item["theme_name"],
                "subtheme": item["subtheme_name"],
                "discussion": item["discussion"],
                "url": item["url"],
            }
            for item in sessions
        ],
    )
    write_json(analysis_dir / "evidence-map.json", evidence_map)
    write_text(analysis_dir / "course-thesis.md", course_thesis_markdown(summary))
    write_text(analysis_dir / "session-briefs.md", session_briefs_markdown(manifest["title"], sessions))
    write_text(
        analysis_dir / "README.md",
        "\n".join(
            [
                "# Analysis Outputs",
                "",
                "This course folder includes:",
                "",
                "- `session-inventory.md`",
                "- `session-briefs.md`",
                "- `course-thesis.md`",
                "- `themes-and-subthemes.json`",
                "- `concepts.json`",
                "- `sessions.json`",
                "- `discussions.json`",
                "- `evidence-map.json`",
            ]
        ),
    )
    return manifest, summary, sessions, concepts


def top_nav(current: str, in_concepts: bool = False) -> str:
    if in_concepts:
        links = [
            ("../index.html", "Overview"),
            ("../course-thesis.html", "Thesis"),
            ("../themes.html", "Themes"),
            ("../subthemes.html", "Subthemes"),
            ("../discussions.html", "Discussions"),
            ("../sessions.html", "Sessions"),
            ("index.html", "Concepts"),
        ]
    else:
        links = [
            ("index.html", "Overview"),
            ("course-thesis.html", "Thesis"),
            ("themes.html", "Themes"),
            ("subthemes.html", "Subthemes"),
            ("discussions.html", "Discussions"),
            ("sessions.html", "Sessions"),
            ("concepts/index.html", "Concepts"),
        ]
    return "".join(
        f'<a class="{"active" if label == current else ""}" href="{href}">{label}</a>'
        for href, label in links
    )


def page_shell(title: str, body: str, current: str, *, in_concepts: bool = False) -> str:
    back_href = "../../../site/index.html" if in_concepts else "../../site/index.html"
    css_href = "../assets/styles.css" if in_concepts else "assets/styles.css"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
  <main class="page">
    <a class="back" href="{back_href}">Back to workspace index</a>
    <header class="hero">
      <div>
        <p class="eyebrow">Course atlas</p>
        <h1>{esc(title)}</h1>
      </div>
      <nav>{top_nav(current, in_concepts=in_concepts)}</nav>
    </header>
    {body}
  </main>
</body>
</html>
"""


def write_styles(site_dir: Path) -> None:
    css = """
:root {
  color-scheme: light;
  --bg: linear-gradient(135deg, #f6f1e8 0%, #edf3f5 48%, #f8ece1 100%);
  --panel: rgba(255,255,255,.88);
  --panel-alt: rgba(247,244,237,.92);
  --ink: #171b1d;
  --muted: #5e666b;
  --line: #d7ddd8;
  --accent: #0f6b73;
  --accent-soft: #dceff1;
  --accent-2: #91501e;
  --shadow: 0 18px 42px rgba(20, 24, 27, .07);
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); line-height: 1.6; }
a { color: inherit; }
.page { width: min(1180px, calc(100% - 28px)); margin: 0 auto; padding: 18px 0 64px; }
.back { display: inline-flex; align-items: center; min-height: 36px; padding: 0 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel); text-decoration: none; color: var(--muted); margin-bottom: 18px; }
.hero, .card, .essay, .strip { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; box-shadow: var(--shadow); }
.hero { padding: 26px; display: grid; grid-template-columns: 1.25fr .95fr; gap: 20px; }
.eyebrow { margin: 0 0 10px; display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
h1, h2, h3 { margin: 0; font-weight: 700; }
h1 { font-size: clamp(2.2rem, 4vw, 3.5rem); line-height: 1.04; }
h2 { font-size: 1.4rem; margin-bottom: 10px; }
h3 { font-size: 1.02rem; margin-bottom: 8px; }
p { margin: 0; color: var(--muted); }
nav { display: flex; flex-wrap: wrap; align-content: flex-start; justify-content: flex-end; gap: 8px; }
nav a, .button { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--panel-alt); text-decoration: none; color: var(--muted); font-weight: 700; }
nav a.active, nav a:hover, .button:hover { background: var(--accent); border-color: var(--accent); color: #fff; }
main section + section { margin-top: 20px; }
.grid-2, .grid-3, .grid-4 { display: grid; gap: 16px; }
.grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.card, .essay, .strip { padding: 18px; }
.meta { color: var(--accent-2); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.lead { font-size: 1.05rem; color: var(--ink); max-width: 72ch; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.chip { display: inline-flex; align-items: center; min-height: 30px; padding: 0 10px; border-radius: 999px; border: 1px solid var(--line); background: var(--panel-alt); color: var(--muted); font-size: .84rem; }
.stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 16px; }
.stat { padding: 14px; border-radius: 8px; border: 1px solid var(--line); background: var(--panel-alt); }
.stat .label { color: var(--muted); font-size: .76rem; font-weight: 700; text-transform: uppercase; }
.stat .value { margin-top: 6px; font-size: 1.28rem; font-weight: 700; color: var(--ink); }
ul { margin: 10px 0 0; padding-left: 18px; color: var(--muted); }
li + li { margin-top: 8px; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .95em; }
@media (max-width: 980px) {
  .hero, .grid-2, .grid-3, .grid-4, .stats { grid-template-columns: 1fr; }
  nav { justify-content: flex-start; }
}
"""
    write_text(site_dir / "assets/styles.css", css)


def build_site(course_root: Path, manifest: dict[str, Any], summary: dict[str, Any], sessions: list[dict[str, Any]], concepts: list[dict[str, Any]]) -> None:
    site_dir = course_root / "site"
    concepts_dir = site_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    write_styles(site_dir)

    overview = f"""
    <section class="essay">
      <h2>Overview</h2>
      <p class="lead">{esc(manifest['title'])} turns geometric deep learning into a single design language for structured machine learning. The course starts with the statistical need for inductive bias, moves through symmetry and domain-specific operators, then ends by testing the framework against real research frontiers in graphs, manifolds, sheaves, physics, and protein structure.</p>
      <div class="chips">
        <span class="chip">Instructor set: {esc(manifest['instructor'])}</span>
        <span class="chip">{summary['videos']} sessions</span>
        <span class="chip">{summary['available_transcripts']} transcripts captured</span>
        <span class="chip">{summary['total_words']:,} transcript words</span>
      </div>
      <div class="stats">
        <div class="stat"><div class="label">Themes</div><div class="value">{len(THEMES)}</div></div>
        <div class="stat"><div class="label">Concepts</div><div class="value">{len(concepts)}</div></div>
        <div class="stat"><div class="label">Lecture Block</div><div class="value">12</div></div>
        <div class="stat"><div class="label">Seminars</div><div class="value">5</div></div>
      </div>
      <div class="chips">
        <a class="button" href="course-thesis.html">Read the thesis</a>
        <a class="button" href="themes.html">Browse themes</a>
        <a class="button" href="concepts/index.html">Browse concepts</a>
        <a class="button" href="sessions.html">Browse sessions</a>
      </div>
    </section>
    <section class="grid-3">
      {''.join(f'<article class="card"><div class="meta">{len(theme["subthemes"])} subthemes</div><h3>{esc(theme["name"])}</h3><p>{esc(theme["summary"])}</p></article>' for theme in THEMES)}
    </section>
    """

    thesis_sections = load_markdown_sections(course_root / "analysis/course-thesis.md")
    thesis_body = "<section class=\"essay\">" + "".join(
        f"<h2>{esc(title)}</h2>{render_markdown_lines(lines)}" for title, lines in thesis_sections
    ) + "</section>"

    theme_body = "<section class=\"grid-2\">" + "".join(
        f"""<article class="card">
          <div class="meta">Evidence sessions: {", ".join(str(x) for x in theme["evidence_sessions"])}</div>
          <h3>{esc(theme["name"])}</h3>
          <p>{esc(theme["summary"])}</p>
          <div class="chips">{''.join(f'<span class="chip">{esc(lens)}</span>' for lens in theme.get("lenses", []))}</div>
          <ul>{''.join(f'<li><strong>{esc(sub["name"])}</strong>: {esc(sub["summary"])}</li>' for sub in theme["subthemes"])}</ul>
        </article>"""
        for theme in THEMES
    ) + "</section>"

    subtheme_rows = []
    for theme in THEMES:
        for subtheme in theme["subthemes"]:
            subtheme_rows.append(
                f"""<article class="card">
                  <div class="meta">{esc(theme["name"])}</div>
                  <h3>{esc(subtheme["name"])}</h3>
                  <p>{esc(subtheme["summary"])}</p>
                  <div class="chips"><span class="chip">Sessions {", ".join(str(x) for x in subtheme["evidence_sessions"])}</span></div>
                </article>"""
            )
    subtheme_body = '<section class="grid-2">' + "".join(subtheme_rows) + "</section>"

    discussion_body = '<section class="grid-2">' + "".join(
        f"""<article class="card">
          <div class="meta">{esc(item["theme_name"])} · {esc(item["subtheme_name"])}</div>
          <h3>{esc(item["session_label"])}</h3>
          <p>{esc(item["discussion"])}</p>
          <div class="chips"><a class="button" href="{esc(item["url"])}">Source video</a></div>
        </article>"""
        for item in sessions
    ) + "</section>"

    session_body = '<section class="grid-2">' + "".join(
        f"""<article class="card">
          <div class="meta">{format_duration(item.get("duration"))} · {item.get("word_count", 0):,} words</div>
          <h3>{esc(item["session_label"])}</h3>
          <p><strong>Theme:</strong> {esc(item["theme_name"])}</p>
          <p><strong>Subtheme:</strong> {esc(item["subtheme_name"])}</p>
          <p>{esc(item["brief"])}</p>
          <div class="chips"><span class="chip">{esc(item["summary"])}</span></div>
          <div class="chips"><a class="button" href="{esc(item["url"])}">Watch on YouTube</a></div>
        </article>"""
        for item in sessions
    ) + "</section>"

    concept_index_body = """
    <section class="essay">
      <h2>Concept Atlas</h2>
      <p class="lead">These concept pages turn the course into a reusable idea system. The emphasis is on transferable design logic: high-dimensional bias, symmetry, domain geometry, operator choice, and the research frontier where those choices become consequential.</p>
    </section>
    <section class="grid-3">
    """ + "".join(
        f"""<article class="card">
          <div class="meta">Sessions {", ".join(str(x) for x in concept["strongest_sessions"])}</div>
          <h3><a href="{esc(concept['slug'])}.html">{esc(concept['name'])}</a></h3>
          <p>{esc(concept['summary'])}</p>
          <div class="chips">{''.join(f'<span class="chip">{esc(lens)}</span>' for lens in concept.get("lenses", [])[:4])}</div>
        </article>"""
        for concept in concepts
    ) + "</section>"

    write_text(site_dir / "index.html", page_shell(manifest["title"], overview, "Overview"))
    write_text(site_dir / "course-thesis.html", page_shell(f"{manifest['title']} - Thesis", thesis_body, "Thesis"))
    write_text(site_dir / "themes.html", page_shell(f"{manifest['title']} - Themes", theme_body, "Themes"))
    write_text(site_dir / "subthemes.html", page_shell(f"{manifest['title']} - Subthemes", subtheme_body, "Subthemes"))
    write_text(site_dir / "discussions.html", page_shell(f"{manifest['title']} - Discussions", discussion_body, "Discussions"))
    write_text(site_dir / "sessions.html", page_shell(f"{manifest['title']} - Sessions", session_body, "Sessions"))
    write_text(concepts_dir / "index.html", page_shell(f"{manifest['title']} - Concepts", concept_index_body, "Concepts", in_concepts=True))

    evidence_map = load_json(course_root / "analysis/evidence-map.json")["concepts"]
    for concept in concepts:
        evidence = evidence_map.get(concept["slug"], [])
        body = f"""
        <section class="essay">
          <div class="meta">Concept Page</div>
          <h2>{esc(concept['name'])}</h2>
          <p>{esc(concept['summary'])}</p>
          <div class="chips">
            {''.join(f'<span class="chip">{esc(item)}</span>' for item in concept.get('lenses', []))}
          </div>
        </section>
        <section class="grid-2">
          <article class="card">
            <h3>Core Idea</h3>
            <p>{esc(concept['core_idea'])}</p>
          </article>
          <article class="card">
            <h3>Why It Matters</h3>
            <p>{esc(concept['why_it_matters'])}</p>
          </article>
        </section>
        <section class="grid-2">
          {''.join(f'<article class="card"><h3>{esc(frame["title"])}</h3><p>{esc(frame["text"])}</p></article>' for frame in concept.get("analytical_frames", []))}
        </section>
        <section class="grid-2">
          <article class="card">
            <div class="meta">Linked Subthemes</div>
            <ul>{''.join(f'<li>{esc(item)}</li>' for item in concept.get('subtheme_refs', []))}</ul>
          </article>
          <article class="card">
            <div class="meta">Broader Patterns</div>
            <ul>{''.join(f'<li>{esc(item)}</li>' for item in concept.get('broader_patterns', []))}</ul>
          </article>
        </section>
        <section class="grid-2">
          <article class="card">
            <div class="meta">Applied Uses</div>
            <ul>{''.join(f'<li>{esc(item)}</li>' for item in concept.get('applied_uses', []))}</ul>
          </article>
          <article class="card">
            <div class="meta">Strongest Sessions</div>
            <ul>{''.join(f'<li>{esc(item["title"])} · {item["word_count"]:,} transcript words</li>' for item in evidence)}</ul>
          </article>
        </section>
        """
        write_text(concepts_dir / f"{concept['slug']}.html", page_shell(concept["name"], body, "Concepts", in_concepts=True))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a rich course site for the AMMI Geometric Deep Learning Course - Second Edition (2022).")
    parser.add_argument(
        "--course-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "ammi-geometric-deep-learning-2022",
        help="Path to the course workspace root.",
    )
    args = parser.parse_args()
    course_root = args.course_root.resolve()
    manifest, summary, sessions, concepts = build_analysis(course_root)
    build_site(course_root, manifest, summary, sessions, concepts)
    print(f"Built {manifest['slug']} with {len(THEMES)} themes, {len(concepts)} concepts, and {len(sessions)} session pages.")


if __name__ == "__main__":
    main()
