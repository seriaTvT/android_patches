# PixelOS 17 MT6893 compatibility snapshot

Use with seriaTvT/local_manifests, branch pixelos-17. From the synced Android root:

```bash
bash patches/apply-patches.sh
bash patches/apply-patches.sh --check
```

The eleven groups include chopin/Redmi Note 10 Pro and ares products, device
Dolby module isolation, AresParts without the Lineage SDK, battery LED ownership,
legacy process reclaim/freezer handling, native Zygote capabilities, frozen HIDL,
MediaTek namespaces, Soong memory limiting and Repo read-only cache handling.
The kernel, ION policy and Codec2 Fence ABI fix are already pinned in the manifest.
The obsolete Codec2 queue-empty revert is intentionally absent.

Each patch is tied to a public base, SHA256 and expected final Git tree. The
runner preflights all projects before applying any changes and is safe to repeat.
Existing modifications or unexpected bases stop application. Generated commits
may have different IDs from the original development commits; final trees match.
Original commit attribution is retained in the provenance files and patch headers.
Do not force patches onto newer source revisions or run repo sync over local work.

Runtime validation remains device-specific. A clean build requires the matching
manifest, all LFS assets and the builder's own signing keys.
