<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

function cff_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid shift date.');
    }
    return (int) date('N', $timestamp);
}

$eventName = 'CFF Corks & Kegs 2026';
$eventDate = '2026-11-20';
$eventStart = '18:00';
$eventEnd = '23:00';
$shiftStart = '16:30';
$shiftEnd = '23:00';
$location = 'Artifact Events, 4325 N Ravenswood Ave, Chicago, IL 60613';
$accountId = 5652; // Cystic Fibrosis Foundation
$createdBy = 1332; // Codex
$eventHost = 1343; // Vanessa Sterling
$cotGroupId = 169; // COTeam
$contactName = 'Emily Hanna';
$contactEmail = 'ehanna@cff.org';
$contactPhone = '218.393.0550';
$notes = implode("\n", [
    'Source: Robert Birnecker email to Vanessa Sterling on 2026-05-26, subject "Fwd: CFF Corks & Kegs 2026".',
    'Robert approved KOVAL participation and requested: confirm with Emily, add OPS event, add unassigned shift, and add notes.',
    'Event: Cystic Fibrosis Foundation Corks & Kegs 2026 at Artifact Events on Friday, November 20, 2026.',
    'Expected attendance: approximately 350 guests; live music, vendors, fall CFF fundraisers, and event celebration.',
    'Vendor timeline from 2026 vendor form: brewer/vendor arrival 4:30 PM-5:00 PM; doors/VIP admission 6:00 PM; general admission 7:00 PM; last call 10:45 PM; event end 11:00 PM.',
    'Vendor requirements from form: enough product for 350 guests at 3 oz samples each; for hard liquor, CFF recommends a batch cocktail highlighting the spirit; one or more employees to serve product; delivery, table presentation, and removal of leftovers are vendor responsibility.',
    'Provided by CFF: one 6 ft table with black cloth, tasting glasses, ice and electrical outlets upon request, social media recognition, event-material recognition. CFF can provide servers if notified by October 2, 2026.',
    'Required documents: Alcohol Service Form; COI listing Nevermore Events, LLC, 4325 N Ravenswood Ave, Chicago, IL 60613; COI listing Cystic Fibrosis Foundation, 4550 Montgomery Ave. Suite 1100 N., Bethesda, MD 20814.',
    'Vendor form: https://afasignup.formstack.com/forms/corksandkegs_vendor_copy',
    'Vendor landing page: https://pages.e2ma.net/pages/1799972/57279',
    'External contacts: Emily Hanna <ehanna@cff.org>; Averey Den Hartog <adenhartog@cff.org>.',
]);

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();

try {
    $dupeStmt = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND (event_name = ? OR event_name LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$eventDate, $eventName, '%Corks & Kegs%', '%Corks & Kegs%']);
    $existingId = (int) ($dupeStmt->fetchColumn() ?: 0);

    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);

    if ($existingId > 0) {
        $eventId = $existingId;
        $updateEvent = $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = ?, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                    contact_name = ?, contact_email = ?, contact_phone = ?, estimated_guest_count = ?,
                    notes = ?, important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $updateEvent->execute([
            $eventName,
            $eventDate,
            null,
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            $contactName,
            $contactEmail,
            $contactPhone,
            350,
            $notes,
            'Unassigned COTeam shift should cover vendor arrival/setup through event end: 4:30 PM-11:00 PM.',
            $eventHost,
            $eventId,
        ]);
    } else {
        $insertEvent = $eventPdo->prepare(
            'INSERT INTO event_bookings (
                event_name, event_date, event_end_date, event_category, event_location, distributor_account_id,
                start_time, end_time, contact_name, contact_email, contact_phone, amount_paid,
                estimated_guest_count, actual_guest_count, max_capacity, notes, important_information,
                is_pioneer_tasting, rooms, google_drive_link, created_by, event_host_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        );
        $insertEvent->execute([
            $eventName,
            $eventDate,
            null,
            'Outreach',
            $location,
            $accountId,
            $eventStart,
            $eventEnd,
            $contactName,
            $contactEmail,
            $contactPhone,
            0,
            350,
            null,
            null,
            $notes,
            'Unassigned COTeam shift should cover vendor arrival/setup through event end: 4:30 PM-11:00 PM.',
            0,
            null,
            null,
            $createdBy,
            $eventHost,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    $accountExists = $eventPdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id = ? AND account_id = ? LIMIT 1');
    $accountExists->execute([$eventId, $accountId]);
    if (!$accountExists->fetchColumn()) {
        $insertAccount = $eventPdo->prepare(
            'INSERT INTO event_booking_accounts (event_booking_id, account_id) VALUES (?, ?)'
        );
        $insertAccount->execute([$eventId, $accountId]);
    }

    ensure_event_shift_links_table($eventPdo);
    $shiftLookup = $eventPdo->prepare(
        'SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1'
    );
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    if ($shiftId > 0) {
        $updateShift = $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = ?, activity_id = 0, updated_by = ?
              WHERE id = ?"
        );
        $updateShift->execute([
            cff_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $shiftStart,
            $shiftEnd,
            'Outreach: CFF Corks & Kegs 2026 - unassigned setup/event coverage',
            $cotGroupId,
            $accountId,
            $createdBy,
            $shiftId,
        ]);
        $trackPdo->prepare("DELETE FROM " . TRACKTIME_DB_NAME . ".shift2user WHERE shift_id = ?")->execute([$shiftId]);
    } else {
        $insertShift = $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, 0, ?, ?)"
        );
        $insertShift->execute([
            cff_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $shiftStart,
            $shiftEnd,
            'Outreach: CFF Corks & Kegs 2026 - unassigned setup/event coverage',
            $cotGroupId,
            $accountId,
            $createdBy,
            $createdBy,
        ]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $linkStmt = $eventPdo->prepare(
            'INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by)
             VALUES (?, ?, ?)'
        );
        $linkStmt->execute([$eventId, $shiftId, $createdBy]);
    }

    if ($trackPdo->inTransaction()) {
        $trackPdo->commit();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }

    $readback = $eventPdo->prepare(
        "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
                eb.event_location, eb.estimated_guest_count, eb.contact_name, eb.contact_email,
                l.shift_id, s.start_time AS shift_start, s.end_time AS shift_end, s.group_id,
                COUNT(s2u.user_id) AS assigned_users
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
          WHERE eb.id = ?
          GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id"
    );
    $readback->execute([$eventId]);
    echo json_encode($readback->fetch(PDO::FETCH_ASSOC), JSON_PRETTY_PRINT) . "\n";
} catch (Throwable $e) {
    if ($trackPdo->inTransaction()) {
        $trackPdo->rollBack();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}
