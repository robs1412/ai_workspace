#!/usr/bin/env php
<?php

declare(strict_types=1);

require_once '/Users/werkstatt/ops/bootstrap.php';

date_default_timezone_set('America/Chicago');

$pdo = get_event_pdo();
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);

$ownerId = 3;
$sourceDate = '2026-06-19';
$subject = 'Brooklyn Market Visit, New York';
$now = date('Y-m-d H:i:s');

$accounts = [
    [
        'key' => 'bar-great-harry',
        'name' => 'Bar Great Harry',
        'street' => '280 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'bar-san-miguel',
        'name' => 'Bar San Miguel',
        'street' => '307 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'cafe-luluc',
        'name' => 'Café Luluc',
        'street' => '214 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'clover-club',
        'name' => 'Clover Club',
        'street' => '210 Smith Street',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => true,
    ],
    [
        'key' => 'ceci-ne-pas-un-bar',
        'name' => 'Ceci ne pas un bar',
        'street' => '257 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'osteria-radisa',
        'name' => 'Osteria Radisa',
        'street' => '241 Smith St.',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'levant',
        'name' => 'Levant',
        'street' => '223 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'landmark',
        'name' => 'Landmark',
        'street' => '221 Smith St.',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => false,
    ],
    [
        'key' => 'bees-knees',
        'name' => "Bee's Knees Provisions",
        'street' => '215 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => true,
    ],
    [
        'key' => 'bar-reve',
        'name' => 'Bar Reve',
        'street' => '222 Smith St',
        'city' => 'Brooklyn',
        'state' => 'New York',
        'country' => 'United States',
        'reuse_exact' => true,
    ],
];

$contacts = [
    [
        'key' => 'sarah-bgh',
        'firstname' => 'Sarah',
        'lastname' => '',
        'title' => 'Bar staff',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bar-great-harry'],
    ],
    [
        'key' => 'dan-bgh',
        'firstname' => 'Dan',
        'lastname' => '',
        'title' => 'Order contact',
        'email' => 'bargreatharry@gmail.com',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bar-great-harry'],
    ],
    [
        'key' => 'aurael-bsm',
        'firstname' => 'Aurael',
        'lastname' => '',
        'title' => 'Bartender',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bar-san-miguel'],
    ],
    [
        'key' => 'petru-buyer',
        'firstname' => 'Petru',
        'lastname' => '',
        'title' => 'Buyer',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bar-san-miguel', 'landmark'],
    ],
    [
        'key' => 'mauritizio-clover',
        'firstname' => 'Mauritizio',
        'lastname' => '',
        'title' => 'Decision maker',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['clover-club'],
    ],
    [
        'key' => 'ryan-clover',
        'firstname' => 'Ryan',
        'lastname' => '',
        'title' => 'Sales contact',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['clover-club'],
    ],
    [
        'key' => 'katerina-ceci',
        'firstname' => 'Katerina',
        'lastname' => '',
        'title' => '',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['ceci-ne-pas-un-bar'],
    ],
    [
        'key' => 'morgan-ceci',
        'firstname' => 'Morgan',
        'lastname' => '',
        'title' => 'Beverage director',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['ceci-ne-pas-un-bar'],
    ],
    [
        'key' => 'althea-osteria',
        'firstname' => 'Althea',
        'lastname' => '',
        'title' => 'Manager',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['osteria-radisa'],
    ],
    [
        'key' => 'marco-levant',
        'firstname' => 'Marco',
        'lastname' => '',
        'title' => 'Manager',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['levant'],
    ],
    [
        'key' => 'philipe-landmark',
        'firstname' => 'Philipe',
        'lastname' => '',
        'title' => 'Bartender',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['landmark'],
    ],
    [
        'key' => 'jacob-bees',
        'firstname' => 'Jacob',
        'lastname' => '',
        'title' => 'Bartender',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bees-knees'],
    ],
    [
        'key' => 'kristen-bees',
        'firstname' => 'Kristen',
        'lastname' => '',
        'title' => 'Beverage director',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bees-knees'],
    ],
    [
        'key' => 'taj-bees',
        'firstname' => 'Taj',
        'lastname' => '',
        'title' => 'Owner',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bees-knees'],
    ],
    [
        'key' => 'marshall-reve',
        'firstname' => 'Marshall',
        'lastname' => '',
        'title' => 'Bartender',
        'email' => '',
        'phone' => '',
        'mobile' => '',
        'account_keys' => ['bar-reve'],
    ],
    [
        'key' => 'dylan-mckeever',
        'firstname' => 'Dylan',
        'lastname' => 'Mckeever',
        'title' => 'Head bartender',
        'email' => 'Dylan.Mckeever@barreve.com',
        'phone' => '651-280-7820',
        'mobile' => '',
        'account_keys' => ['bar-reve'],
    ],
];

