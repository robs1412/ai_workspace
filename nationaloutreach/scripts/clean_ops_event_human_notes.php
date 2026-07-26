#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function clean_ops_event_text(?string $text): ?string
{
    if ($text === null) {
        return null;
    }

    $text = str_replace(["\r\n", "\r"], "\n", $text);
    $lines = explode("\n", $text);
    $clean = [];
    $lastBlank = false;

    foreach ($lines as $line) {
        $line = trim($line);
        $originalLine = $line;

        $line = preg_replace('/\s*\[[^\]]*taskflow-[^\]]*\]\s*/i', ' ', $line) ?? $line;
        $line = preg_replace('/\s*\/?\s*taskflow-[a-z0-9]+(?:\s*\/\s*taskflow-[a-z0-9]+)*/i', '', $line) ?? $line;
        $line = preg_replace('/\s*\[(connecteam-import-key|connecteam-source|wfm-request|wfm-store|wfm-approved|wfm-canceled):[^\]]*\]\s*/i', '', $line) ?? $line;
        $line = preg_replace('/,?\s*(?:Source proof\s*)?(?:Original source\s*)?(?:Source\s*)?Message-ID:?\s*<?[^>\s]+>?\s*\.?/i', '', $line) ?? $line;
        $line = preg_replace('/\s+from\s+National Outreach source\s+[a-z0-9._%+\-=]+@[a-z0-9.\-]+\.?/i', '', $line) ?? $line;
        $line = preg_replace('/WFM cancellation confirmation recorded from .*?:\s*/i', 'WFM cancellation: ', $line) ?? $line;
        $line = preg_replace('/\s*No new WFM portal login was needed\.?/i', '', $line) ?? $line;
        $line = preg_replace('/\s*Imported from Robert-approved WFM import request; WFM portal field still read Pending at refresh\.?/i', '', $line) ?? $line;
        $line = preg_replace('/^Event page readback on [^:]+:\s*/i', 'Event details: ', $line) ?? $line;
        $line = preg_replace('/\s*OPS task\s+\d+\.?\s*Created from AI Manager approved OPS follow-through\.?/i', '', $line) ?? $line;
        $line = preg_replace('/\s*Task Flow:\s*\.?\s*$/i', '', $line) ?? $line;
        $line = trim(preg_replace('/\s{2,}/', ' ', $line) ?? $line);

        if ($line === '') {
            if (!$lastBlank && $clean !== []) {
                $clean[] = '';
                $lastBlank = true;
            }
            continue;
        }

        if (preg_match('/^Created by Codex[^.]*\.\s*(.+)$/i', $line, $m)) {
            $line = trim((string) $m[1]);
        }

        if (preg_match('/^(Task Flow|Dedupe key|Source update|Created from AI Manager|Created by Codex|AI Manager approved|Workspaceboard)\b/i', $line)) {
            continue;
        }
        if (preg_match('/^(Direct instruction|Requested deliverable):\s*(add|create|update|route|send|confirm)\b/i', $line)) {
            continue;
        }
        if (preg_match('/^Moved from\b/i', $line)) {
            continue;
        }
        if (preg_match('/\b(source packet|source email|source thread|source proof)\b/i', $line) && preg_match('/\b(no|not|missing|pending|copied|routed)\b/i', $line)) {
            continue;
        }
        if (preg_match('/^(Approval source|Portal refresh|Linked to CRM account)\b/i', $line)) {
            continue;
        }
        if (preg_match('/^Imported from Robert-approved WFM import request\b/i', $line)) {
            continue;
        }
        if (preg_match('/\b(Message-ID|taskflow-|Dedupe key|Workspaceboard|approved send cycle|source can be filed|source_ref|approval_gates)\b/i', $line)) {
            continue;
        }
        if (preg_match('/^[a-z0-9._%+\-]+@[a-z0-9.\-]+>?$/i', $line) || preg_match('/^(gmail|mail|outlook|namprd|eurprd)[a-z0-9.\->]*$/i', $line)) {
            continue;
        }

        if (preg_match('/^Source:\s*(https?:\/\/\S+)\s*;?\s*(.*)$/i', $line, $m)) {
            $tail = trim((string) $m[2]);
            $line = $tail !== '' ? $tail : 'Event page: ' . $m[1];
        } elseif (preg_match('/^Source:\s*(.*)$/i', $line, $m)) {
            continue;
        }
        $line = preg_replace('/\s*Source:\s*(https?:\/\/\S+)/i', ' Event page: $1', $line) ?? $line;
        $line = preg_replace('/\s*Source:\s*[^.]+\.?/i', '', $line) ?? $line;

        $line = preg_replace('/\bEvent details from source:/i', 'Event details:', $line) ?? $line;
        $line = preg_replace('/\bParticipation notes from source:/i', 'Participation notes:', $line) ?? $line;
        $line = preg_replace('/\bPrep notes from source thread:/i', 'Prep notes:', $line) ?? $line;
        $line = preg_replace('/\bSource registration link:/i', 'Registration link:', $line) ?? $line;
        $line = preg_replace('/\bSource also\b/i', 'Also', $line) ?? $line;
        $line = preg_replace('/\bper source\b/i', '', $line) ?? $line;
        $line = preg_replace('/\bfrom source\b/i', '', $line) ?? $line;
        $line = preg_replace('/\bnot specified in source\b/i', 'not specified', $line) ?? $line;
        $line = preg_replace('/\bin source\b/i', 'in the request', $line) ?? $line;
        $line = preg_replace('/\bProducts\/assignee\b/i', 'Products and assignee', $line) ?? $line;
        $line = preg_replace('/\bSource text says\b/i', 'Original list says', $line) ?? $line;
        $line = preg_replace('/\bEvent page\s+:/i', 'Event page:', $line) ?? $line;
        $line = preg_replace('/\s{2,}/', ' ', $line) ?? $line;
        $line = trim($line, " \t\n\r\0\x0B;.");
        if ($line === '') {
            continue;
        }
        if ($line !== $originalLine && preg_match('/\b(Source|Message-ID|Task Flow|taskflow-|source packet|source email)\b/i', $line)) {
            continue;
        }

        $clean[] = $line;
        $lastBlank = false;
    }

    while ($clean !== [] && end($clean) === '') {
        array_pop($clean);
    }

    $result = trim(implode("\n", $clean));
    return $result === '' ? null : $result;
}

