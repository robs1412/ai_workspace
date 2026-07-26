#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function common_pantry_week_day_id(string $date): int
{
    $timestamp = strtotime($date);
    if ($timestamp === false) {
        throw new RuntimeException('Invalid event date.');
    }
    return (int) date('N', $timestamp);
}

function common_pantry_google_token_user_id(PDO $pdo): ?int
{
    google_oauth_tokens_table_ready($pdo);
    $stmt = $pdo->query('SELECT user_id FROM ops_google_oauth_tokens ORDER BY updated_at DESC');
    foreach (($stmt ? $stmt->fetchAll(PDO::FETCH_ASSOC) : []) as $row) {
        $candidate = (int) ($row['user_id'] ?? 0);
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            return $candidate;
        }
    }
    return null;
}

function common_pantry_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $pdo->exec("CREATE TABLE IF NOT EXISTS event_booking_google_links (
        event_booking_id INT NOT NULL,
        google_event_uid VARCHAR(255) NOT NULL,
        calendar_type VARCHAR(32) NOT NULL DEFAULT 'events',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (event_booking_id),
        UNIQUE KEY ux_event_booking_google_uid (google_event_uid),
        CONSTRAINT fk_event_booking_google_links_event FOREIGN KEY (event_booking_id) REFERENCES event_bookings(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");

    $pdo->prepare('DELETE FROM event_booking_google_links WHERE google_event_uid = ? AND event_booking_id <> ?')->execute([$uid, $eventId]);
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'outreach']);
}

$eventPdo = get_event_pdo();
$trackPdo = get_tracktime_pdo();

$eventId = 1063;
$eventName = 'Common Pantry I Am Your Neighbor Party 2026';
$eventDate = '2026-10-02';
$eventStart = '19:00';
$eventEnd = '23:00';
$shiftStart = '17:00';
$shiftEnd = '24:00';
$location = 'Artifact Events, 4325 N Ravenswood Ave, Chicago, IL 60613';
$accountId = 166237; // Common Pantry
$createdBy = 1332; // Codex
$eventHost = 1343; // Vanessa Sterling
$cotGroupId = 169; // COTeam
$contactName = 'Lynn Hamill';
$contactEmail = 'lynn.c.hamill@gmail.com';
$contactPhone = '773.910.2311';
$sourceMessageId = '<CAKcfwQhxZOE4_UoY0k5PEitisRVskXDhxeWnGoSGOSD_Xxxdew@mail.gmail.com>';
$notes = implode("\n", [
    'Source: Cathy Chambliss reply on 2026-06-22, subject "Re: 15 Years, 1,000 Neighbors and One Big Ask! - KOVAL DISTILLERY", Message-ID ' . $sourceMessageId . '.',
    'KOVAL participation was already confirmed by Vanessa on 2026-06-21; Sonat and Robert were copied.',
    'Event logistics from Cathy: Friday, October 2, 2026 at Artifact Events; event hours 7:00 PM-11:00 PM; setup any time after 5:00 PM; be ready to pour by 6:45 PM; breakdown 11:00 PM-12:00 AM.',
    'Arrival/loading: use front parking lot loading zone; large deliveries may access the courtyard via the alley east of Ravenswood; call/text Heather Kundert or Lynn Hamill on arrival for display-area direction.',
    'Provided by Common Pantry: one 6 ft x 30 in x 30 in table with black linen tablecloth.',
    'Provided by KOVAL: products, serving supplies, branded decor, signage/business cards as desired.',
    'Contacts: Heather Kundert, Event Planner, heather@onthewayevents.com, 773-531-1265; Lynn Hamill, F+B Chair, lynn.c.hamill@gmail.com, 773-910-2311; Cathy Chambliss, Committee Chair, fundraising@commonpantry.org, 312-287-1718.',
    'Approval-sensitive asks in Cathy reply are not approved by this operational update: donated KOVAL Cranberry Gin for Artifact Events bars and COI naming Nevermore Events, LLC. Those are already routed separately to Ezra/legal-affairs taskflow-b17740ed97592539.',
]);
$importantInformation = 'Unassigned COTeam shift linked for setup/event/breakdown coverage: 5:00 PM-12:00 AM. Be ready to pour by 6:45 PM. Donation/COI requests require separate Ezra/legal-affairs approval before external commitment.';
$shiftNotes = 'Outreach: Common Pantry I Am Your Neighbor Party 2026 - unassigned COTeam setup/event/breakdown coverage';

