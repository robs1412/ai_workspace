'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const context = require('../../scripts/workspaceboard_session_context.cjs');
test('only valid terminal context is added; owner markers are preserved', () => {
 assert.deepEqual(context.environment({CODEX_OWNER_USER_ID:'1'}, {WORKSPACEBOARD_SESSION_ID:'3339bac44fbdbed5'}), {CODEX_OWNER_USER_ID:'1',WORKSPACEBOARD_SESSION_ID:'3339bac44fbdbed5'});
 assert.deepEqual(context.environment({CODEX_OWNER_USER_ID:'1'}, {WORKSPACEBOARD_SESSION_ID:'bad/value'}), {CODEX_OWNER_USER_ID:'1'});
});
test('thread mapping survives resume and contains only identity metadata', t => {
 const dir=fs.mkdtempSync(path.join(__dirname,'map-test-'));
 t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const thread='01a16935-af1e-7503-9c78-aa8d13205095';
 const env={WORKSPACEBOARD_SESSION_ID:'3339bac44fbdbed5',CODEX_OWNER_USER_ID:'1'};
 assert.equal(context.recordThread(thread,env,dir),true);
 const value=JSON.parse(fs.readFileSync(path.join(dir,thread+'.json')));
 assert.equal(value.workspaceboard_session,env.WORKSPACEBOARD_SESSION_ID);
 assert.equal(value.owner_user_id,1);
 assert.equal(context.recordThread('../bad',env,dir),false);
});
