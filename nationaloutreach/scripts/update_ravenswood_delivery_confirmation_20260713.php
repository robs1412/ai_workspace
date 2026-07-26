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
$sourceMessageId = '<DM6PR12MB43002C5F60E88BE7F403F682BDFA2@DM6PR12MB4300.namprd12.prod.outlook.com>';
$marker = 'RAVENSWOOD_DELIVERY_CONFIRMED_20260715_0930_LOADING_DOCK';
$noteLine = '2026-07-13 delivery confirmation: Amy confirmed Mark\'s Wednesday 2026-07-15 9:30am delivery time and will meet the delivery at the loading dock. No Vanessa reply needed because Amy\'s message is the final acknowledgement on Mark\'s logistics thread. Source Message-ID ' . $sourceMessageId . '. Marker ' . $marker . '.';
$infoLine = 'Delivery confirmed: Wed 2026-07-15 at 9:30am via the loading dock; Amy will meet the delivery there. Marker ' . $marker . '.';

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
        $important = append_once((string) ($row['important_information'] ?? ''), $infoLine);
        $update->execute([$notes, $important, $eventId]);
    }

    $pdo->commit();
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$verify = $pdo->prepare(
    'SELECT id, event_name, event_date, updated_at,
            notes LIKE ? AS notes_has_marker,
            important_information LIKE ? AS important_has_marker
       FROM event_bookings
      WHERE id IN (866, 867)
      ORDER BY id'
);
$like = '%' . $marker . '%';
$verify->execute([$like, $like]);

echo json_encode([
    'ok' => true,
    'marker' => $marker,
    'source_message_id' => $sourceMessageId,
    'ops_urls' => array_map(static fn (int $id): string => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $id, $eventIds),
    'readback' => $verify->fetchAll(PDO::FETCH_ASSOC),
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
