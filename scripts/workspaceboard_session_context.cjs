'use strict';
const fs = require('node:fs');
const path = require('node:path');
const directory = '/Users/werkstatt/ai_workspace/.work/workspaceboard-thread-links';
const validSession = value => /^[a-f0-9]{8}(?:[a-f0-9]{8})?$/.test(value || '');
function environment(base, env = process.env) {
  return { ...base, ...(validSession(env.WORKSPACEBOARD_SESSION_ID) ? { WORKSPACEBOARD_SESSION_ID: env.WORKSPACEBOARD_SESSION_ID } : {}) };
}
function recordThread(thread, env = process.env, target = directory) {
  if (!validSession(env.WORKSPACEBOARD_SESSION_ID) || !/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/.test(thread || '')) return false;
  try {
  fs.mkdirSync(target, { recursive: true, mode: 0o700 });
  const file = path.join(target, thread + '.json');
  const temp = file + '.' + process.pid + '.tmp';
  fs.writeFileSync(temp, JSON.stringify({ codex_thread_id: thread, workspaceboard_session: env.WORKSPACEBOARD_SESSION_ID,
    owner_user_id: Number(env.CODEX_OWNER_USER_ID) || null, recorded_at: new Date().toISOString() }), { mode: 0o600 });
  fs.renameSync(temp, file);
  return true;
  } catch { return false; }
}
module.exports = { environment, recordThread };
