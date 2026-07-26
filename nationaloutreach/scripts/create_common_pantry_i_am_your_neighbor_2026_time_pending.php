<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

$pdo = get_event_pdo();

$eventName = 'Common Pantry I Am Your Neighbor Party 2026';
$eventDate = '2026-10-02';
$location = 'Artifact Events, 4325 N Ravenswood Ave, Chicago, IL 60613';
$accountId = 166237; // Common Pantry
$createdBy = 1332; // Codex
$eventHost = 1343; // Vanessa Sterling
$contactName = 'Lynn Hamill';
$contactEmail = 'lynn.c.hamill@gmail.com';
$contactPhone = '773.910.2311';

$notes = implode("\n", [
    'Source: Lynn Hamill email to Macee Maddox/National Outreach on 2026-06-21, subject "15 Years, 1,000 Neighbors and One Big Ask! - KOVAL DISTILLERY".',
    'Robert approved KOVAL participation on 2026-06-21 and asked Frank/National Outreach to put it on the outreach calendar, add an unassigned shift, and reply to Lynn with Sonat and Robert copied.',
    'Common Pantry requested KOVAL participation in the 15th annual I Am Your Neighbor Party at Artifact Events on Friday, October 2, 2026.',
    'Requested contribution: approximately 350 tasting-size portions for an expected crowd of over 1,000 guests.',
    'RSVP deadline in source email: July 1, 2026.',
    'Event time and vendor load-in/staffing window were not present in the cached source body or saved attachments. Vanessa reply asks Lynn for those details before creating the unassigned COTeam shift.',
]);

$important = 'Time pending. Create linked unassigned COTeam shift after Lynn confirms event hours and vendor load-in/staffing window.';

$pdo->beginTransaction();
try {
    $dupe = $pdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND (event_name LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupe->execute([$eventDate, '%Common Pantry%Neighbor%', '%Common Pantry%I Am Your Neighbor%']);
    $eventId = (int) ($dupe->fetchColumn() ?: 0);

    ensure_event_bookings_important_information_column($pdo);
    ensure_event_bookings_max_capacity_column($pdo);
    ensure_event_bookings_pioneer_flag_column($pdo);

    if ($eventId > 0) {
        $stmt = $pdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = NULL, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = NULL, end_time = NULL,
                    contact_name = ?, contact_email = ?, contact_phone = ?, estimated_guest_count = ?,
                    notes = ?, important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $stmt->execute([
            $eventName,
            $eventDate,
            'Outreach',
            $location,
            $accountId,
            $contactName,
            $contactEmail,
            $contactPhone,
            1000,
            $notes,
            $important,
            $eventHost,
            $eventId,
        ]);
    } else {
        $stmt = $pdo->prepare(
            'INSERT INTO event_bookings (
                event_name, event_date, event_end_date, event_category, event_location,
                distributor_account_id, start_time, end_time, contact_name, contact_email,
                contact_phone, amount_paid, estimated_guest_count, actual_guest_count, max_capacity,
                notes, important_information, is_pioneer_tasting, rooms, google_drive_link,
                created_by, event_host_user_id
            ) VALUES (?, ?, NULL, ?, ?, ?, NULL, NULL, ?, ?, ?, 0, ?, NULL, NULL, ?, ?, 0, NULL, NULL, ?, ?)'
        );
        $stmt->execute([
            $eventName,
            $eventDate,
            'Outreach',
            $location,
            $accountId,
            $contactName,
            $contactEmail,
            $contactPhone,
            1000,
            $notes,
            $important,
            $createdBy,
            $eventHost,
        ]);
        $eventId = (int) $pdo->lastInsertId();
    }

    $accountExists = $pdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id = ? AND account_id = ? LIMIT 1');
    $accountExists->execute([$eventId, $accountId]);
    if (!$accountExists->fetchColumn()) {
        $insertAccount = $pdo->prepare('INSERT INTO event_booking_accounts (event_booking_id, account_id) VALUES (?, ?)');
        $insertAccount->execute([$eventId, $accountId]);
    }

    $pdo->commit();

    $readback = $pdo->prepare(
        "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
                eb.event_location, eb.distributor_account_id, eb.contact_name, eb.contact_email,
                eb.estimated_guest_count, eb.important_information,
                COUNT(l.shift_id) AS linked_shift_count
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
          WHERE eb.id = ?
          GROUP BY eb.id"
    );
    $readback->execute([$eventId]);
    echo json_encode($readback->fetch(PDO::FETCH_ASSOC), JSON_PRETTY_PRINT) . "\n";
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}
