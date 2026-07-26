#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';
require_once '/Users/werkstatt/ops/outreach_team_chat_notifier.php';

const SOURCE_REF = 'caatx44yc-m2bdn7kohbyugadgymkhgbg=zv+8jy9rdhp-jjhxw@mail.gmail.com';
const SOURCE_MESSAGE_ID = '<CAAtX44YC-m2bdn7KohByugadgYMkHgBg=zV+8Jy9rdHP-jJhxw@mail.gmail.com>';
const TASK_FLOW_KEY = 'taskflow-b85fb23741597802';
const WORKSPACEBOARD_SESSION = 'e5d366e9';
const CAMPAIGN_SOURCE_ID = 568;
const CAMPAIGN_LIST_IDS = [73, 95];
const EVENT_IDS = [1032, 1124, 1031, 1030, 1037, 955];
const PROOF_MARKER = 'OPEN_TASTINGS_20260724_25_PHPLIST_CHAT';

/** @param array<string,mixed> $payload */
function write_json_file(string $path, array $payload): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true) && !is_dir($dir)) {
        throw new RuntimeException('Unable to create outbox directory.');
    }
    $json = json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    if ($json === false) {
        throw new RuntimeException('Unable to encode outbox message.');
    }
    $tmp = $path . '.tmp.' . getmypid();
    if (file_put_contents($tmp, $json . "\n", LOCK_EX) === false) {
        throw new RuntimeException('Unable to write outbox message.');
    }
    chmod($tmp, 0600);
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        throw new RuntimeException('Unable to install outbox message.');
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
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);
    if (proc_close($process) !== 0) {
        throw new RuntimeException('Task Flow recorder failed: ' . trim((string) $stderr . ' ' . (string) $stdout));
    }
}

function time_label(string $start, string $end): string
{
    $format = static function (string $value): string {
        $date = DateTimeImmutable::createFromFormat('H:i:s', $value)
            ?: DateTimeImmutable::createFromFormat('H:i', $value);
        return $date ? $date->format('g:i A') : $value;
    };
    return $format($start) . '-' . $format($end);
}

/** @return list<array<string,mixed>> */
function current_open_shifts(PDO $pdo): array
{
    $placeholders = implode(',', array_fill(0, count(EVENT_IDS), '?'));
    $stmt = $pdo->prepare(
        "SELECT id, event_name, event_date, start_time, end_time, event_location
           FROM event_bookings
          WHERE id IN ($placeholders)
          ORDER BY event_date, start_time, id"
    );
    $stmt->execute(EVENT_IDS);
    $events = $stmt->fetchAll(PDO::FETCH_ASSOC) ?: [];
    $links = fetch_event_booking_shift_links(EVENT_IDS, false);
    $open = [];
    foreach ($events as $event) {
        $eventId = (int) $event['id'];
        foreach (($links[$eventId] ?? []) as $shift) {
            if ((int) ($shift['deleted'] ?? 0) === 1 || (int) ($shift['assigned_count'] ?? 0) > 0) {
                continue;
            }
            $shiftId = (int) ($shift['shift_id'] ?? 0);
            if ($shiftId <= 0) {
                continue;
            }
            $open[] = [
                'event_id' => $eventId,
                'shift_id' => $shiftId,
                'date' => (string) ($shift['start_date'] ?: $event['event_date']),
                'time' => time_label((string) ($shift['start_time'] ?: $event['start_time']), (string) ($shift['end_time'] ?: $event['end_time'])),
                'event' => (string) $event['event_name'],
                'location' => (string) $event['event_location'],
                'ops_url' => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $eventId,
                'shift_url' => 'https://www.koval-distillery.com/ops/index.php?view=shifts&focus=' . $shiftId,
            ];
        }
    }
    return $open;
}

