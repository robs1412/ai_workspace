#!/usr/bin/env php
<?php
declare(strict_types=1);

require_once '/Users/werkstatt/ops/config.php';
require_once '/Users/werkstatt/ops/bootstrap.php';

function fsc_market_token_user_id(PDO $pdo, array $preferredUserIds): ?int
{
    foreach ($preferredUserIds as $candidate) {
        $candidate = (int) $candidate;
        if ($candidate > 0 && google_oauth_has_user_token($candidate)) {
            return $candidate;
        }
    }

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

function fsc_upsert_google_link(PDO $pdo, int $eventId, string $uid): void
{
    $stmt = $pdo->prepare(
        'INSERT INTO event_booking_google_links (event_booking_id, google_event_uid, calendar_type)
         VALUES (?, ?, ?)
         ON DUPLICATE KEY UPDATE google_event_uid = VALUES(google_event_uid), calendar_type = VALUES(calendar_type), updated_at = CURRENT_TIMESTAMP'
    );
    $stmt->execute([$eventId, $uid, 'market']);
}

$eventPdo = get_event_pdo();

$eventName = 'Fine Spirits Classic';
$eventDate = '2026-08-20';
$eventStart = '18:00';
$eventEnd = '21:00';
$location = 'Orchestra Hall, 1111 Nicollet Mall, Minneapolis, MN 55403';
$createdBy = 1332; // Codex
$sourceMessageIds = [
    'calbltzwta=e0p5urcmdx+gk4k4zvvgj1oqvlu77_g=3qdtj-hw@mail.gmail.com',
    'calbltzz_f9yfohvkgg6nahvbpxraa6cm8keavov_lxr7xfsnbg@mail.gmail.com',
    'calbltzzqozfklpx_cqjxq2hnelmatyvkrsy=1rxn5xt+hm55dw@mail.gmail.com',
];
$notes = implode("\n", [
    'Source: Sonat Birnecker email to Vanessa Sterling, Message-ID <' . $sourceMessageIds[0] . '>.',
    'Related payment thread copied to National Outreach, Message-ID <' . $sourceMessageIds[1] . '>.',
    'Welcome packet forwarded by Sonat to Vanessa, Message-ID <' . $sourceMessageIds[2] . '>.',
    'Direct instruction: add Fine Spirits Classic to the OPS Market Calendar.',
    'Event details from source: Minnesota Monthly Fine Spirits Classic on August 20, 2026 from 6:00 PM-9:00 PM at Orchestra Hall, 1111 Nicollet Mall, Minneapolis, MN 55403.',
    'Participation/payment context from copied thread: Sonat asked Scott Rorvig how to pay the reduced $350 fee.',
    'Welcome packet requests: confirm brand listing as KOVAL Distillery linked to https://www.koval-distillery.com/; decide whether to participate in the Crafted Cocktail Contest; submit cocktail details by 2026-07-06 if participating; provide at least 35 press-kit items by 2026-07-13; provide social media giveaway product by 2026-07-13; send product/flavor list for onsite tasting notes by 2026-08-01; submit required operations forms, including Minneapolis Short-Term Food Permit Application Request, by 2026-08-05.',
    'Ship/drop-off information for press kit and giveaway product: Beth Wulf, Greenspring Media, 9401 James Avenue S., Suite #152, Bloomington, MN 55431. Office hours: Monday-Thursday 8:30 AM-4:30 PM, Friday 8:30 AM-3:30 PM.',
    'Operations contact from welcome packet: Rick Krueger, rkrueger@greenspring.com.',
    'Discounted ticket code from welcome packet: GMPARTNER.',
    'Event page from source: https://www.minnesotamonthly.com/fine-spirits-classic/',
    'Sponsor & Exhibitor Portal from source: https://greenspring.com/fine-spirits-classic-sponsor-exhibitor-portal/',
    'No attendee, staffing, linked account, products, receipts, or shifts were supplied in the source packet.',
]);
$importantInformation = 'Market Event from Sonat request. Reduced fee is $350; Sonat asked Scott Rorvig how to pay. Welcome packet deadlines: 7/6 cocktail details if participating; 7/13 press-kit and giveaway product; 8/1 product/flavor list; 8/5 operations forms/food permit request. Add attendee/staffing, account, products, receipts, and shifts when confirmed.';
$sonatUserId = 3;
$taskDefinitions = [
    [
        'name' => 'Fine Spirits Classic: confirm brand listing',
        'external_due' => '2026-07-02',
        'reminder_due' => '2026-06-30',
        'description' => 'Confirm Minnesota Monthly should list the brand as "KOVAL Distillery" linked to https://www.koval-distillery.com/. Source did not provide a hard external deadline; reminder due date is set for prompt handling.',
    ],
    [
        'name' => 'Fine Spirits Classic: decide on Crafted Cocktail Contest and send cocktail details if participating',
        'external_due' => '2026-07-06',
        'reminder_due' => '2026-07-04',
        'description' => 'If KOVAL participates in the 3rd Annual Crafted Cocktail Contest, send cocktail name, ingredients, and details. External deadline: 2026-07-06.',
    ],
    [
        'name' => 'Fine Spirits Classic: send or ship at least 35 press-kit items',
        'external_due' => '2026-07-13',
        'reminder_due' => '2026-07-11',
        'description' => 'Provide at least 35 press-kit items such as product samples, stickers, branded merchandise, swag, or coupons. Ship/drop off to Beth Wulf, Greenspring Media, 9401 James Avenue S., Suite #152, Bloomington, MN 55431. External deadline: 2026-07-13.',
    ],
    [
        'name' => 'Fine Spirits Classic: provide social media giveaway product',
        'external_due' => '2026-07-13',
        'reminder_due' => '2026-07-11',
        'description' => 'Provide product for the @MNMOmag giveaway series, such as samples, branded merchandise, gift cards, or a curated prize box. Ship/drop off to Beth Wulf at Greenspring Media. External deadline: 2026-07-13.',
    ],
    [
        'name' => 'Fine Spirits Classic: send product and flavor list for tasting notes',
        'external_due' => '2026-08-01',
        'reminder_due' => '2026-07-30',
        'description' => 'Send the list of products and flavors KOVAL will sample onsite for inclusion in printed tasting notes. External deadline: 2026-08-01.',
    ],
    [
        'name' => 'Fine Spirits Classic: submit required operations forms and permit request',
        'external_due' => '2026-08-05',
        'reminder_due' => '2026-08-03',
        'description' => 'Visit the Sponsor & Exhibitor Portal and submit required operations forms, including the Minneapolis Short-Term Food Permit Application Request. Operations contact: Rick Krueger, rkrueger@greenspring.com. External deadline: 2026-08-05.',
    ],
];

function fsc_create_or_update_sonat_task(PDO $eventPdo, int $eventId, array $eventRow, array $task, int $sonatUserId): array
{
    $taskName = (string) $task['name'];
    $reminderDue = (string) $task['reminder_due'];
    $description = implode("\n", [
        'Auto-generated from Sonat-forwarded Fine Spirits Classic welcome packet.',
        'Event: ' . (string) ($eventRow['event_name'] ?? 'Fine Spirits Classic'),
        'Event date: ' . (string) ($eventRow['event_date'] ?? '2026-08-20'),
        'Reminder due date: ' . $reminderDue . ' (two days before the external deadline where one was provided).',
        'External deadline: ' . (string) $task['external_due'],
        (string) $task['description'],
        'OPS: https://www.koval-distillery.com/ops/index.php?view=edit&id=' . $eventId,
        'Source Message-ID: <calbltzzqozfklpx_cqjxq2hnelmatyvkrsy=1rxn5xt+hm55dw@mail.gmail.com>',
    ]);

    $existingStmt = $eventPdo->prepare(
        'SELECT id, crm_task_id
           FROM event_booking_tasks
          WHERE event_booking_id = ?
            AND task_name = ?
          ORDER BY id DESC
          LIMIT 1'
    );
    $existingStmt->execute([$eventId, $taskName]);
    $existing = $existingStmt->fetch(PDO::FETCH_ASSOC) ?: null;
    $bookingTaskId = (int) ($existing['id'] ?? 0);
    $crmTaskId = (int) ($existing['crm_task_id'] ?? 0);

    if ($crmTaskId <= 0) {
        $payload = [
            'task_name' => $taskName,
            'description' => $description,
            'date_start' => $reminderDue,
            'due_date' => $reminderDue,
            'status' => ['label' => 'Not Started'],
            'priority' => ['label' => 'Normal'],
            'assigned_to' => [['id' => $sonatUserId]],
            'assignedUsers' => [['id' => $sonatUserId]],
            'assigned_to_ids' => [$sonatUserId],
            'sendnotification' => 1,
            'send_notification' => true,
            'sendNotification' => true,
        ];
        $resp = crm_create_task($payload, 'sonat', [
            'allow_service_fallback' => true,
            'force_creator_user_id' => 1332,
            'force_owner_user_id' => $sonatUserId,
        ]);
        $crmTaskId = (int) ($resp['id'] ?? 0);
    } else {
        $eventPdo->prepare(
            "UPDATE koval_crm.vtiger_activity
                SET subject = ?, date_start = ?, due_date = ?, status = 'Not Started', priority = 'Normal', sendnotification = 1
              WHERE activityid = ? AND activitytype = 'Task'"
        )->execute([$taskName, $reminderDue, $reminderDue, $crmTaskId]);
        $eventPdo->prepare('UPDATE koval_crm.vtiger_crmentity SET smownerid = ?, modifiedtime = NOW(), modifiedby = ? WHERE crmid = ?')
            ->execute([$sonatUserId, 1332, $crmTaskId]);
    }

    if ($bookingTaskId > 0) {
        $eventPdo->prepare(
            'UPDATE event_booking_tasks
                SET task_description = ?, due_date = ?, assigned_user_id = ?, crm_task_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        )->execute([$description, $reminderDue, $sonatUserId, $crmTaskId > 0 ? $crmTaskId : null, $bookingTaskId]);
    } else {
        $insertStmt = $eventPdo->prepare(
            'INSERT INTO event_booking_tasks (event_booking_id, task_id, task_name, task_description, due_date, assigned_user_id, crm_task_id)
             VALUES (?, NULL, ?, ?, ?, ?, ?)'
        );
        $insertStmt->execute([$eventId, $taskName, $description, $reminderDue, $sonatUserId, $crmTaskId > 0 ? $crmTaskId : null]);
        $bookingTaskId = (int) $eventPdo->lastInsertId();
    }

    return [
        'event_booking_task_id' => $bookingTaskId,
        'crm_task_id' => $crmTaskId,
        'task_name' => $taskName,
        'reminder_due' => $reminderDue,
        'external_due' => (string) $task['external_due'],
    ];
}

$eventPdo->beginTransaction();

try {
    ensure_event_bookings_important_information_column($eventPdo);
    ensure_event_bookings_max_capacity_column($eventPdo);
    ensure_event_bookings_pioneer_flag_column($eventPdo);
    ensure_event_shift_links_table($eventPdo);

    $dupeStmt = $eventPdo->prepare(
        "SELECT id
           FROM event_bookings
          WHERE event_date = ?
            AND event_category = 'Market Event'
            AND (event_name LIKE ? OR event_location LIKE ? OR notes LIKE ? OR notes LIKE ?)
          ORDER BY id DESC
          LIMIT 1"
    );
    $dupeStmt->execute([
        $eventDate,
        '%Fine%Spirits%Classic%',
        '%Orchestra Hall%',
        '%' . $sourceMessageIds[0] . '%',
        '%' . $sourceMessageIds[1] . '%',
    ]);
    $eventId = (int) ($dupeStmt->fetchColumn() ?: 0);

    if ($eventId > 0) {
        $updateEvent = $eventPdo->prepare(
            'UPDATE event_bookings
                SET event_name = ?, event_date = ?, event_end_date = ?, event_category = ?,
                    event_location = ?, distributor_account_id = ?, start_time = ?, end_time = ?,
                    contact_name = ?, contact_email = ?, contact_phone = ?, amount_paid = ?,
                    estimated_guest_count = ?, notes = ?, important_information = ?,
                    event_host_user_id = ?, updated_at = CURRENT_TIMESTAMP
              WHERE id = ?'
        );
        $updateEvent->execute([
            $eventName,
            $eventDate,
            null,
            'Market Event',
            $location,
            null,
            $eventStart,
            $eventEnd,
            'Scott Rorvig',
            'srorvig@greenspring.com',
            '',
            350,
            null,
            $notes,
            $importantInformation,
            null,
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
            'Market Event',
            $location,
            null,
            $eventStart,
            $eventEnd,
            'Scott Rorvig',
            'srorvig@greenspring.com',
            '',
            350,
            null,
            null,
            null,
            $notes,
            $importantInformation,
            0,
            null,
            null,
            $createdBy,
            null,
        ]);
        $eventId = (int) $eventPdo->lastInsertId();
        if ($eventId <= 0) {
            throw new RuntimeException('Event insert did not return an id.');
        }
    }

    if ($eventPdo->inTransaction()) {
        $eventPdo->commit();
    }
} catch (Throwable $e) {
    if ($eventPdo->inTransaction()) {
        $eventPdo->rollBack();
    }
    fwrite(STDERR, $e->getMessage() . "\n");
    exit(1);
}

$taskResults = [];
try {
    $eventStmt = $eventPdo->prepare('SELECT id, event_name, event_date, start_time, end_time FROM event_bookings WHERE id = ?');
    $eventStmt->execute([$eventId]);
    $eventRowForTasks = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRowForTasks)) {
        throw new RuntimeException('Unable to read event before creating tasks.');
    }

    foreach ($taskDefinitions as $taskDefinition) {
        $taskResults[] = fsc_create_or_update_sonat_task($eventPdo, $eventId, $eventRowForTasks, $taskDefinition, $sonatUserId);
    }
} catch (Throwable $e) {
    fwrite(STDERR, 'Task sync failed: ' . $e->getMessage() . "\n");
    exit(1);
}

