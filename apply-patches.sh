#!/usr/bin/env bash
#
# Apply local patches to upstream-managed AOSP/LineageOS projects.
#
# Run this once after every `repo sync`, before `lunch`/`m`. It is idempotent:
# already-applied patches are skipped, so re-running is safe. A patch that no
# longer applies (upstream moved under it) stops the script with a clear error
# so you can rebase it -- that loud failure is the whole point of preferring
# patches over a silent fork.
#
# Layout: patches live under this script's dir, mirroring the project path they
# target, e.g.  system/core/0001-*.patch  ->  $TOP/system/core
#
set -euo pipefail

PATCHES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOP="${ANDROID_BUILD_TOP:-$(cd "$PATCHES_DIR/.." && pwd)}"
BRANCH="local-patches"

apply_one() {
    local proj="$1" patch="$2" dir="$TOP/$1"
    if [ ! -d "$dir/.git" ]; then
        echo "  ! skip: $proj not present (not synced?)"
        return 0
    fi
    # Already applied? A cleanly-reversing diff means the content is present.
    if git -C "$dir" apply --reverse --check "$patch" >/dev/null 2>&1; then
        echo "  = already applied: $(basename "$patch")"
        return 0
    fi
    # Put the commit on a topic branch so `repo sync` rebases it forward.
    ( cd "$dir" && { repo start "$BRANCH" . >/dev/null 2>&1 || git checkout -B "$BRANCH" >/dev/null 2>&1; } )
    if git -C "$dir" am "$patch" >/dev/null 2>&1; then
        echo "  + applied: $(basename "$patch")"
    else
        git -C "$dir" am --abort >/dev/null 2>&1 || true
        echo "  ! FAILED: $(basename "$patch") no longer applies to $proj -- rebase it" >&2
        return 1
    fi
}

rc=0
while IFS= read -r -d '' patch; do
    proj="$(dirname "${patch#"$PATCHES_DIR"/}")"
    apply_one "$proj" "$patch" || rc=1
done < <(find "$PATCHES_DIR" -name '*.patch' -print0 | sort -z)

if [ "$rc" -ne 0 ]; then
    echo "One or more patches need attention (see above)." >&2
fi
exit "$rc"
