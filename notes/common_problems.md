# Problems I ran into

**hp.x can't find the SCF data it needs.** This is almost always a
`prefix`/`outdir` mismatch between the SCF step and the hp.x step. They
have to point at exactly the same `prefix.save` directory. Double-check
this before anything else if hp.x complains about missing files.

**U comes out looking wrong, with no obvious error.** Stale or
mismatched `.save` data from a previous run can sit in `outdir` and get
picked up silently. I now wipe and recreate the scratch directory at the
start of every iteration rather than reusing one - cheap insurance
against debugging a "wrong" U for an hour before realizing the real
cause.

**More than one U value shows up for what you thought was one species.**
This means hp.x found that the atoms aren't equivalent - usually because
they ended up with different occupations even though they're the same
element. The fix isn't to average them. Relabel them as separate atomic
types (e.g. `Fe1`, `Fe2`) pointing at the same pseudopotential, and carry
each one's own U forward separately in the next iteration. See the
`two_inequivalent_sites` example.

**Smeared SCF converges fine, but hp.x gives a weird result.** For
the insulating Fe-bearing systems I use this workflow on, I want hp.x
running on the fixed-occupation reference state, not the metallic
smeared one - make sure the fixed-occupation SCF (step 2 in
`workflow.md`) actually converged to the magnetic state you intended,
check the magnetization in its output, not just that it finished.

**`find_atpert`.** This flag tells hp.x to automatically find
Hubbard-perturbed atoms rather than you specifying them by hand. Worth
knowing it exists because its output is what tells you whether you've
got equivalent or inequivalent Hubbard sites in the first place.

**Running iteration 2 accidentally reuses iteration 1's scratch data.**
Related to the stale-`.save` point above - if your directory structure
or script has a path typo, you can end up re-running what is effectively
iteration 1 again and getting a suspiciously "converged" result on the
first try. If convergence looks too easy, check the scratch directory
actually changed between iterations.
