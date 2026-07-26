#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';
require_once '/Users/werkstatt/ops/outreach_team_chat_notifier.php';

const SOURCE_REF = 'caatx44bod=mmn1h7g-39okgubb3jzw2lwilrqgztge3vjrqzoa@mail.gmail.com';
const SOURCE_MESSAGE_ID = '<CAAtX44bOd=mmn1H7g-39oKgubb3JZw2LWiLRqGZTgE3vjrqzoA@mail.gmail.com>';
const TASK_FLOW_KEY = 'taskflow-2cfe293b213abef4';
const WORKSPACEBOARD_SESSION = 'c6b98146';
const CAMPAIGN_SOURCE_ID = 581;
const CAMPAIGN_LIST_IDS = [73, 95];
const EVENTS = [
    1032 => ['name' => "Binny's Algonquin Tasting", 'date' => '2026-07-24', 'shift_id' => 5560],
    1124 => ['name' => 'Saloon Royale Tasting', 'date' => '2026-07-25', 'shift_id' => 5668],
    1030 => ['name' => "Binny's Orland Park Tasting", 'date' => '2026-07-25', 'shift_id' => 5558],
    1031 => ['name' => "Binny's Geneva Tasting", 'date' => '2026-07-25', 'shift_id' => 5559],
    955 => ['name' => 'Park Ridge Market After Dark', 'date' => '2026-07-25', 'shift_id' => 5396],
    1037 => ['name' => "Binny's Hyde Park Tasting", 'date' => '2026-07-25', 'shift_id' => 5565],
];

/** @param array<string,mixed> $payload */
function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create National Outreach outbox.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode completion draft.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write completion draft.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install completion draft.');
    }
    chmod($path, 0600);
}

