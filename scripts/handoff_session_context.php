<?php
declare(strict_types=1);

function handoff_valid_terminal_id(string $id): bool
{
    return preg_match('/^[a-f0-9]{8}(?:[a-f0-9]{8})?$/D', $id) === 1;
}

function handoff_apply_session_context(array $entry, array $environment, ?string $mapDirectory = null): array
{
    $thread = (string) ($environment['CODEX_THREAD_ID'] ?? $environment['CODEX_SESSION_ID'] ?? '');
    $session = trim((string) ($entry['workspaceboard_session'] ?? ''));
    $envSession = trim((string) ($environment['WORKSPACEBOARD_SESSION_ID'] ?? ''));
    $method = '';
    // Older callers sometimes put a known Codex UUID in the board-session slot.
    // Resolve that exact owner-scoped alias, even after the caller changes threads.
    if (preg_match('/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/D', $session)) {
        $directory = $mapDirectory ?? '/Users/werkstatt/ai_workspace/.work/workspaceboard-thread-links';
        $file = $directory . '/' . $session . '.json';
        $map = is_file($file) ? json_decode((string) file_get_contents($file), true) : null;
        $owner = (int) ($environment['CODEX_OWNER_USER_ID'] ?? 0);
        if (is_array($map) && ($map['codex_thread_id'] ?? '') === $session && $owner > 0
            && $owner === (int) ($map['owner_user_id'] ?? 0)
            && handoff_valid_terminal_id((string) ($map['workspaceboard_session'] ?? ''))) {
            $entry['metadata'] = is_array($entry['metadata'] ?? null) ? $entry['metadata'] : [];
            $entry['metadata']['requested_session_ref'] = $session;
            $session = $map['workspaceboard_session'];
            $method = 'verified_session_alias';
        }
    }
    // A Codex thread UUID is not a board terminal ID. Normalize only when the
    // caller supplied this exact current thread and we have authoritative context.
    if ($session === '' || ($thread !== '' && $session === $thread)) {
        if (handoff_valid_terminal_id($envSession)) {
            $session = $envSession;
            $method = 'terminal_environment';
        } elseif (preg_match('/^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/D', $thread)) {
            $directory = $mapDirectory ?? '/Users/werkstatt/ai_workspace/.work/workspaceboard-thread-links';
            $file = $directory . '/' . $thread . '.json';
            $map = is_file($file) ? json_decode((string) file_get_contents($file), true) : null;
            $mapped = (string) ($map['workspaceboard_session'] ?? '');
            $owner = (int) ($environment['CODEX_OWNER_USER_ID'] ?? 0);
            if (is_array($map) && ($map['codex_thread_id'] ?? '') === $thread
                && handoff_valid_terminal_id($mapped) && $owner > 0 && $owner === (int) ($map['owner_user_id'] ?? 0)) {
                $session = $mapped;
                $method = 'verified_thread_map';
            }
        }
    }
    $entry['workspaceboard_session'] = $session;
    $metadata = is_array($entry['metadata'] ?? null) ? $entry['metadata'] : [];
    if ($thread !== '') {
        if (isset($metadata['codex_thread_id']) && $metadata['codex_thread_id'] !== $thread) {
            $metadata['recording_codex_thread_id'] = $thread;
        } else {
            $metadata['codex_thread_id'] = $thread;
        }
    }
    if ($method !== '') $metadata['session_link'] = ['method' => $method, 'workspaceboard_session' => $session];
    $entry['metadata'] = $metadata;
    return $entry;
}