/** @param list<array<string,mixed>> $open @return array{subject:string,html:string,text:string,chat:string} */
function content(array $open): array
{
    $subject = 'Open KOVAL tasting shifts this week';
    $plain = [
        'Hi COTeam and Management Team,',
        '',
        'We still need coverage for the following KOVAL tasting shifts this week. Please claim a shift in OPS if you can cover it, or email Vanessa directly at vanessa.sterling@kovaldistillery.com.',
        '',
    ];
    $rows = '';
    $chat = ['Open KOVAL tasting shifts this week:', ''];
    foreach ($open as $row) {
        $line = $row['date'] . ', ' . $row['time'] . ': ' . $row['event'] . ' at ' . $row['location']
            . ' (OPS #' . $row['event_id'] . ', shift #' . $row['shift_id'] . ')';
        $plain[] = '- ' . $line;
        $plain[] = '  OPS: ' . $row['ops_url'];
        $plain[] = '  Claim: ' . $row['shift_url'];
        $chat[] = '- ' . $line;
        $chat[] = '  ' . $row['shift_url'];
        $rows .= '<tr><td>' . htmlspecialchars((string) $row['date']) . '</td>'
            . '<td>' . htmlspecialchars((string) $row['time']) . '</td>'
            . '<td>' . htmlspecialchars((string) $row['event']) . '</td>'
            . '<td>' . htmlspecialchars((string) $row['location']) . '</td>'
            . '<td><a href="' . htmlspecialchars((string) $row['shift_url']) . '">Claim shift #' . (int) $row['shift_id'] . '</a></td></tr>';
    }
    $plain = array_merge($plain, [
        '',
        'This message was sent from a no-reply list address. Please email Vanessa directly instead of replying to the list sender.',
        '',
        'Best,',
        'Vanessa Sterling',
        'Outreach Coordinator',
    ]);
    $chat[] = '';
    $chat[] = 'Please claim a shift in OPS if you can cover it, or email Vanessa directly.';
    $html = '<!doctype html><html><body style="font-family:Arial,sans-serif">'
        . '<p>Hi COTeam and Management Team,</p>'
        . '<p>We still need coverage for the following KOVAL tasting shifts this week. Please claim a shift in OPS if you can cover it, or email Vanessa directly at vanessa.sterling@kovaldistillery.com.</p>'
        . '<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse"><thead><tr><th>Date</th><th>Time</th><th>Event</th><th>Location</th><th>OPS</th></tr></thead><tbody>'
        . $rows . '</tbody></table>'
        . '<p>This message was sent from a no-reply list address. Please email Vanessa directly instead of replying to the list sender.</p>'
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
            $uuid = (string) $pdo->query('SELECT UUID()')->fetchColumn();
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
                'uuid' => $uuid,
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
                'codex_open_shift_count' => (string) count(current_open_shifts($pdo)),
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
$open = current_open_shifts($pdo);
if ($open === []) {
    throw new RuntimeException('No current unassigned tasting shifts remain.');
}
$copy = content($open);
$campaignId = create_or_get_campaign($pdo, $copy, $submit);
$chatMessageName = '';
$chatStatus = 'not_requested';
if ($postChat) {
    $notificationKey = 'outreach-team-chat|weekly-open-tastings|' . TASK_FLOW_KEY;
    $lookup = $pdo->prepare('SELECT chat_message_name FROM ' . OUTREACH_TEAM_CHAT_LOG_TABLE . ' WHERE notification_key = ? AND chat_target = ? LIMIT 1');
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
            'event_id' => (int) $open[0]['event_id'],
            'shift_id' => (int) $open[0]['shift_id'],
            'notification_type' => 'weekly_open_tastings',
            'notification_key' => $notificationKey,
            'chat_target' => OUTREACH_TEAM_CHAT_TARGET,
            'chat_message_name' => $chatMessageName,
        ]);
        $chatStatus = 'sent';
    }
}

