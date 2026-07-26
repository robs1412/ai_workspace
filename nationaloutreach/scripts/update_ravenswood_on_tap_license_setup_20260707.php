#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

function append_once(string $existing, string $line): string
{
    $existing = trim($existing);
    if ($existing !== '' && str_contains($existing, $line)) {
        return $existing;
    }
    return trim($existing . ($existing !== '' ? "\n\n" : '') . $line);
}

$eventIds = [866, 867];
$sourceMessageId = '<DM6PR12MB430074F213B9F7B216691134BDF02@DM6PR12MB4300.namprd12.prod.outlook.com>';
$noteLine = '2026-07-07 Amy sent the special event liquor license to Sebastian after the CRT-61 form, and Sebastian told Amy KOVAL will set the account up and follow up soon regarding the ordering process. Source Message-ID ' . $sourceMessageId . '.';
$infoLine = '2026-07-07 license/CRT-61 update: Sebastian has the special event liquor license and CRT-61; account setup/direct bottle ordering follow-up is with Sebastian/Amy. No separate Vanessa outreach reply needed for Amy\'s acknowledgement.';

$pdo = get_event_pdo();
ensure_event_bookings_important_information_column($pdo);

$pdo->beginTransaction();
try {
    $select = $pdo->prepare('SELECT id, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $update = $pdo->prepare('UPDATE event_bookings SET notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');

    foreach ($eventIds as $eventId) {
        $select->execute([$eventId]);
        $row = $select->fetch(PDO::FETCH_ASSOC);
        if (!is_array($row)) {
            throw new RuntimeException('OPS event ' . $eventId . ' was not found.');
        }
        $notes = append_once((string) ($row['notes'] ?? ''), $noteLine);
        $info = append_once((string) ($row['important_information'] ?? ''), $infoLine);
        $update->execute([$notes, $info, $eventId]);
    }

    $pdo->commit();
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$stmt = $pdo->query(
    'SELECT id, event_name, event_date, start_time, end_time, event_location, contact_name, contact_email, important_information, updated_at
       FROM event_bookings
      WHERE id IN (866, 867)
      ORDER BY event_date, id'
);

echo json_encode([
    'ok' => true,
    'updated_event_ids' => $eventIds,
    'source_message_id' => $sourceMessageId,
    'ops_urls' => array_map(static fn (int $id): string => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $id, $eventIds),
    'readback' => $stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : [],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
