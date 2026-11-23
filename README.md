# PixelOS 17 MT6893 compatibility for tracking branches

Use with seriaTvT/local_manifests, branch pixelos-17-tracking. From the synced Android root:

```bash
bash patches/apply-patches.sh
bash patches/apply-patches.sh --check
```

The eleven groups include chopin/Redmi Note 10 Pro and ares products, device
Dolby module isolation, AresParts without the Lineage SDK, battery LED ownership,
legacy process reclaim/freezer handling, native Zygote capabilities, frozen HIDL,
MediaTek namespaces, Soong memory limiting and Repo read-only cache handling.
The kernel, ION policy and Codec2 Fence ABI fix are already in the tracked histories.
The obsolete Codec2 queue-empty revert is intentionally absent.

Each original patch has a public base, SHA256 and expected Git tree. The runner
reconstructs and verifies that tree, then uses Git's three-way merge to combine
the original patch with newer upstream revisions. It preflights every project
before changing checked-out files. Existing worktree changes, missing base
history, rewritten upstream history or merge conflicts stop application.
Git must support `merge-tree --write-tree --merge-base`; patched repositories
must include the recorded base history. Repeated application is supported.
`--check` verifies that merging the patches requires no additional changes.
Trees at the original bases match the tested snapshot; newer upstream versions
retain their own changes and require new build and device validation.
Original commit attribution is retained in the provenance files and patch headers.
Do not force past conflicts or run repo sync over uncommitted local work.

Runtime validation remains device-specific. A clean build requires the matching
manifest, all LFS assets and the builder's own signing keys. The fixed snapshot
and strict tree-checking runner remain available on the `pixelos-17` branch.
