#!/usr/bin/env php
<?php
declare(strict_types=1);

function arg_value(array $argv, string $name, ?string $default = null): ?string
{
    foreach ($argv as $idx => $arg) {
        if ($arg === $name && isset($argv[$idx + 1])) {
            return (string) $argv[$idx + 1];
        }
        if (str_starts_with($arg, $name . '=')) {
            return substr($arg, strlen($name) + 1);
        }
    }
    return $default;
}

function load_jsonl_rows(string $path): array
{
    if (!is_file($path)) {
        return [];
    }
    $rows = [];
    foreach ((file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: []) as $line) {
        $row = json_decode($line, true);
        if (is_array($row)) {
            $rows[] = $row;
        }
    }
    return $rows;
}

function write_jsonl_rows(string $path, array $rows): void
{
    $dir = dirname($path);
    if (!is_dir($dir)) {
        mkdir($dir, 0700, true);
    }
    $tmp = $path . '.tmp';
    $payload = '';
    foreach ($rows as $row) {
        $payload .= json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
    }
    file_put_contents($tmp, $payload);
    chmod($tmp, 0600);
    rename($tmp, $path);
    chmod($path, 0600);
}

function sync_scheduled_actions_db(array $rows, string $mailboxLane = 'nationaloutreach'): void
{
    $recorder = '/Users/werkstatt/ai_workspace/scripts/scheduled_actions_mysql_recorder.php';
    if (!is_file($recorder) || $rows === []) {
        return;
    }
    $payload = json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    if ($payload === false) {
        return;
    }
    $tmp = tempnam(sys_get_temp_dir(), 'sched-actions-');
    if ($tmp === false) {
        return;
    }
    file_put_contents($tmp, $payload);
    $cmd = 'php ' . escapeshellarg($recorder) . ' upsert ' . escapeshellarg($mailboxLane)
        . ' < ' . escapeshellarg($tmp) . ' >/dev/null 2>/dev/null';
    exec($cmd);
    @unlink($tmp);
}

function normalize_ref(string $value): string
{
    return strtolower(trim($value));
}

function coteam_bcc_recipients(): array
{
    return [
        'abbiejbrenner@gmail.com',
        'benngoodman@gmail.com',
        'chayarsmolensky@gmail.com',
        'christina.pinciotti@gmail.com',
        'christine.cummins37@gmail.com',
        'clwilander@gmail.com',
        'darla.swango@kovaldistillery.com',
        'dereck.atwater@kovaldistillery.com',
        'dylancollinsgphs@gmail.com',
        'gabriele.thormann99@gmail.com',
        'jth2d@hotmail.com',
        'julie.feyerer@kovaldistillery.com',
        'kmccarthy1991@gmail.com',
        'kyle.combs@kovaldistillery.com',
        'lsargent313@gmail.com',
        'matt.andrews@kovaldistillery.com',
        'mattdevens22@icloud.com',
        'sarahelizabethwelford@gmail.com',
        'sddulman@gmail.com',
        'sebastian.saller@kovaldistillery.com',
        'sonat@kovaldistillery.com',
        'stephen.desena@gmail.com',
    ];
}

function mitch_facing_payload(DateTimeImmutable $monday): array
{
    $cmd = [
        'php',
        '/Users/werkstatt/ai_workspace/nationaloutreach/scripts/build_mitch_weekly_report.php',
        '--start',
        $monday->format('Y-m-d'),
    ];
    $descriptor = [
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];
    $proc = proc_open($cmd, $descriptor, $pipes);
    if (!is_resource($proc)) {
        throw new RuntimeException('Could not start Mitch report generator.');
    }
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    $exit = proc_close($proc);
    if ($exit !== 0) {
        throw new RuntimeException('Mitch report generator failed: ' . trim((string) $stderr));
    }
    $payload = json_decode((string) $stdout, true, flags: JSON_THROW_ON_ERROR);
    $body = str_replace(
        "Hi Robert,\n\nDraft for approval: this is the current weekly upcoming tastings report for Mitch Conti. It has not been sent to Mitch.\n\nSummary:",
        "Hi Mitch,\n\nHere is this week's upcoming KOVAL tasting schedule.\n\nSummary:",
        (string) ($payload['body'] ?? '')
    );
    $body = str_replace(
        'Use Product / sample prep when reminding staff what products the account appears to carry and what samples/materials to bring.',
        'Open, partially assigned, or missing linked-shift rows are highlighted in the HTML version. The Product / sample prep column is included so the team can see what products the account appears to carry and what samples/materials to bring.',
        $body
    );
    $html = str_replace(
        '<p>Hi Robert,</p><p>Draft for approval: this is the current weekly upcoming tastings report for Mitch Conti. It has not been sent to Mitch.</p>',
        "<p>Hi Mitch,</p><p>Here is this week's upcoming KOVAL tasting schedule.</p>",
        (string) ($payload['html_body'] ?? '')
    );
    return [
        'from' => 'vanessa.sterling@kovaldistillery.com',
        'from_name' => 'Vanessa Sterling',
        'to' => ['Mitch.Conti@rndc-usa.com'],
        'cc' => ['robert@kovaldistillery.com'],
        'bcc' => coteam_bcc_recipients(),
        'subject' => 'Upcoming KOVAL tastings this week',
        'body' => $body,
        'html_body' => $html,
    ];
}

