# MT6893 LineageOS 24 compatibility patches

Use the pinned `lineage-24.0` branch of [seriaTvT/local_manifests](https://github.com/seriaTvT/local_manifests/tree/lineage-24.0).

After sync, from the Android source root:

```sh
bash patches/apply-patches.sh
bash patches/apply-patches.sh --check
```

`series.json` pins the upstream base, original tested commit, expected final Git
tree, and SHA256 of every patch. The script preflights all projects, refuses wrong
bases or tracked changes, never resets an existing branch, and verifies the final
source trees. Repeated application is safe. New commit IDs may differ because of
committer metadata; final source trees must match exactly.

| Project | Compatibility change |
|---|---|
| build/soong | Opt-in SOONG_GOMEMLIMIT for large analysis runs |
| hardware/interfaces | Frozen HIDL packages required by FCM 6 |
| hardware/mediatek | Pixel USB/statistics namespace imports |
| frameworks/base | Legacy process reclaim, real JNI errors, freezer capability gate |
| frameworks/av | Revert MTK queue-empty-work behavior |
| system/core | Rate-limit old MediaTek RefBase destruction backtraces |
| system/zygote | Skip capability bounds absent from the actual kernel |
| .repo/repo | Read-only Git-config cache cleanup compatibility (Repo v2.71) |

The ARM64 sync-core change is published directly on `seriaTvT/kernel_mt6893`
`lineage-24.0`; it is not applied twice here. Device/vendor integration belongs
in the existing seriaTvT device/vendor repositories. No new platform forks are
required by this series. No private signing key is included.