$activityPlan = [
    'bar-great-harry' => [
        'contacts' => ['sarah-bgh', 'dan-bgh'],
        'note' => "Sarah was at the bar, but Dan handles order placement.\nEmail noted in recap: bargreatharry@gmail.com",
    ],
    'bar-san-miguel' => [
        'contacts' => ['aurael-bsm', 'petru-buyer'],
        'note' => "Aurael is the bartender. Petru is the buyer for both places.",
    ],
    'cafe-luluc' => [
        'contacts' => [],
        'note' => "Manager not named in recap. Phone noted in recap: 1-718-625-3815.",
    ],
    'clover-club' => [
        'contacts' => ['mauritizio-clover', 'ryan-clover'],
        'note' => "Mauritizio is the decision maker; spelling was uncertain in the recap. Ryan tried everything.",
    ],
    'ceci-ne-pas-un-bar' => [
        'contacts' => ['katerina-ceci', 'morgan-ceci'],
        'note' => "Katerina loved the Cranberry Gin. Morgan is the beverage director and boyfriend of Katerina.",
    ],
    'osteria-radisa' => [
        'contacts' => ['althea-osteria'],
        'note' => "Althea is the manager.",
    ],
    'levant' => [
        'contacts' => ['marco-levant'],
        'note' => "Marco is the manager and needs follow-up.",
    ],
    'landmark' => [
        'contacts' => ['philipe-landmark', 'petru-buyer'],
        'note' => "Petru was in meeting; Philipe was the bartender. Aurael sent Sonat to Petru at Landmark, who is the buyer for both places.",
    ],
    'bees-knees' => [
        'contacts' => ['jacob-bees', 'kristen-bees', 'taj-bees'],
        'note' => "Jacob is the bartender. Kristen is the beverage director. Taj is the owner.",
    ],
    'bar-reve' => [
        'contacts' => ['marshall-reve', 'dylan-mckeever'],
        'note' => "Marshall is the new bartender. Dylan Mckeever is the head bartender and likely decision maker.",
    ],
];

function nextCrmId(PDO $pdo): int
{
    $pdo->exec('UPDATE vtiger_crmentity_seq SET id = id + 1');
    return (int) $pdo->query('SELECT id FROM vtiger_crmentity_seq LIMIT 1')->fetchColumn();
}

function nextModuleNo(PDO $pdo, string $module): string
{
    $pdo->exec('UPDATE vtiger_modentity_num_seq SET id = id + 1');
    $num = (int) $pdo->query('SELECT id FROM vtiger_modentity_num_seq LIMIT 1')->fetchColumn();
    $stmt = $pdo->prepare('UPDATE vtiger_modentity_num SET cur_id = ? WHERE semodule = ?');
    $stmt->execute([$num, $module]);
    return ($module === 'Calendar' ? 'CAL' : ($module === 'Contacts' ? 'CON' : 'ACC')) . $num;
}