if (!$eventPdo->inTransaction()) {
    $eventPdo->beginTransaction();
}
if (!$trackPdo->inTransaction()) {
    $trackPdo->beginTransaction();
}

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $exists = $eventPdo->prepare('SELECT id FROM event_bookings WHERE id = ? LIMIT 1');
    $exists->execute([$eventId]);
    if (!$exists->fetchColumn()) {
        throw new RuntimeException('Expected OPS event 1063 was not found.');
    }

    $updateEvent = $eventPdo->prepare(
        'UPDATE event_bookings
            SET event_name = ?, event_date = ?, event_end_date = NULL, event_category = ?,
                event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                contact_name = ?, contact_email = ?, contact_phone = ?, estimated_guest_count = ?,
                notes = ?, important_information = ?, event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ?'
    );
    $updateEvent->execute([
        $eventName,
        $eventDate,
        'Outreach',
        $location,
        $accountId,
        $eventStart,
        $eventEnd,
        $contactName,
        $contactEmail,
        $contactPhone,
        1000,
        $notes,
        $importantInformation,
        $eventHost,
        $eventId,
    ]);

    $accountExists = $eventPdo->prepare('SELECT 1 FROM event_booking_accounts WHERE event_booking_id = ? AND account_id = ? LIMIT 1');
    $accountExists->execute([$eventId, $accountId]);
    if (!$accountExists->fetchColumn()) {
        $eventPdo->prepare('INSERT INTO event_booking_accounts (event_booking_id, account_id) VALUES (?, ?)')->execute([$eventId, $accountId]);
    }

    $shiftLookup = $eventPdo->prepare('SELECT shift_id FROM event_booking_shift_links WHERE event_booking_id = ? ORDER BY id ASC LIMIT 1');
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
            common_pantry_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $shiftStart,
            $shiftEnd,
            $shiftNotes,
            $cotGroupId,
            $accountId,
            $createdBy,
            $shiftId,
        ]);
    } else {
        $insertShift = $trackPdo->prepare(
            "INSERT INTO " . TRACKTIME_DB_NAME . ".shifts
             (parent_id, week_day_id, start_date, end_date, start_time, end_time, deleted, notes, is_template, group_id, account_id, activity_id, created_by, updated_by)
             VALUES (0, ?, ?, ?, ?, ?, 0, ?, 0, ?, ?, 0, ?, ?)"
        );
        $insertShift->execute([
            common_pantry_week_day_id($eventDate),
            $eventDate,
            $eventDate,
            $shiftStart,
            $shiftEnd,
            $shiftNotes,
            $cotGroupId,
            $accountId,
            $createdBy,
            $createdBy,
        ]);
        $shiftId = (int) $trackPdo->lastInsertId();
        if ($shiftId <= 0) {
            throw new RuntimeException('Shift insert did not return an id.');
        }
        $eventPdo->prepare('INSERT INTO event_booking_shift_links (event_booking_id, shift_id, created_by) VALUES (?, ?, ?)')->execute([$eventId, $shiftId, $createdBy]);
    }

    $trackPdo->prepare("DELETE FROM " . TRACKTIME_DB_NAME . ".shift2user WHERE shift_id = ?")->execute([$shiftId]);

    if ($trackPdo->inTransaction()) {
        $trackPdo->commit();
    }
    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }
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

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => ''];
try {
    $tokenUserId = common_pantry_google_token_user_id($eventPdo);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $eventStmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $eventStmt->execute([$eventId]);
    $eventRow = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-outreach-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
    $calendarId = google_calendar_outreach_id();
    $existing = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($existing) && !empty($existing['id'])) {
        $resp = google_calendar_request(
            'PATCH',
            'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']),
            [],
            $payload,
            $tokenUserId
        );
        $operation = 'patched';
    } else {
        $resp = google_calendar_request(
            'POST',
            'calendars/' . rawurlencode($calendarId) . '/events',
            [],
            $payload,
            $tokenUserId
        );
        $operation = 'created';
    }
    if (empty($resp['success'])) {
        throw new RuntimeException((string) ($resp['error'] ?? 'Google Calendar request failed.'));
    }
    common_pantry_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => ''];
}

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.start_time, eb.end_time, eb.event_category,
            eb.event_location, eb.distributor_account_id, eb.contact_name, eb.contact_email,
            eb.contact_phone, eb.estimated_guest_count, eb.important_information,
            eb.event_host_user_id, l.shift_id, s.start_time AS shift_start, s.end_time AS shift_end,
            s.group_id, COUNT(s2u.user_id) AS assigned_user_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shifts s ON s.id = l.shift_id
       LEFT JOIN " . TRACKTIME_DB_NAME . ".shift2user s2u ON s2u.shift_id = s.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, l.shift_id, s.start_time, s.end_time, s.group_id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);
echo json_encode(['event' => $readback->fetch(PDO::FETCH_ASSOC), 'google_sync' => $googleSync], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n";
