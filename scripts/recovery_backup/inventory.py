#!/usr/local/bin/python3.13
"""Metadata-only source inventory. Never emits individual paths or file contents."""
import fnmatch, os, stat, time
from pathlib import Path

def inventory(sources, excluded_names=(), excluded_paths=()):
    seen=set(); rows=[]
    excluded_paths=[Path(x).absolute() for x in excluded_paths]
    for source in sources:
        root=Path(source['path']).absolute()
        row=dict(label=source['label'],files=0,logical_bytes=0,allocated_bytes=0,
                 excluded_files=0,excluded_logical_bytes=0,unreadable=0,symlinks=0,special_files=0,sqlite_candidates=0)
        stack=[(root,False)]
        while stack:
            p,excluded=stack.pop()
            try:
                st=p.lstat()
                if stat.S_ISLNK(st.st_mode): row['symlinks']+=1;continue
                excluded=excluded or p.name in excluded_names or any(p==x or x in p.parents for x in excluded_paths)
                if stat.S_ISDIR(st.st_mode):
                    with os.scandir(p) as it: stack.extend((Path(e.path),excluded) for e in it)
                elif stat.S_ISREG(st.st_mode):
                    if excluded:
                        row['excluded_files']+=1;row['excluded_logical_bytes']+=st.st_size;continue
                    key=(st.st_dev,st.st_ino)
                    if key in seen:continue
                    seen.add(key)
                    row['files']+=1;row['logical_bytes']+=st.st_size;row['allocated_bytes']+=st.st_blocks*512
                    if not os.access(p,os.R_OK):row['unreadable']+=1
                    if p.suffix.lower() in ('.db','.sqlite','.sqlite3'):row['sqlite_candidates']+=1
                else:row['special_files']+=1
            except (OSError,ValueError):row['unreadable']+=1
        rows.append(row)
    return dict(generated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),sources=rows,
                total_logical_bytes=sum(x['logical_bytes'] for x in rows),
                total_allocated_bytes=sum(x['allocated_bytes'] for x in rows),
                unreadable=sum(x['unreadable'] for x in rows))
