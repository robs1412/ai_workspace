#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

$eventId = 902;
$sourceMessageId = '<CALbLtzzOi3n2JGH1m_ebfVKrcXLFbBBFJFAB9TkRfrJJfNJAbQ@mail.gmail.com>';
$sourceMarker = 'Day-of logistics update from Sullivan Anderson email on 2026-06-04, Message-ID ' . $sourceMessageId . '.';
$details = implode("\n", [
    $sourceMarker,
    'Event date/location: Tuesday, June 30, 2026 at Chicago Shakespeare Theater, 800 E Grand Ave, Chicago, IL 60611.',
    'Audience: approximately 300 business leaders, innovators, entrepreneurs, educators, and civic leaders.',
    'Food and beverage exhibitor setup window: 4:00 PM-6:00 PM in the Courtyard reception area. Set up earlier if the representative will attend the seated program.',
    'Program timeline: 5:00 PM-5:20 PM exhibitor move to Yard Theater if attending seated program; 5:00 PM-5:30 PM guest check-in/seating; 5:30 PM-6:30 PM seated program; 6:15 PM early dismissal for exhibitors; 6:30 PM panel release; 6:30 PM-8:00 PM networking reception and exhibitor showcase.',
    'Arrival/load-in: follow signs for Chicago Shakespeare Theater; Courtyard reception area is just past the main theater entrance near the box office. Box office contact for guidance: 312.595.5600. Loading dock must be scheduled ahead and is first-come-first-served.',
    'Venue provides a 6-foot table and linen. KOVAL may bring branded linen. Venue cannot provide kitchen/prep space; samples should arrive prepared or be table-prep ready. Cart and electrical outlet are not guaranteed; bring extension cords if power is essential.',
    'Registration: table representative receives one complimentary full-event ticket; reply to Sullivan with representative name, title, and email. Five additional complimentary team tickets are available with promo code EcoPartnerCompTix on the registration page. Ticket redemption deadline: Tuesday, June 23, 2026.',
]);

$pdo = get_event_pdo();
$stmt = $pdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, notes, important_information FROM event_bookings WHERE id = ?');
$stmt->execute([$eventId]);
$event = $stmt->fetch(PDO::FETCH_ASSOC);
if (!is_array($event)) {
    fwrite(STDERR, "Event {$eventId} not found.\n");
    exit(1);
}

$notes = trim((string) ($event['notes'] ?? ''));
$important = trim((string) ($event['important_information'] ?? ''));

$updatedNotes = str_contains($notes, $sourceMessageId)
    ? $notes
    : trim($notes . "\n\n" . $details);
$updatedImportant = str_contains($important, $sourceMessageId)
    ? $important
    : trim($important . "\n\nDay-of OPS note: setup 4:00 PM-6:00 PM; reception/showcase 6:30 PM-8:00 PM; table rep registration and 5 comp team tickets due by Tuesday, June 23, 2026. See notes for full Sullivan logistics. Source Message-ID " . $sourceMessageId);

$update = $pdo->prepare('UPDATE event_bookings SET notes = ?, important_information = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?');
$update->execute([$updatedNotes, $updatedImportant, $eventId]);

$verify = $pdo->prepare('SELECT id, event_name, event_date, start_time, end_time, event_location, notes LIKE ? AS notes_has_marker, important_information LIKE ? AS important_has_marker FROM event_bookings WHERE id = ?');
$like = '%' . $sourceMessageId . '%';
$verify->execute([$like, $like, $eventId]);
$row = $verify->fetch(PDO::FETCH_ASSOC);

echo json_encode([
    'ok' => true,
    'event_id' => $eventId,
    'event_name' => $row['event_name'] ?? '',
    'event_date' => $row['event_date'] ?? '',
    'start_time' => $row['start_time'] ?? '',
    'end_time' => $row['end_time'] ?? '',
    'event_location' => $row['event_location'] ?? '',
    'notes_has_source_marker' => (bool) ($row['notes_has_marker'] ?? false),
    'important_has_source_marker' => (bool) ($row['important_has_marker'] ?? false),
    'proof_marker' => 'OPS_EVENT_902_DAY_OF_DETAILS_MESSAGE_CALbLtzzOi3n2JGH1m_20260604',
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
