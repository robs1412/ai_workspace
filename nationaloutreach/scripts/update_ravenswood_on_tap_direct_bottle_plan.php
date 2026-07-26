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

function normalize_direct_bottle_plan(string $existing): string
{
    return str_replace(
        'Amy/RNDC bottle order via Taylor',
        'Direct KOVAL bottle sale/delivery coordination pending; do not use RNDC/Taylor',
        $existing
    );
}

$eventIds = [866, 867];
$noteLine = '2026-06-26 Sonat correction: RNDC will not be able to deliver the KOVAL bottles for Ravenswood On Tap. KOVAL/Vanessa needs to coordinate selling the bottles directly instead of assuming RNDC delivery.';
$infoLine = 'Bottle plan updated 2026-06-26: RNDC will not deliver KOVAL bottles; KOVAL/Vanessa must coordinate direct bottle sales.';

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
        $notes = append_once(normalize_direct_bottle_plan((string) ($row['notes'] ?? '')), $noteLine);
        $info = append_once(normalize_direct_bottle_plan((string) ($row['important_information'] ?? '')), $infoLine);
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
    'SELECT id, event_name, event_date, start_time, end_time, event_location, important_information
       FROM event_bookings
      WHERE id IN (866, 867)
      ORDER BY event_date, id'
);

echo json_encode([
    'ok' => true,
    'updated_event_ids' => $eventIds,
    'ops_urls' => array_map(static fn (int $id): string => 'https://www.koval-distillery.com/ops/index.php?view=outreach_detail&id=' . $id, $eventIds),
    'readback' => $stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : [],
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