function has_machine_note(?string $text): bool
{
    if ($text === null || trim($text) === '') {
        return false;
    }
    return (bool) preg_match(
        '/Message-ID|Task Flow|taskflow-|Dedupe key|connecteam-import-key|connecteam-source|wfm-request:|wfm-store:|wfm-approved:|wfm-canceled:|Interactions email|No new WFM portal login|Imported from Robert-approved WFM import request|Event page readback|National Outreach source|@mail\.gmail\.com|Source:|Source update|Source proof Message-ID|Source Message-ID|Created by Codex|AI Manager|source_ref|approval_gates|approved send cycle|source can be filed/i',
        $text
    );
}

$apply = in_array('--apply', $argv, true);
$backupDir = '/Users/werkstatt/ai_workspace/.private/ops-event-note-cleanup';
if (!is_dir($backupDir) && !mkdir($backupDir, 0700, true) && !is_dir($backupDir)) {
    throw new RuntimeException('Unable to create backup directory.');
}

$pdo = get_event_pdo();
$stmt = $pdo->query(
    'SELECT id, event_name, event_date, notes, important_information
       FROM event_bookings
      ORDER BY event_date DESC, id DESC'
);
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
$changes = [];

foreach ($rows as $row) {
    $oldNotes = $row['notes'] ?? null;
    $oldImportant = $row['important_information'] ?? null;
    if (!has_machine_note($oldNotes) && !has_machine_note($oldImportant)) {
        continue;
    }

    $newNotes = clean_ops_event_text(is_string($oldNotes) ? $oldNotes : null);
    $newImportant = clean_ops_event_text(is_string($oldImportant) ? $oldImportant : null);
    if ($newNotes === $oldNotes && $newImportant === $oldImportant) {
        continue;
    }

    $changes[] = [
        'id' => (int) $row['id'],
        'event_name' => (string) $row['event_name'],
        'event_date' => (string) $row['event_date'],
        'old_notes' => $oldNotes,
        'new_notes' => $newNotes,
        'old_important_information' => $oldImportant,
        'new_important_information' => $newImportant,
    ];
}

$backupPath = $backupDir . '/ops-event-note-cleanup-' . date('Ymd-His') . ($apply ? '-applied' : '-preview') . '.json';
file_put_contents($backupPath, json_encode($changes, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n", LOCK_EX);
chmod($backupPath, 0600);

if ($apply && $changes !== []) {
    $update = $pdo->prepare(
        'UPDATE event_bookings
            SET notes = :notes,
                important_information = :important_information,
                updated_at = CURRENT_TIMESTAMP
          WHERE id = :id'
    );
    $pdo->beginTransaction();
    try {
        foreach ($changes as $change) {
            $update->execute([
                ':notes' => $change['new_notes'],
                ':important_information' => $change['new_important_information'],
                ':id' => $change['id'],
            ]);
        }
        $pdo->commit();
    } catch (Throwable $e) {
        $pdo->rollBack();
        throw $e;
    }
}

$sample = array_slice(array_map(static function (array $change): array {
    return [
        'id' => $change['id'],
        'event_name' => $change['event_name'],
        'event_date' => $change['event_date'],
        'new_notes' => $change['new_notes'],
        'new_important_information' => $change['new_important_information'],
    ];
}, $changes), 0, 12);

echo json_encode([
    'ok' => true,
    'mode' => $apply ? 'applied' : 'preview',
    'changed_rows' => count($changes),
    'backup_path' => $backupPath,
    'sample' => $sample,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
