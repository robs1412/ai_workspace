#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function bdg_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid shift date.');
    }
    return (int) date('N', $timestamp);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventName = "Binny's Downers Grove Midwest Whiskey Event";
$eventDate = '2026-07-18';
$eventStart = '13:00';
$eventEnd = '15:00';
$location = "Binny's Downers Grove, 2010 Butterfield Rd., Downers Grove, IL 60515";
$createdBy = 1332; // Codex
$eventHost = 1343; // Vanessa Sterling
$cotGroupId = 169; // COTeam
$contactName = 'Rob Weekley';
$contactEmail = 'rweekley@binnys.com';
$contactPhone = '224-491-6156';
$sourceMessageId = '<DS5PR13MB765371A7C1412059B4849DAFAA132@DS5PR13MB7653.namprd13.prod.outlook.com>';
$notes = implode("\n", [
    'Source: Rob Weekley email, subject "Binny\'s Downers Grove - Midwest Whiskey Event - 7/18/26", Message-ID ' . $sourceMessageId . '.',
    "Binny's Downers Grove team is hosting a walkaround whiskey event and asked KOVAL to be one of the showcased distilleries.",
    'Source details: Location: Downers Grove; Date: 2026-07-18; Time: 1:00 PM-3:00 PM.',
    'Coordination requested with the Downers Grove team copied on the source email.',
]);
$importantInformation = 'Unassigned COTeam coverage needed for Binny\'s Downers Grove Midwest Whiskey Event, 1:00 PM-3:00 PM. Product/setup details still to be coordinated with Binny\'s.';

$eventPdo->beginTransaction();
$trackPdo->beginTransaction();

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupeStmt = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND (event_name = ? OR event_name LIKE ? OR event_location LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([$eventDate, $eventName, '%Downers Grove%Whiskey%', '%Downers Grove%', '%' . $sourceMessageId . '%']);
    $eventId = (int) ($dupeStmt->fetchColumn() ?: 0);

    if ($eventId > 0) {
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
            null,
            $eventStart,
            $eventEnd,
            $contactName,
            $contactEmail,
            $contactPhone,
            null,
            $notes,
            $importantInformation,
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
            null,
            $eventStart,
            $eventEnd,
            $contactName,
            $contactEmail,
            $contactPhone,
            0,
            null,
            null,
            null,
            $notes,
            $importantInformation,
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

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
    $shiftLookup->execute([$eventId]);
    $shiftId = (int) ($shiftLookup->fetchColumn() ?: 0);
    $shiftNotes = "Outreach: Binny's Downers Grove Midwest Whiskey Event - unassigned COTeam coverage";

    if ($shiftId > 0) {
        $updateShift = $trackPdo->prepare(
            "UPDATE " . TRACKTIME_DB_NAME . ".shifts
                SET week_day_id = ?, start_date = ?, end_date = ?, start_time = ?, end_time = ?,
                    notes = ?, group_id = ?, account_id = 0, activity_id = 0, updated_by = ?
              WHERE id = ?"
        );
        $updateShift->execute([
            bdg_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
            $createdBy,
            $shiftId,
        ]);
        $trackPdo->prepare("DELETE FROM " . TRACKTIME_DB_NAME . ".shift2user WHERE shift_id = ?")->execute([$shiftId]);
    } else {
        $insertShift = $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
                (week_day_id, start_date, end_date, start_time, end_time, notes, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)"
        );
        $insertShift->execute([
            bdg_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $eventStart,
            $eventEnd,
            $shiftNotes,
            $cotGroupId,
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
        "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time,
                eb.event_category, eb.event_location, eb.contact_name, eb.contact_email,
                eb.contact_phone, eb.event_host_user_id, l.shift_id,
                s.start_time AS shift_start, s.end_time AS shift_end, s.group_id,
                COUNT(s2u.user_id) AS assigned_users
           FROM event_bookings eb
           LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
           LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
          WHERE eb.id = ?
          GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id"
    );
    $readback->execute([$eventId]);
    echo json_encode($readback->fetch(PDO::FETCH_ASSOC), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
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
