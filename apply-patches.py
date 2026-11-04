#!/usr/bin/env python3
"""Apply pinned LOS24 patches and verify source trees without resetting branches."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--check', action='store_true')
p.add_argument('--top', type=Path)
args = p.parse_args()
patches = Path(__file__).resolve().parent
top = (args.top or patches.parent).resolve()
series = json.loads((patches / 'series.json').read_text())

def git(repo, *cmd):
    return subprocess.check_output(['git', '-C', str(repo), *cmd], text=True).strip()

pending = []
for row in series:
    repo = top / row['project']
    assert (repo / '.git').exists(), f'Missing project: {repo}'
    assert not git(repo, 'diff', '--name-only', 'HEAD'), f'Tracked changes: {repo}'
    for patch in row['patches']:
        f = patches / patch['file']
        assert hashlib.sha256(f.read_bytes()).hexdigest() == patch['sha256'], str(f)
    if git(repo, 'rev-parse', 'HEAD^{tree}') == row['tree']:
        print('Verified:', row['project'], flush=True)
        continue
    assert not args.check, f'Not patched: {repo}'
    assert git(repo, 'rev-parse', 'HEAD') == row['base'], f'Wrong base: {repo}'
    assert not git(repo, 'ls-files', '--others', '--exclude-standard'), f'Untracked files: {repo}'
    pending.append(row)

for row in pending:
    repo = top / row['project']
    branches = git(repo, 'for-each-ref', '--format=%(refname:short)', 'refs/heads').splitlines()
    branch = 'los24-patches'
    n = 1
    while branch in branches:
        branch = f'los24-patches-{n}'
        n += 1
    subprocess.run(['git', '-C', str(repo), 'switch', '-c', branch], check=True)
    command = ['git', '-C', str(repo), '-c', 'user.name=LOS24 Builder',
               '-c', 'user.email=los24-builder@localhost', 'am', '--committer-date-is-author-date']
    command += [str(patches / item['file']) for item in row['patches']]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        subprocess.run(['git', '-C', str(repo), 'am', '--abort'], check=False)
        raise
    assert git(repo, 'rev-parse', 'HEAD^{tree}') == row['tree'], f'Tree mismatch: {repo}'
    print('Applied and verified:', row['project'], flush=True)
print('All pinned LOS24 source trees verified', flush=True)