$dateRaw = arg_value($argv, '--date', date('Y-m-d'));
$stateDir = rtrim((string) arg_value($argv, '--state-dir', '/Users/admin/.nationaloutreach-launch/state'), '/');
$date = DateTimeImmutable::createFromFormat('Y-m-d', (string) $dateRaw);
if (!$date || $date->format('Y-m-d') !== $dateRaw) {
    fwrite(STDERR, "Invalid --date. Use YYYY-MM-DD.\n");
    exit(2);
}
$monday = $date->modify('monday this week');
if ($date->format('N') !== '1') {
    $monday = $date->modify('next monday');
}
$stateDir = $stateDir !== '' ? $stateDir : '/Users/admin/.nationaloutreach-launch/state';
if (!is_dir($stateDir)) {
    mkdir($stateDir, 0700, true);
}

$scheduledPath = $stateDir . '/scheduled-actions.jsonl';
$scheduledRows = load_jsonl_rows($scheduledPath);
$existingRefs = [];
foreach ($scheduledRows as $row) {
    $sourceRef = (string) ($row['source_ref'] ?? $row['id'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[normalize_ref($sourceRef)] = true;
    }
}
foreach (load_jsonl_rows($stateDir . '/sent-log.jsonl') as $row) {
    $taskPacket = is_array($row['task_packet'] ?? null) ? $row['task_packet'] : [];
    $sourceRef = (string) ($taskPacket['source_ref'] ?? $row['source_ref'] ?? '');
    if ($sourceRef !== '') {
        $existingRefs[normalize_ref($sourceRef)] = true;
    }
}

$sourceRef = 'vanessa-mitch-weekly-direct-' . $monday->format('Y-m-d') . '-0800';
$queued = 0;
$skipped = 0;
$rowsForDbSync = [];
if (!isset($existingRefs[normalize_ref($sourceRef)])) {
    $payload = mitch_facing_payload($monday);
    $payload['source_ref'] = $sourceRef;
    $payload['task_packet'] = [
        'source_ref' => $sourceRef,
        'dedupe_key' => 'taskflow-' . $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'ops_portal_or_domain_task' => 'OPS 367856',
        'status' => 'reported',
        'requested_deliverable' => 'Monday 8 AM Mitch Conti weekly upcoming tasting report, Robert copied, COTeam BCC.',
        'human_owner_or_recipient' => 'Mitch Conti; Robert copied; COTeam BCC',
        'output_channel' => 'email',
        'proof_required' => 'sent Message-ID plus sent-log recipient counts',
        'verification_readback' => 'Generated from live OPS Outreach schedule for week starting ' . $monday->format('Y-m-d') . '.',
        'papers_projection' => 'not_required',
        'next_update' => 'Pending Monday 8:00 AM scheduled-action queue for approved send cycle.',
    ];
    $newRow = [
        'id' => $sourceRef,
        'kind' => 'mitch_weekly_report_direct',
        'status' => 'pending',
        'ops_task_id' => 367856,
        'due_at' => $monday->format('Y-m-d') . 'T08:00:00-05:00',
        'owner' => 'Robert Birnecker',
        'worker' => 'Vanessa Sterling',
        'dependency' => 'Monday 8 AM Mitch weekly upcoming tastings report direct send',
        'resolution_checks' => [],
        'email' => $payload,
        'source_ref' => $sourceRef,
        'intake_channel' => 'scheduled-action:nationaloutreach',
        'requester' => 'Robert Birnecker',
        'owner_lane' => 'outreach-coordinator',
        'responsible_worker_or_persona' => 'Vanessa Sterling',
        'source_links' => 'OPS task 367856',
        'approval_gates' => 'Approved recurring Monday direct send; Robert cc required.',
        'verification_readback' => 'Generated from live OPS Outreach schedule.',
        'papers_projection' => 'not_applicable',
        'next_update' => 'Pending Monday 8:00 AM scheduled-action queue for approved send cycle.',
        'report_start' => $monday->format('Y-m-d'),
    ];
    $scheduledRows[] = $newRow;
    $rowsForDbSync[] = $newRow;
    $queued = 1;
} else {
    $skipped = 1;
}

write_jsonl_rows($scheduledPath, $scheduledRows);
sync_scheduled_actions_db($rowsForDbSync);

echo json_encode([
    'ok' => true,
    'date' => $date->format('Y-m-d'),
    'report_start' => $monday->format('Y-m-d'),
    'source_ref' => $sourceRef,
    'queued' => $queued,
    'skipped' => $skipped,
], JSON_UNESCAPED_SLASHES) . "\n";
