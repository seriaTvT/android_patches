#!/usr/bin/env python3
"""Apply the pinned MT6893 PixelOS snapshot, or verify it with --check."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--check',action='store_true',help='verify every final tree without changing sources')
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
args=parser.parse_args()
patches=Path(__file__).resolve().parent
root=args.root.resolve()
env=dict(os.environ,GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0')
def git(path,*command):
    return subprocess.check_output(['git','-C',str(path),*command],env=env,text=True).strip()
pending=[]
for item in json.loads((patches/'series.json').read_text()):
    project=root/item['project']
    patch=patches/'series'/item['patch']
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=item['sha256']:
        raise SystemExit('Patch hash mismatch: '+item['project'])
    if git(project,'status','--porcelain'):
        raise SystemExit('Commit or stash local changes first: '+item['project'])
    tree=git(project,'rev-parse','HEAD^{tree}')
    if tree==item['tree']:
        print('Verified:',item['project'])
        continue
    if args.check:
        raise SystemExit('Patch is not applied: '+item['project'])
    if git(project,'rev-parse','HEAD')!=item['base']:
        raise SystemExit('Unexpected base; do not force patches: '+item['project'])
    git(project,'apply','--index','--check',str(patch))
    pending.append((item,project,patch))
for item,project,patch in pending:
    git(project,'apply','--index',str(patch))
    if git(project,'write-tree')!=item['tree']:
        raise SystemExit('Unexpected resulting tree; inspect staged changes: '+item['project'])
    git(project,'-c','user.name=MT6893 PixelOS patches','-c',
        'user.email=63958697+seriaTvT@users.noreply.github.com','commit',
        '-m','Apply pinned PixelOS MT6893 compatibility: '+item['project'])
    print('Applied:',item['project'])
print('All pinned patch trees verified.')
