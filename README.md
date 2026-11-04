# android_patches — local patches for the chopin/ares MT6893 LOS 24 tree

Small, self-contained changes to **upstream-managed** AOSP/LineageOS projects
that don't justify forking the whole repo. Wired into the tree via
`.repo/local_manifests/mt6893.xml` (cloned to `patches/`).

## Usage

After every `repo sync`, before `lunch`/`m`:

```bash
./patches/apply-patches.sh
```

Idempotent — already-applied patches are skipped; a patch that no longer
applies stops the script so you can rebase it (a loud failure, by design).

## Contents

| Project | Patch | Why |
|---|---|---|
| `system/core` | rate-limit RefBase explicit-destruction backtrace | MediaTek `libgpu_aux` trips `RefBase`'s per-object CallStack capture on every `eglDestroyImageKHR`, pegging the GPU thread → media-playback stutter. See PORT-LOG 2026-07-23. |
| `frameworks/av` | Revert "codec2: Extend the queue empty work hack to MTK decoders too" | MTK decoder behavior (was the sole delta of the retired `frameworks/av` fork). Re-evaluate whether upstream still needs it. |
| `system/zygote` | tolerate unknown capability bounds on older kernels | Native App Zygote must skip PR_CAPBSET_READ EINVAL for capability bits absent from the running kernel; keep real drop failures fatal. Fixes Chrome startup and the ensuing application-start timeouts on 4.14. |

## Adding a patch

```bash
cd <project> && git format-patch -1 -o <tree>/patches/<project>/
```
Commit it here, push, done — a fresh `repo sync` + `apply-patches.sh` reproduces it.

## One-time: retiring the frameworks/av fork

The old fork is replaced by the `frameworks/av` patch above. To switch the live
tree over to upstream + patch:

```bash
# from tree root, with the frameworks/av override already removed from mt6893.xml
rm -rf frameworks/av .repo/projects/frameworks/av.git .repo/project-objects/android_frameworks_av.git
repo sync -c --force-sync frameworks/av      # re-clones pristine LineageOS
./patches/apply-patches.sh                   # re-applies the revert on a topic branch
```
