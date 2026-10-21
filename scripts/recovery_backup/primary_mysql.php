<?php
declare(strict_types=1);
// Uses the established application connection; never prints credentials or raw errors.
// --estimate is metadata-only. --dump is gated and requires an installed MySQL client.
$options = getopt('', ['estimate', 'check', 'dump', 'approved', 'allow-write-locks', 'client:']);
$temporary = null;
$exitCode = 0;
try {
    require '/Users/werkstatt/ops/bootstrap.php';
    $pdo = get_event_pdo();
    $rows = $pdo->query("SELECT table_schema,COUNT(*) AS tables,COALESCE(SUM(data_length+index_length),0) AS bytes,SUM(engine IS NOT NULL AND engine <> 'InnoDB') AS non_innodb FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','performance_schema','mysql','sys') GROUP BY table_schema")->fetchAll(PDO::FETCH_ASSOC);
    if (isset($options['estimate'])) { echo json_encode($rows), PHP_EOL; exit(0); }
    if (!isset($options['check']) && !isset($options['dump'], $options['approved'], $options['allow-write-locks'])) throw new RuntimeException('Export requires explicit approval and database write-lock approval.');
    $client = $options['client'] ?? '';
    if ($client === '' || !is_executable($client)) throw new RuntimeException('Database client is not installed.');
    $names = array_column($rows, 'table_schema');
    if (!$names) throw new RuntimeException('No databases accessible.');
    foreach ($names as $name) if (!preg_match('/^[A-Za-z0-9_]+$/', $name)) throw new RuntimeException('Unsupported database identifier.');
    $targets = array_merge(['--databases'], $names);
    if (isset($options['check'])) {
        $sample = $pdo->query("SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','performance_schema','mysql','sys') AND table_type='BASE TABLE' ORDER BY data_length LIMIT 1")->fetch(PDO::FETCH_ASSOC);
        if (!$sample || !preg_match('/^[A-Za-z0-9_]+$/', $sample['table_name'])) throw new RuntimeException('No safe schema probe target.');
        $targets = [$sample['table_schema'], $sample['table_name']];
    }
    $quote = static fn($s) => '"' . str_replace(["\\", '"', "\n", "\r"], ["\\\\", '\\"', '\\n', '\\r'], (string)$s) . '"';
    $temporary = tempnam(sys_get_temp_dir(), 'recovery-client-');
    if ($temporary === false || !chmod($temporary, 0600)) throw new RuntimeException('Cannot prepare protected client configuration.');
    $data = "[client]\nhost=".$quote(DB_HOST)."\nuser=".$quote(DB_USER)."\npassword=".$quote(DB_PASS)."\n";
    if (file_put_contents($temporary, $data) === false) throw new RuntimeException('Cannot write protected client configuration.');
    $mode = isset($options['check']) ? ['--no-data', '--skip-lock-tables'] : ['--lock-all-tables'];
    $args = array_merge([$client, '--defaults-extra-file='.$temporary, '--column-statistics=0', '--no-tablespaces', '--set-gtid-purged=OFF'], $mode, ['--quick', '--routines', '--events', '--triggers', '--hex-blob'], $targets);
    // SQL goes only to the controller's protected export stream. stderr stays suppressed.
    $process = proc_open($args, [0=>['file','/dev/null','r'], 1=>isset($options['check']) ? ['file','/dev/null','w'] : STDOUT, 2=>['file','/dev/null','w']], $pipes);
    if (!is_resource($process) || proc_close($process) !== 0) throw new RuntimeException('Database export failed.');
    if (isset($options['check'])) echo json_encode(['representative_schema_export_check'=>true,'inventoried_schemas'=>count($names)]), PHP_EOL;
} catch (Throwable $e) {
    fwrite(STDERR, "Database backup operation failed; private details suppressed.\n");
    $exitCode = 1;
} finally {
    if (is_string($temporary) && is_file($temporary)) unlink($temporary);
}

exit($exitCode);
