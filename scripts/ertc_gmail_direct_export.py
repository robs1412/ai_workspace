#!/usr/bin/env python3
"""Direct Gmail exports for ERTC discovery gaps / privilege checks."""
from __future__ import annotations

import argparse, email, email.policy, hashlib, html, json, re, sys, time
from pathlib import Path
import importlib.util

GMAIL_SCRIPT=Path('/Users/werkstatt/ai_workspace/scripts/gmail_export.py')
CASE_ROOT=Path('/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work')
OUT_ROOT=CASE_ROOT/'02_Communications/discovery_export'

spec=importlib.util.spec_from_file_location('gm', GMAIL_SCRIPT)
gm=importlib.util.module_from_spec(spec); sys.modules['gm']=gm; spec.loader.exec_module(gm)


def safe(value, limit=120):
    value=re.sub(r'[/:\\\0]+',' - ', value or '').strip()
    value=re.sub(r'\s+',' ', value)
    return (value[:limit].strip() or 'message')

def html_to_text(value):
    value=re.sub(r'(?is)<(script|style).*?>.*?</\1>','',value)
    value=re.sub(r'(?i)<br\s*/?>','\n',value)
    value=re.sub(r'(?i)</p\s*>','\n\n',value)
    value=re.sub(r'<[^>]+>','',value)
    return html.unescape(value)

def body_text(msg):
    plain=[]; htmls=[]
    for part in msg.walk():
        if part.is_multipart(): continue
        if (part.get_content_disposition() or '').lower() == 'attachment': continue
        ctype=part.get_content_type()
        try: content=part.get_content()
        except Exception:
            payload=part.get_payload(decode=True) or b''
            content=payload.decode(part.get_content_charset() or 'utf-8', errors='replace')
        if ctype=='text/plain': plain.append(str(content))
        elif ctype=='text/html': htmls.append(html_to_text(str(content)))
    return '\n\n'.join(plain or htmls).strip()

def export_query(query, bucket, label, limit=500):
    access=gm.access_token(gm.DEFAULT_TOKEN, gm.DEFAULT_CLIENT_SECRET)
    refs=gm.list_messages(access, query, limit)
    root=OUT_ROOT/bucket/label
    for sub in ['eml','txt','metadata','attachments']:
        (root/sub).mkdir(parents=True, exist_ok=True)
    manifest=[]
    for i,ref in enumerate(refs,1):
        raw,api_meta=gm.get_message_raw(access, ref.message_id)
        msg=email.message_from_bytes(raw, policy=email.policy.default)
        subject=str(msg.get('Subject','no-subject'))
        prefix=f'{i:05d}-{ref.safe_id}-{safe(subject,80)}'
        eml_path=root/'eml'/f'{prefix}.eml'
        txt_path=root/'txt'/f'{prefix}.txt'
        meta_path=root/'metadata'/f'{prefix}.json'
        eml_path.write_bytes(raw)
        headers='\n'.join([
            f'From: {msg.get("From","")}', f'To: {msg.get("To","")}', f'Cc: {msg.get("Cc","")}',
            f'Date: {msg.get("Date","")}', f'Subject: {subject}', f'Gmail Export Bucket: {bucket}/{label}',
            f'Query: {query}', '', '--- BODY ---', ''
        ])
        txt_path.write_text(headers + body_text(msg) + '\n', encoding='utf-8', errors='replace')
        attach_dir=root/'attachments'/prefix
        attach_dir.mkdir(parents=True, exist_ok=True)
        attachments=[]; n=0
        for part in msg.walk():
            if part.is_multipart(): continue
            filename=part.get_filename()
            disp=part.get_content_disposition()
            if not filename and disp!='attachment': continue
            payload=part.get_payload(decode=True)
            if payload is None: continue
            n+=1
            target=attach_dir/f'{n:02d}-{safe(filename or f"attachment-{n}",160)}'
            target.write_bytes(payload)
            attachments.append(str(target))
        if not attachments:
            try: attach_dir.rmdir()
            except OSError: pass
        meta={
            'message_hash': ref.safe_id,
            'thread_hash': hashlib.sha256((ref.thread_id or '').encode()).hexdigest()[:16] if ref.thread_id else None,
            'query': query,
            'bucket': bucket,
            'label': label,
            'date': str(msg.get('Date','')),
            'from': str(msg.get('From','')),
            'to': str(msg.get('To','')),
            'cc': str(msg.get('Cc','')),
            'subject': subject,
            'label_ids': api_meta.get('labelIds',[]),
            'eml_export': str(eml_path),
            'txt_export': str(txt_path),
            'attachments': attachments,
            'exported_at': int(time.time()),
        }
        meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding='utf-8')
        manifest.append(meta)
    man=root/f'{label}_manifest.csv'
    import csv
    with man.open('w', newline='', encoding='utf-8') as fh:
        fields=['message_hash','date','from','to','cc','subject','eml_export','txt_export','attachments_count','query']
        wr=csv.DictWriter(fh, fieldnames=fields); wr.writeheader()
        for m in manifest:
            wr.writerow({k: (len(m['attachments']) if k=='attachments_count' else m.get(k,'')) for k in fields})
    summary={'query':query,'bucket':bucket,'label':label,'messages':len(manifest),'attachments':sum(len(m['attachments']) for m in manifest),'manifest':str(man)}
    (root/f'{label}_summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps(summary, indent=2, sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--query', required=True)
    ap.add_argument('--bucket', default='privileged_alan_borlack')
    ap.add_argument('--label', default='gmail_direct')
    ap.add_argument('--limit', type=int, default=500)
    args=ap.parse_args()
    export_query(args.query, args.bucket, args.label, args.limit)

if __name__=='__main__': main()