$googleSync = ['attempted' => false, 'status' => 'not_attempted', 'uid' => '', 'calendar_type' => 'market'];
try {
    if (!google_oauth_is_configured() || !google_oauth_has_any_token()) {
        throw new RuntimeException('Google OAuth is not connected yet.');
    }
    $tokenUserId = fsc_market_token_user_id($eventPdo, [$createdBy, 3, 21, 144]);
    if ($tokenUserId === null) {
        throw new RuntimeException('No usable Google OAuth refresh token user found.');
    }
    $calendarId = google_calendar_market_id();
    if ($calendarId === '') {
        throw new RuntimeException('Market calendar ID is not configured.');
    }
    $eventStmt = $eventPdo->prepare('SELECT * FROM event_bookings WHERE id = ?');
    $eventStmt->execute([$eventId]);
    $eventRow = $eventStmt->fetch(PDO::FETCH_ASSOC);
    if (!is_array($eventRow)) {
        throw new RuntimeException('Unable to read event for Google sync.');
    }
    $uid = 'ops-market-' . $eventId . '@koval-distillery.com';
    $payload = google_calendar_build_event_payload($eventRow, $uid);
    $payload['status'] = 'confirmed';
    $existing = google_calendar_find_event_by_icaluid($calendarId, $uid, true, $tokenUserId);
    if (is_array($existing) && !empty($existing['id'])) {
        $patchPayload = $payload;
        unset($patchPayload['iCalUID']);
        $resp = google_calendar_request(
            'PATCH',
            'calendars/' . rawurlencode($calendarId) . '/events/' . rawurlencode((string) $existing['id']),
            [],
            $patchPayload,
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
    fsc_upsert_google_link($eventPdo, $eventId, $uid);
    $googleSync = ['attempted' => true, 'status' => $operation, 'uid' => $uid, 'calendar_type' => 'market'];
} catch (Throwable $e) {
    $googleSync = ['attempted' => true, 'status' => 'failed', 'error' => $e->getMessage(), 'uid' => '', 'calendar_type' => 'market'];
}

$readback = $eventPdo->prepare(
    "SELECT eb.id, eb.event_name, eb.event_date, eb.event_end_date, eb.start_time, eb.end_time,
            eb.event_category, eb.event_location, eb.contact_name, eb.contact_email, eb.amount_paid,
            eb.event_host_user_id, eb.created_by,
            CONCAT(cu.first_name, ' ', cu.last_name) AS created_by_name,
            COUNT(DISTINCT l.shift_id) AS linked_shift_count,
            COUNT(DISTINCT ebs.user_id) AS staff_count,
            COUNT(DISTINCT ebt.id) AS task_count,
            gl.google_event_uid, gl.calendar_type
       FROM event_bookings eb
       LEFT JOIN koval_crm.vtiger_users cu ON cu.id = eb.created_by
       LEFT JOIN event_booking_shift_links l ON l.event_booking_id = eb.id
       LEFT JOIN event_booking_staff ebs ON ebs.event_booking_id = eb.id
       LEFT JOIN event_booking_tasks ebt ON ebt.event_booking_id = eb.id
       LEFT JOIN event_booking_google_links gl ON gl.event_booking_id = eb.id
      WHERE eb.id = ?
      GROUP BY eb.id, gl.google_event_uid, gl.calendar_type"
);
$readback->execute([$eventId]);

$taskReadback = $eventPdo->prepare(
    "SELECT ebt.id, ebt.task_name, ebt.due_date, ebt.assigned_user_id, ebt.crm_task_id,
            a.subject AS crm_subject, a.due_date AS crm_due_date, a.status AS crm_status,
            ent.smownerid AS crm_owner_user_id,
            CONCAT(owner.first_name, ' ', owner.last_name) AS crm_owner_name
       FROM event_booking_tasks ebt
       LEFT JOIN koval_crm.vtiger_activity a ON a.activityid = ebt.crm_task_id
       LEFT JOIN koval_crm.vtiger_crmentity ent ON ent.crmid = ebt.crm_task_id
       LEFT JOIN koval_crm.vtiger_users owner ON owner.id = ent.smownerid
      WHERE ebt.event_booking_id = ?
      ORDER BY ebt.due_date ASC, ebt.id ASC"
);
$taskReadback->execute([$eventId]);

echo json_encode(
    [
        'event' => $readback->fetch(PDO::FETCH_ASSOC),
        'google_sync' => $googleSync,
        'task_sync' => $taskResults,
        'tasks' => $taskReadback->fetchAll(PDO::FETCH_ASSOC),
    ],
    JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES
) . "\n";
