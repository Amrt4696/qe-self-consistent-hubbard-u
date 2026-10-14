# Example: two inequivalent Fe sites

This is the case that actually trips people up: your structure has more
than one Fe atom, and hp.x finds they aren't equivalent - different local
occupations even though they're the same element.

## How I handle it

Run iteration 1 normally with `make_usc_inputs.py` treating all Fe atoms
as one species, same as the single-site example. Look at the iteration-1
`Hubbard_parameters.dat` - if you see two different U values both
labeled `Fe`, that's your signal.

For iteration 2, `make_usc_inputs.py` doesn't split species
automatically (it builds the structure block straight from whatever
species the CONTCAR lists), so this part is manual. Starting from the
iteration-1 structure block:

1. In `ATOMIC_SPECIES`, add a second entry for the same element pointing
   at the same pseudopotential, and bump `ntyp` in `&SYSTEM` by one to
   match (e.g. `ntyp=5` in iteration 1 becomes `ntyp=6` once the single
   `Fe` type splits into `Fe1`/`Fe2`):

   ```
   ATOMIC_SPECIES
   Fe1  55.845  Fe.UPF
   Fe2  55.845  Fe.UPF
   ```

2. In `ATOMIC_POSITIONS`, relabel the two Fe atoms `Fe1` and `Fe2`. Which
   physical atom you call `Fe1` vs `Fe2` is arbitrary - but once you pick,
   that assignment has to stay attached to the same atom (the same
   `site n.` in `Hubbard_parameters.dat`) for the rest of the run, since
   you're about to feed each site's own `Uout` back in as that same
   site's `Uin`. `check_convergence.py` tracks sites by their site
   number for exactly this reason - see its docstring if you want the
   details.

3. If you're using `starting_magnetization` (as in the single-site
   example), give it one entry per new species - `Fe1` and `Fe2` both
   need their own line now that they're no longer a single `Fe` type:

   ```
   starting_magnetization(1)=0.8   ! Fe1
   starting_magnetization(2)=0.8   ! Fe2
   ```

4. Replace the single `HUBBARD atomic` line with one per site, using
   each site's own `Uout` from iteration 1 as its `Uin` for iteration 2:

   ```
   HUBBARD atomic
   U Fe1-3d <Uout_1 from iteration 1>
   U Fe2-3d <Uout_2 from iteration 1>
   ```

Everything else about the iteration - the smeared SCF, the fixed SCF, hp.x
- runs exactly the same way as the single-site case.

`check_convergence.py` already handles this: point it at Hubbard files
where the sites are labeled `Fe1`/`Fe2` and it tracks each one's
convergence separately rather than conflating them.

## Result

*(worked example pending - same as the single-site case, I want to pull
the real Uout values from my actual `Hubbard_parameters.dat` files rather
than write down approximate numbers)*
