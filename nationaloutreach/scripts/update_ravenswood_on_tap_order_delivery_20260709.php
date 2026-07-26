#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

function append_once_line(string $existing, string $line): string
{
    $existing = trim($existing);
    if ($existing !== '' && str_contains($existing, $line)) {
        return $existing;
    }
    return trim($existing . ($existing !== '' ? "\n\n" : '') . $line);
}

$eventIds = [866, 867];
$sourceMessageId = '<DM6PR12MB43001A1B9C9A93B62647E2F7BDFE2@DM6PR12MB4300.namprd12.prod.outlook.com>';
$noteLine = '2026-07-09 Amy/Ravenswood order detail: Amy confirmed check payment after the event; order request is 25 cases Bourbon and 25 cases Cranberry Gin. Preferred delivery is Wednesday 2026-07-15 between 9:00am and 10:00am to 1770 W Berteau Ave Suite 101, Chicago, IL 60613. Amy can return unopened cases/bottles Tuesday after the event because their office is closed Monday. Source Message-ID ' . $sourceMessageId . '.';
$infoLine = '2026-07-09 direct bottle order details received: 25 cases Bourbon + 25 cases Cranberry Gin; check after event; preferred delivery Wed 2026-07-15 9:00-10:00am to 1770 W Berteau Ave Suite 101; unopened returns Tuesday after event. Coordinate fulfillment with Sebastian/Amy.';

$pdo = get_event_pdo();
ensure_event_bookings_important_information_column($pdo);

$pdo->beginTransaction();
try {
    $select = $pdo->prepare('SELECT id, event_name, event_date, notes, important_information FROM event_bookings WHERE id = ? FOR UPDATE');
    $update = $pdo->prepare('UPDATE event_bookings SET notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');

    foreach ($eventIds as $eventId) {
        $select->execute([$eventId]);
        $row = $select->fetch(PDO::FETCH_ASSOC);
        if (!is_array($row)) {
            throw new RuntimeException('OPS event ' . $eventId . ' was not found.');
        }

        $notes = append_once_line((string) ($row['notes'] ?? ''), $noteLine);
        $info = append_once_line((string) ($row['important_information'] ?? ''), $infoLine);
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
    'SELECT id, event_name, event_date, start_time, end_time, event_location, important_information, updated_at
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