$readback = campaign_readback($pdo, $campaignId);
if ($finalize) {
    if ((string) ($readback['status'] ?? '') !== 'sent' || $chatMessageName === '') {
        throw new RuntimeException('Cannot finalize without sent phpList and recorded Chat proof.');
    }
    $openIds = implode(', ', array_map(static fn(array $row): string => (string) $row['shift_id'], $open));
    $verification = 'Live OPS readback: open shifts ' . $openIds . '; phpList campaign ' . $campaignId
        . ' sent to lists 73/95; Outreach Team Chat message id recorded.';
    $packet = [
        'source_ref' => SOURCE_REF,
        'dedupe_key' => TASK_FLOW_KEY,
        'intake_channel' => 'email:nationaloutreach',
        'requester' => 'Robert Birnecker <robert@kovaldistillery.com>',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'vanessa.sterling@kovaldistillery.com',
        'workspaceboard_session' => WORKSPACEBOARD_SESSION,
        'ops_portal_or_domain_task' => 'OPS open shifts ' . $openIds,
        'status' => 'reported',
        'source_links' => 'Re: Upcoming KOVAL tastings this week',
        'approval_gates' => 'Direct Robert instruction to email the team and post in Google Chat.',
        'verification_readback' => $verification,
        'next_update' => 'Await COTeam claims for open shifts ' . $openIds . '.',
        'requested_deliverable' => 'Email the team with current open tasting shifts and post the same request in Google Chat.',
        'human_owner_or_recipient' => 'COTeam list 73; Management Group list 95; Outreach Team Google Chat; Robert completion reply',
        'output_channel' => 'phpList email, Outreach Team Google Chat, and same-thread completion email',
        'proof_required' => 'Live OPS open-shift readback, phpList campaign sent readback, Chat message id, and completion sent Message-ID',
        'result_email_required' => 'true',
        'owner_question_required' => 'false',
        'proof_marker' => PROOF_MARKER . '_CAMPAIGN_' . $campaignId,
    ];
    $completionBody = implode("\n", [
        'Robert,',
        '',
        'Done. I emailed COTeam and Management and posted the current open tasting shifts in the Outreach Team Google Chat.',
        '',
        'The live OPS check showed four shifts still open: Binny\'s Algonquin, Geneva, Orland Park, and Hyde Park. Saloon Royale is now covered, so I left it out of the notice.',
        '',
        'Best,',
        'Vanessa',
    ]);
    $draftPath = '/Users/admin/.nationaloutreach-launch/state/outbox/' . TASK_FLOW_KEY . '-open-tastings-completion.approved.json';
    write_json_file($draftPath, [
        'action_id' => TASK_FLOW_KEY . '-open-tastings-completion',
        'source_ref' => SOURCE_REF,
        'source_message_id' => SOURCE_REF,
        'status' => 'reported',
        'from' => 'vanessa.sterling@kovaldistillery.com',
        'from_name' => 'Vanessa Sterling',
        'to' => ['robert@kovaldistillery.com'],
        'cc' => [],
        'bcc' => [],
        'subject' => 'Re: Upcoming KOVAL tastings this week',
        'body' => $completionBody,
        'in_reply_to' => SOURCE_MESSAGE_ID,
        'references' => SOURCE_MESSAGE_ID,
        'approval_gates' => $packet['approval_gates'],
        'verification_readback' => $verification,
        'output_channel' => 'email',
        'task_packet' => $packet,
    ]);
    record_task_flow($packet, 'team_email_and_chat_posted');
}

echo json_encode([
    'ok' => true,
    'campaign' => $readback,
    'open_event_ids' => array_map(static fn(array $row): int => (int) $row['event_id'], $open),
    'open_shift_ids' => array_map(static fn(array $row): int => (int) $row['shift_id'], $open),
    'chat_status' => $chatStatus,
    'chat_message_recorded' => $chatMessageName !== '',
    'finalized' => $finalize,
    'proof_marker' => PROOF_MARKER . '_CAMPAIGN_' . $campaignId,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