/** @param array<string,mixed> $packet */
function record_task_flow(array $packet, string $event): void
{
    $process = proc_open(
        ['/usr/local/bin/php', '/Users/werkstatt/workspaceboard/scripts/planner/task_flow_mysql_recorder.php', 'record'],
        [0 => ['pipe', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
        $pipes,
        '/Users/werkstatt/workspaceboard'
    );
    if (!is_resource($process)) {
        throw new RuntimeException('Unable to start Task Flow recorder.');
    }
    fwrite($pipes[0], json_encode(['event' => $event, 'packet' => $packet], JSON_UNESCAPED_SLASHES) ?: '{}');
    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    if (proc_close($process) !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

/** @return list<array<string,mixed>> */
function event_readback(PDO $pdo, bool $forUpdate = false): array
{
    $ids = array_keys(EVENTS);
    $placeholders = implode(',', array_fill(0, count($ids), '?'));
    $sql = "SELECT id, event_name, event_date, start_time, end_time, event_location, is_pioneer_tasting
              FROM event_bookings
             WHERE id IN ($placeholders)
             ORDER BY event_date, start_time, id";
    if ($forUpdate) {
        $sql .= ' FOR UPDATE';
    }
    $stmt = $pdo->prepare($sql);
    $stmt->execute($ids);
    return $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
}

/** @return list<array<string,mixed>> */
function verified_schedule(PDO $pdo): array
{
    $rows = event_readback($pdo);
    if (count($rows) !== count(EVENTS)) {
        throw new RuntimeException('The reviewed six-event OPS schedule is incomplete.');
    }
    $links = fetch_event_booking_shift_links(array_keys(EVENTS), false);
    foreach ($rows as &$row) {
        $eventId = (int) $row['id'];
        $expected = EVENTS[$eventId] ?? null;
        if (!is_array($expected)
            || (string) $row['event_name'] !== $expected['name']
            || (string) $row['event_date'] !== $expected['date']) {
            throw new RuntimeException('OPS event ' . $eventId . ' no longer matches the reviewed schedule.');
        }
        $shift = null;
        foreach (($links[$eventId] ?? []) as $candidate) {
            if ((int) ($candidate['shift_id'] ?? 0) === (int) $expected['shift_id']
                && (int) ($candidate['deleted'] ?? 0) === 0) {
                $shift = $candidate;
                break;
            }
        }
        if (!is_array($shift)) {
            throw new RuntimeException('OPS event ' . $eventId . ' is missing reviewed shift ' . $expected['shift_id'] . '.');
        }
        $row['shift_id'] = (int) $expected['shift_id'];
        $row['assigned_count'] = (int) ($shift['assigned_count'] ?? 0);
        $row['ops_url'] = 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId;
        $row['shift_url'] = 'https://www.koval-distillery.com/ops/index.php?view=shifts&focus=' . (int) $expected['shift_id'];
    }
    unset($row);
    return $rows;
}

function time_label(string $start, string $end): string
{
    $format = static function (string $value): string {
        $time = DateTimeImmutable::createFromFormat('H:i:s', $value);
        return $time ? $time->format('g:i A') : $value;
    };
    return $format($start) . '-' . $format($end);
}

/** @param list<array<string,mixed>> $events @return array{subject:string,html:string,text:string,chat:string} */
function content(array $events): array
{
    $subject = 'This week\'s KOVAL tastings are Pioneer Tastings';
    $plain = [
        'Hi COTeam and Management Team,',
        '',
        'All six OPS tasting-schedule rows for July 24-25 are now marked as Pioneer Tastings in OPS so Pioneer bonus tracking recognizes them explicitly.',
        '',
    ];
    $chat = [
        'Pioneer Tasting update for July 24-25:',
        '',
        'All six upcoming tasting-schedule rows are now marked as Pioneer Tastings in OPS for bonus tracking.',
        '',
    ];
    $htmlRows = '';
    foreach ($events as $event) {
        $coverage = (int) $event['assigned_count'] > 0 ? 'Covered' : 'Open - please claim in OPS';
        $line = $event['event_date'] . ', ' . time_label((string) $event['start_time'], (string) $event['end_time'])
            . ': ' . $event['event_name'] . ' (' . $coverage . ', OPS #' . $event['id'] . ', shift #' . $event['shift_id'] . ')';
        $plain[] = '- ' . $line;
        $plain[] = '  OPS: ' . $event['ops_url'];
        $chat[] = '- ' . $line;
        $chat[] = '  ' . ((int) $event['assigned_count'] > 0 ? $event['ops_url'] : $event['shift_url']);
        $htmlRows .= '<tr><td>' . htmlspecialchars((string) $event['event_date']) . '</td>'
            . '<td>' . htmlspecialchars(time_label((string) $event['start_time'], (string) $event['end_time'])) . '</td>'
            . '<td>' . htmlspecialchars((string) $event['event_name']) . '</td>'
            . '<td>' . htmlspecialchars($coverage) . '</td>'
            . '<td><a href="' . htmlspecialchars((string) $event['ops_url']) . '">OPS #' . (int) $event['id'] . '</a></td></tr>';
    }
    $plain = array_merge($plain, [
        '',
        'Please claim any open shift in OPS if you can cover it. This message was sent from a no-reply list address; email Vanessa directly instead of replying to the list sender.',
        '',
        'Best,',
        'Vanessa Sterling',
        'Outreach Coordinator',
    ]);
    $chat[] = '';
    $chat[] = 'Please claim any open shift in OPS if you can cover it.';
    $html = '<!doctype html><html><body style="font-family:Arial,sans-serif">'
        . '<p>Hi COTeam and Management Team,</p>'
        . '<p>All six OPS tasting-schedule rows for July 24-25 are now marked as <strong>Pioneer Tastings</strong> in OPS so Pioneer bonus tracking recognizes them explicitly.</p>'
        . '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse"><thead><tr><th>Date</th><th>Time</th><th>Event</th><th>Coverage</th><th>OPS</th></tr></thead><tbody>'
        . $htmlRows . '</tbody></table>'
        . '<p>Please claim any open shift in OPS if you can cover it. This message was sent from a no-reply list address; email Vanessa directly instead of replying to the list sender.</p>'
        . '<p>Best,<br>Vanessa Sterling<br>Outreach Coordinator</p></body></html>';
    return ['subject' => $subject, 'html' => $html, 'text' => implode("\n", $plain), 'chat' => implode("\n", $chat)];
}

/** @return array<string,mixed> */
function campaign_readback(PDO $pdo, int $campaignId): array
{
    $stmt = $pdo->prepare(
        "SELECT m.id, m.subject, m.fromfield, m.replyto, m.status, m.processed, m.sent, m.sendstart,
                GROUP_CONCAT(DISTINCT CONCAT(l.id, ':', l.name) ORDER BY l.id SEPARATOR '|') AS target_lists
           FROM koval_plst1.phplist_message m
           LEFT JOIN koval_plst1.phplist_listmessage lm ON lm.messageid = m.id
           LEFT JOIN koval_plst1.phplist_list l ON l.id = lm.listid
          WHERE m.id = ?
          GROUP BY m.id"
    );
    $stmt->execute([$campaignId]);
    return $stmt->fetch(PDO::FETCH_ASSOC) ?: [];
}

/** @param array{subject:string,html:string,text:string,chat:string} $copy */
function create_or_get_campaign(PDO $pdo, array $copy, bool $submit): int
{
    $existing = $pdo->prepare(
        "SELECT id FROM koval_plst1.phplist_messagedata WHERE name = 'codex_source' AND data = ? ORDER BY id DESC LIMIT 1"
    );
    $existing->execute([SOURCE_REF]);
    $campaignId = (int) ($existing->fetchColumn() ?: 0);
    if ($campaignId <= 0) {
        $pdo->beginTransaction();
        try {
            $source = $pdo->prepare('SELECT * FROM koval_plst1.phplist_message WHERE id = ? FOR UPDATE');
            $source->execute([CAMPAIGN_SOURCE_ID]);
            $row = $source->fetch(PDO::FETCH_ASSOC);
            if (!is_array($row)) {
                throw new RuntimeException('Known-good phpList source campaign is missing.');
            }
            unset($row['id']);
            $row = array_merge($row, [
                'subject' => $copy['subject'],
                'fromfield' => 'Vanessa Sterling <noreply@lists.koval-distillery.com>',
                'tofield' => '',
                'replyto' => 'vanessa.sterling@kovaldistillery.com',
                'message' => $copy['html'],
                'textmessage' => $copy['text'],
                'entered' => date('Y-m-d H:i:s'),
                'modified' => date('Y-m-d H:i:s'),
                'embargo' => date('Y-m-d H:i:s'),
                'repeatuntil' => date('Y-m-d H:i:s'),
                'requeueuntil' => date('Y-m-d H:i:s'),
                'status' => 'draft',
                'sent' => null,
                'processed' => 0,
                'viewed' => 0,
                'bouncecount' => 0,
                'sendstart' => null,
                'uuid' => (string) $pdo->query('SELECT UUID()')->fetchColumn(),
            ]);
            $columns = array_keys($row);
            $insert = $pdo->prepare(
                'INSERT INTO koval_plst1.phplist_message (`' . implode('`,`', $columns) . '`) VALUES ('
                . implode(',', array_fill(0, count($columns), '?')) . ')'
            );
            $insert->execute(array_values($row));
            $campaignId = (int) $pdo->lastInsertId();

            $sourceData = $pdo->prepare('SELECT name, data FROM koval_plst1.phplist_messagedata WHERE id = ?');
            $sourceData->execute([CAMPAIGN_SOURCE_ID]);
            $data = [];
            foreach ($sourceData->fetchAll(PDO::FETCH_ASSOC) ?: [] as $item) {
                $data[(string) $item['name']] = (string) $item['data'];
            }
            $data = array_merge($data, [
                'id' => (string) $campaignId,
                'subject' => $copy['subject'],
                'campaigntitle' => $copy['subject'],
                'fromfield' => 'Vanessa Sterling <noreply@lists.koval-distillery.com>',
                'from_identity' => 'Vanessa Sterling',
                'replyto' => 'vanessa.sterling@kovaldistillery.com',
                'message' => $copy['html'],
                'textmessage' => $copy['text'],
                'status' => 'draft',
                'targetlist' => 'a:3:{i:73;s:2:"73";i:95;s:2:"95";s:8:"unselect";s:2:"-1";}',
                'template' => '70',
                'sendformat' => 'HTML',
                'to process' => '0',
                'samplesent' => '0',
                'sampletime' => '0',
                'last msg sent' => '0',
                'start_notified' => '',
                'end_notified' => '',
                'codex_source' => SOURCE_REF,
                'codex_pioneer_event_ids' => implode(',', array_keys(EVENTS)),
            ]);
            $insertData = $pdo->prepare('INSERT INTO koval_plst1.phplist_messagedata (id, name, data) VALUES (?, ?, ?)');
            foreach ($data as $name => $value) {
                $insertData->execute([$campaignId, $name, $value]);
            }
            $insertList = $pdo->prepare('INSERT INTO koval_plst1.phplist_listmessage (messageid, listid, entered) VALUES (?, ?, NOW())');
            foreach (CAMPAIGN_LIST_IDS as $listId) {
                $insertList->execute([$campaignId, $listId]);
            }
            $pdo->commit();
        } catch (Throwable $error) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            throw $error;
        }
    }
    if ($submit) {
        $pdo->beginTransaction();
        try {
            $stmt = $pdo->prepare("UPDATE koval_plst1.phplist_message SET status = 'submitted', modified = NOW(), embargo = NOW() WHERE id = ? AND status = 'draft'");
            $stmt->execute([$campaignId]);
            $stmt = $pdo->prepare("UPDATE koval_plst1.phplist_messagedata SET data = 'submitted' WHERE id = ? AND name = 'status'");
            $stmt->execute([$campaignId]);
            $pdo->commit();
        } catch (Throwable $error) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            throw $error;
        }
    }
    return $campaignId;
}

$submit = in_array('--submit', $argv, true);
$postChat = in_array('--post-chat', $argv, true);
$finalize = in_array('--finalize', $argv, true);
$pdo = get_event_pdo();
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$pdo->beginTransaction();
try {
    ensure_event_bookings_pioneer_flag_column($pdo);
    $before = event_readback($pdo, true);
    if (count($before) !== count(EVENTS)) {
        throw new RuntimeException('The reviewed six-event OPS schedule is incomplete.');
    }
    foreach ($before as $row) {
        $eventId = (int) $row['id'];
        $expected = EVENTS[$eventId] ?? null;
        if (!is_array($expected)
            || (string) $row['event_name'] !== $expected['name']
            || (string) $row['event_date'] !== $expected['date']) {
            throw new RuntimeException('OPS event ' . $eventId . ' no longer matches the reviewed schedule.');
        }
    }
    $ids = array_keys(EVENTS);
    $update = $pdo->prepare(
        'UPDATE event_bookings SET is_pioneer_tasting = 1, updated_at = CURRENT_TIMESTAMP WHERE id IN ('
        . implode(',', array_fill(0, count($ids), '?')) . ') AND is_pioneer_tasting <> 1'
    );
    $update->execute($ids);
    $pdo->commit();
} catch (Throwable $error) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    throw $error;
}

$events = verified_schedule($pdo);
foreach ($events as $event) {
    if ((int) $event['is_pioneer_tasting'] !== 1) {
        throw new RuntimeException('Pioneer flag readback failed for OPS event ' . $event['id'] . '.');
    }
}
$copy = content($events);
$campaignId = create_or_get_campaign($pdo, $copy, $submit);

ensure_outreach_team_chat_log_table($pdo);
$chatType = 'pioneer_weekly_schedule';
$chatMessageName = '';
$chatStatus = 'not_requested';
if ($postChat) {
    $lookup = $pdo->prepare(
        'SELECT chat_message_name FROM ' . OUTREACH_TEAM_CHAT_LOG_TABLE
        . ' WHERE notification_key = ? AND chat_target = ? LIMIT 1'
    );
    $notificationKey = 'outreach-team-chat|pioneer-weekly|' . TASK_FLOW_KEY;
    $lookup->execute([$notificationKey, OUTREACH_TEAM_CHAT_TARGET]);
    $chatMessageName = trim((string) ($lookup->fetchColumn() ?: ''));
    if ($chatMessageName !== '') {
        $chatStatus = 'already_sent';
    } else {
        $result = send_outreach_team_chat_message($copy['chat']);
        if (!($result['ok'] ?? false)) {
            throw new RuntimeException('Outreach Team Chat post failed: ' . (string) ($result['error'] ?? 'unknown error'));
        }
        $chatMessageName = trim((string) (($result['message']['name'] ?? '') ?: ''));
        if ($chatMessageName === '') {
            throw new RuntimeException('Outreach Team Chat returned no message id.');
        }
        record_outreach_team_chat_notification($pdo, [
            'event_id' => 1032,
            'shift_id' => 5560,
            'notification_type' => $chatType,
            'notification_key' => $notificationKey,
            'chat_target' => OUTREACH_TEAM_CHAT_TARGET,
            'chat_message_name' => $chatMessageName,
        ]);
        $chatStatus = 'sent';
    }
}

$campaign = campaign_readback($pdo, $campaignId);
$proofMarker = 'OPS_PIONEER_955_1030_1031_1032_1037_1124_PHPLIST_' . $campaignId . '_CHAT';
$draftPath = '';
if ($finalize) {
    if ((string) ($campaign['status'] ?? '') !== 'sent' || $chatMessageName === '') {
        throw new RuntimeException('Cannot finalize without sent phpList and recorded Chat proof.');
    }
    $verification = 'Live OPS readback: events 955, 1030, 1031, 1032, 1037, and 1124 have is_pioneer_tasting=1; phpList campaign '
        . $campaignId . ' sent to lists 73/95; Outreach Team Chat message id recorded.';
    $packet = [
        'source_ref' => SOURCE_REF,
        'dedupe_key' => TASK_FLOW_KEY,
        'intake_channel' => 'email:nationaloutreach',
        'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
        'workspaceboard_session' => WORKSPACEBOARD_SESSION,
        'ops_portal_or_domain_task' => 'OPS Outreach events 955, 1030, 1031, 1032, 1037, 1124',
        'status' => 'reported',
        'due_or_trigger' => 'Robert instructed Vanessa to make all six upcoming tasting-schedule rows Pioneer Tastings and notify the team.',
        'scheduled_action' => 'Four unassigned shifts remain open: 5558, 5559, 5560, and 5565.',
        'calendar_event' => 'Six OPS Outreach event rows for July 24-25, 2026',
        'source_links' => 'Re: Upcoming KOVAL tastings this week',
        'approval_gates' => 'Direct Robert instruction; routine OPS update and internal team notification approved.',
        'verification_readback' => $verification,
        'next_update' => 'Await COTeam claims for open shifts 5558, 5559, 5560, and 5565.',
        'requested_deliverable' => 'Mark all six upcoming tasting rows as Pioneer Tastings for bonus tracking and notify the team.',
        'human_owner_or_recipient' => 'COTeam list 73; Management Group list 95; Outreach Team Google Chat; Robert completion reply',
        'output_channel' => 'OPS, phpList email, Outreach Team Google Chat, and same-thread email',
        'proof_required' => 'OPS Pioneer flag readback, phpList sent readback, Chat message id, completion Message-ID, and archive proof',
        'result_email_required' => 'true',
        'owner_question_required' => 'false',
        'proof_marker' => $proofMarker,
    ];
    $body = implode("\n", [
        'Robert,',
        '',
        'Done. All six tastings in the July 24-25 OPS schedule are now explicitly marked as Pioneer Tastings for bonus tracking.',
        '',
        'I also notified COTeam and Management by email and posted the update in the Outreach Team Google Chat. Four linked shifts remain open: Algonquin, Orland Park, Geneva, and Hyde Park.',
        '',
        'Best,',
        '',
        'Vanessa',
        '',
        'Vanessa Sterling',
        'Outreach Coordinator',
        'KOVAL Distillery',
        '4241 N Ravenswood Ave',
        'Chicago, IL 60613',
        '312 878 7988',
        'http://www.koval-distillery.com',
    ]);
    $draftPath = '/Users/admin/.nationaloutreach-launch/state/outbox/' . TASK_FLOW_KEY . '-weekly-pioneer-completion.approved.json';
    write_json_file($draftPath, [
        'action_id' => TASK_FLOW_KEY . '-weekly-pioneer-completion',
        'source_ref' => SOURCE_REF,
        'source_message_id' => SOURCE_REF,
        'status' => 'reported',
        'from' => 'vanessa.sterling@kovaldistillery.com',
        'from_name' => 'Vanessa Sterling',
        'to' => ['robert@kovaldistillery.com'],
        'cc' => [],
        'bcc' => [],
        'subject' => 'Re: Upcoming KOVAL tastings this week',
        'body' => $body,
        'in_reply_to' => SOURCE_MESSAGE_ID,
        'references' => SOURCE_MESSAGE_ID,
        'approval_gates' => $packet['approval_gates'],
        'verification_readback' => $verification,
        'output_channel' => 'email',
        'task_packet' => $packet,
    ]);
    record_task_flow($packet, 'ops_pioneer_updated_team_notified');
}

echo json_encode([
    'ok' => true,
    'event_ids' => array_map(static fn(array $row): int => (int) $row['id'], $events),
    'pioneer_flags' => array_map(static fn(array $row): int => (int) $row['is_pioneer_tasting'], $events),
    'campaign' => $campaign,
    'chat_status' => $chatStatus,
    'chat_message_recorded' => $chatMessageName !== '',
    'draft_queued' => $draftPath !== '' && is_file($draftPath),
    'proof_marker' => $proofMarker,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