function findAccount(PDO $pdo, string $name, string $street, string $city, string $state): ?array
{
    $stmt = $pdo->prepare(
        'SELECT acc.accountid, acc.accountname, bill.bill_street, bill.bill_city, bill.bill_state
         FROM vtiger_account acc
         JOIN vtiger_accountbillads bill ON bill.accountaddressid = acc.accountid
         JOIN vtiger_crmentity ent ON ent.crmid = acc.accountid AND ent.deleted = 0
         WHERE acc.accountname = ? AND IFNULL(bill.bill_street, "") = ? AND IFNULL(bill.bill_city, "") = ? AND IFNULL(bill.bill_state, "") = ?'
    );
    $stmt->execute([$name, $street, $city, $state]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function findAccountByStreet(PDO $pdo, string $street, string $city, string $state): ?array
{
    $stmt = $pdo->prepare(
        'SELECT acc.accountid, acc.accountname, bill.bill_street, bill.bill_city, bill.bill_state
         FROM vtiger_account acc
         JOIN vtiger_accountbillads bill ON bill.accountaddressid = acc.accountid
         JOIN vtiger_crmentity ent ON ent.crmid = acc.accountid AND ent.deleted = 0
         WHERE IFNULL(bill.bill_street, "") = ? AND IFNULL(bill.bill_city, "") = ? AND IFNULL(bill.bill_state, "") = ?'
    );
    $stmt->execute([$street, $city, $state]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function findContactDuplicate(PDO $pdo, array $spec): ?array
{
    $stmt = $pdo->prepare(
        'SELECT c.contactid, c.firstname, c.lastname, c.email
         FROM vtiger_contactdetails c
         JOIN vtiger_crmentity ent ON ent.crmid = c.contactid AND ent.deleted = 0
         WHERE IFNULL(c.firstname, "") = ? AND IFNULL(c.lastname, "") = ? AND IFNULL(c.email, "") = ?'
    );
    $stmt->execute([$spec['firstname'], $spec['lastname'], $spec['email']]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function findActivityDuplicate(PDO $pdo, int $accountId, string $subject, string $dateStart): ?array
{
    $stmt = $pdo->prepare(
        'SELECT act.activityid, act.subject, act.date_start
         FROM vtiger_activity act
         JOIN vtiger_seactivityrel rel ON rel.activityid = act.activityid
         JOIN vtiger_crmentity ent ON ent.crmid = act.activityid AND ent.deleted = 0
         WHERE rel.crmid = ? AND act.subject = ? AND act.date_start = ?'
    );
    $stmt->execute([$accountId, $subject, $dateStart]);
    $row = $stmt->fetch();
    return $row ?: null;
}

function createAccount(PDO $pdo, array $spec, int $ownerId, string $now): int
{
    $id = nextCrmId($pdo);
    $accountNo = nextModuleNo($pdo, 'Accounts');

    $pdo->prepare(
        'INSERT INTO vtiger_crmentity
         (crmid, smcreatorid, smownerid, modifiedby, setype, description, createdtime, modifiedtime, viewedtime, status, version, presence, deleted, label)
         VALUES (?, ?, ?, ?, "Accounts", "", ?, ?, 0, 0, 0, 1, 0, ?)'
    )->execute([$id, $ownerId, $ownerId, $ownerId, $now, $now, $spec['name']]);

    $pdo->prepare(
        'INSERT INTO vtiger_account (accountid, account_no, accountname, website, email1, phone, fax)
         VALUES (?, ?, ?, "", "", "", "")'
    )->execute([$id, $accountNo, $spec['name']]);

    $pdo->prepare(
        'INSERT INTO vtiger_accountscf (accountid, cf_586, cf_672, cf_671)
         VALUES (?, NULL, NULL, NULL)'
    )->execute([$id]);

    $pdo->prepare(
        'INSERT INTO vtiger_accountbillads (accountaddressid, bill_country, bill_state, bill_city, bill_street, bill_code, bill_pobox)
         VALUES (?, ?, ?, ?, ?, "", "")'
    )->execute([$id, $spec['country'], $spec['state'], $spec['city'], $spec['street']]);

    $pdo->prepare(
        'INSERT INTO vtiger_accountshipads (accountaddressid, ship_country, ship_state, ship_city, ship_street, ship_code, ship_pobox)
         VALUES (?, "", "", "", "", "", "")'
    )->execute([$id]);

    return $id;
}

function createContact(PDO $pdo, array $spec, int $ownerId, string $now): int
{
    $id = nextCrmId($pdo);
    $contactNo = nextModuleNo($pdo, 'Contacts');
    $fullName = trim($spec['firstname'] . ' ' . $spec['lastname']);

    $pdo->prepare(
        'INSERT INTO vtiger_crmentity
         (crmid, smcreatorid, smownerid, modifiedby, setype, description, createdtime, modifiedtime, viewedtime, status, version, presence, deleted, label)
         VALUES (?, ?, ?, ?, "Contacts", "", ?, ?, 0, 0, 0, 1, 0, ?)'
    )->execute([$id, $ownerId, $ownerId, $ownerId, $now, $now, $fullName]);

    $pdo->prepare(
        'INSERT INTO vtiger_contactdetails (contactid, salutation, firstname, lastname, email, phone, mobile, title, department, fax, secondaryemail, contact_no, current_dist)
         VALUES (?, "", ?, ?, ?, ?, ?, ?, "", "", "", ?, 0)'
    )->execute([
        $id,
        $spec['firstname'],
        $spec['lastname'],
        $spec['email'],
        $spec['phone'],
        $spec['mobile'],
        $spec['title'],
        $contactNo,
    ]);

    $pdo->prepare(
        'INSERT INTO vtiger_contactaddress
         (contactaddressid, mailingcountry, mailingstate, mailingcity, mailingstreet, mailingzip, mailingpobox, othercountry, othercity, otherstate, otherzip, otherstreet, otherpobox)
         VALUES (?, "", "", "", "", "", "", "", "", "", "", "", "")'
    )->execute([$id]);

    return $id;
}

function linkContactToAccount(PDO $pdo, int $contactId, int $accountId): void
{
    $exists = $pdo->prepare('SELECT 1 FROM contact2account WHERE contact_id = ? AND account_id = ? LIMIT 1');
    $exists->execute([$contactId, $accountId]);
    if ($exists->fetchColumn()) {
        return;
    }

    $pdo->prepare('INSERT INTO contact2account (contact_id, account_id) VALUES (?, ?)')->execute([$contactId, $accountId]);
    $pdo->prepare(
        'INSERT INTO contact2account_history (contact_id, account_id, status, modified_by) VALUES (?, ?, "added", ?)'
    )->execute([$contactId, $accountId, 3]);
}

function createActivity(PDO $pdo, array $spec, int $accountId, array $contactIds, int $ownerId, string $date, string $now): int
{
    $id = nextCrmId($pdo);
    $activityNo = nextModuleNo($pdo, 'Calendar');
    $eventStatus = (new DateTimeImmutable($date) > new DateTimeImmutable(date('Y-m-d'))) ? 'Planned' : 'Held';

    $pdo->prepare(
        'INSERT INTO vtiger_crmentity
         (crmid, smcreatorid, smownerid, modifiedby, setype, description, createdtime, modifiedtime, viewedtime, status, version, presence, deleted, label)
         VALUES (?, ?, ?, ?, "Calendar", ?, ?, ?, 0, 0, 0, 1, 0, ?)'
    )->execute([$id, $ownerId, $ownerId, $ownerId, $spec['note'], $now, $now, $subject]);

    $pdo->prepare(
        'INSERT INTO vtiger_activity
         (activityid, parent_id, subject, semodule, activitytype, date_start, due_date, time_start, time_end, sendnotification, duration_hours, duration_minutes, status, eventstatus, priority, location, notime, visibility, recurringtype, reviewed)
         VALUES (?, 0, ?, "", "Meeting", ?, ?, "", "", 0, 0, 0, "", ?, "", "", 0, "Public", "", 1)'
    )->execute([$id, $subject, $date, $date, $eventStatus]);

    $pdo->prepare(
        'INSERT INTO vtiger_activitycf
         (activityid, cf_674, cf_675, cf_676, cf_677, cf_678, cf_679, cf_680, cf_684, cf_685, cf_686, cf_687, cf_901, cf_903)
         VALUES (?, "", "", "", "", "", "", "", "", "", "", "", "", "")'
    )->execute([$id]);

    $pdo->prepare(
        'INSERT INTO vtiger_seactivityrel (crmid, activityid) VALUES (?, ?)'
    )->execute([$accountId, $id]);

    $contactStmt = $pdo->prepare('INSERT INTO activity2contact (activity_id, contact_id) VALUES (?, ?)');
    foreach ($contactIds as $contactId) {
        $check = $pdo->prepare('SELECT 1 FROM activity2contact WHERE activity_id = ? AND contact_id = ? LIMIT 1');
        $check->execute([$id, $contactId]);
        if (!$check->fetchColumn()) {
            $contactStmt->execute([$id, $contactId]);
        }
    }

    return $id;
}

$summary = [
    'duplicates' => [],
    'accounts' => [],
    'contacts' => [],
    'activities' => [],
];

try {
    $pdo->beginTransaction();

    $accountIds = [];
    foreach ($accounts as $spec) {
        $existing = $spec['reuse_exact']
            ? findAccount($pdo, $spec['name'], $spec['street'], $spec['city'], $spec['state'])
            : null;

        if ($existing) {
            $accountIds[$spec['key']] = (int) $existing['accountid'];
            $summary['duplicates']['accounts'][] = [
                'key' => $spec['key'],
                'accountid' => (int) $existing['accountid'],
                'name' => $existing['accountname'],
                'street' => $existing['bill_street'],
                'mode' => 'exact',
            ];
            continue;
        }

        if ($spec['key'] === 'bees-knees') {
            $streetMatch = findAccountByStreet($pdo, $spec['street'], $spec['city'], $spec['state']);
            if ($streetMatch) {
                $accountIds[$spec['key']] = (int) $streetMatch['accountid'];
                $summary['duplicates']['accounts'][] = [
                    'key' => $spec['key'],
                    'accountid' => (int) $streetMatch['accountid'],
                    'name' => $streetMatch['accountname'],
                    'street' => $streetMatch['bill_street'],
                    'mode' => 'street-match',
                ];
                continue;
            }
        }

        $newId = createAccount($pdo, $spec, $ownerId, $now);
        $accountIds[$spec['key']] = $newId;
        $summary['accounts'][] = [
            'key' => $spec['key'],
            'accountid' => $newId,
            'name' => $spec['name'],
            'street' => $spec['street'],
            'created' => true,
        ];
    }

    $contactIds = [];
    foreach ($contacts as $spec) {
        $existing = findContactDuplicate($pdo, $spec);
        if ($existing) {
            $contactIds[$spec['key']] = (int) $existing['contactid'];
            $summary['duplicates']['contacts'][] = [
                'key' => $spec['key'],
                'contactid' => (int) $existing['contactid'],
                'firstname' => $existing['firstname'],
                'lastname' => $existing['lastname'],
                'email' => $existing['email'],
            ];
            continue;
        }

        $newId = createContact($pdo, $spec, $ownerId, $now);
        $contactIds[$spec['key']] = $newId;
        foreach ($spec['account_keys'] as $accountKey) {
            linkContactToAccount($pdo, $newId, $accountIds[$accountKey]);
        }
        $summary['contacts'][] = [
            'key' => $spec['key'],
            'contactid' => $newId,
            'firstname' => $spec['firstname'],
            'lastname' => $spec['lastname'],
            'email' => $spec['email'],
            'accounts' => $spec['account_keys'],
            'created' => true,
        ];
    }

    foreach ($activityPlan as $accountKey => $plan) {
        $accountId = $accountIds[$accountKey];
        $existing = findActivityDuplicate($pdo, $accountId, $subject, $sourceDate);
        if ($existing) {
            $summary['duplicates']['activities'][] = [
                'account_key' => $accountKey,
                'activityid' => (int) $existing['activityid'],
                'subject' => $existing['subject'],
                'date_start' => $existing['date_start'],
            ];
            continue;
        }

        $linkedContactIds = [];
        foreach ($plan['contacts'] as $contactKey) {
            if (isset($contactIds[$contactKey])) {
                $linkedContactIds[] = $contactIds[$contactKey];
            }
        }

        $newId = createActivity($pdo, $plan, $accountId, $linkedContactIds, $ownerId, $sourceDate, $now);
        $summary['activities'][] = [
            'account_key' => $accountKey,
            'activityid' => $newId,
            'subject' => $subject,
            'date_start' => $sourceDate,
            'contacts' => $plan['contacts'],
            'created' => true,
        ];
    }

    $pdo->commit();
    $summary['status'] = 'committed';
    $summary['account_ids'] = $accountIds;
    $summary['contact_ids'] = $contactIds;
    echo json_encode($summary, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . PHP_EOL;
    exit(0);
} catch (Throwable $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    $summary['status'] = 'failed';
    $summary['error'] = $e->getMessage();
    echo json_encode($summary, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . PHP_EOL;
    exit(1);
}
