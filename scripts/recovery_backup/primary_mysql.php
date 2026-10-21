<?php
declare(strict_types=1);
// Uses the established application connection; never prints credentials or raw errors.
// --estimate is metadata-only. --dump is gated and requires an installed MySQL client.
$options = getopt('', ['estimate', 'dump', 'approved', 'allow-write-locks', 'client:']);
$temporary = null;
$exitCode = 0;
try {
    require '/Users/werkstatt/ops/bootstrap.php';
    $pdo = get_event_pdo();
    $rows = $pdo->query("SELECT table_schema,COUNT(*) AS tables,COALESCE(SUM(data_length+index_length),0) AS bytes,SUM(engine IS NOT NULL AND engine <> 'InnoDB') AS non_innodb FROM information_schema.tables WHERE table_schema NOT IN ('information_schema','performance_schema','mysql','sys') GROUP BY table_schema")->fetchAll(PDO::FETCH_ASSOC);
    if (isset($options['estimate'])) { echo json_encode($rows), PHP_EOL; exit(0); }
    if (!isset($options['dump'], $options['approved'], $options['allow-write-locks'])) throw new RuntimeException('Export requires explicit approval and database write-lock approval.');
    $client = $options['client'] ?? '';
    if ($client === '' || !is_executable($client)) throw new RuntimeException('Database client is not installed.');
    $names = array_column($rows, 'table_schema');
    if (!$names) throw new RuntimeException('No databases accessible.');
    foreach ($names as $name) if (!preg_match('/^[A-Za-z0-9_]+$/', $name)) throw new RuntimeException('Unsupported database identifier.');
    $quote = static fn($s) => '"' . str_replace(["\\", '"', "\n", "\r"], ["\\\\", '\\"', '\\n', '\\r'], (string)$s) . '"';
    $temporary = tempnam(sys_get_temp_dir(), 'recovery-client-');
    if ($temporary === false || !chmod($temporary, 0600)) throw new RuntimeException('Cannot prepare protected client configuration.');
    $data = "[client]\nhost=".$quote(DB_HOST)."\nuser=".$quote(DB_USER)."\npassword=".$quote(DB_PASS)."\n";
    if (file_put_contents($temporary, $data) === false) throw new RuntimeException('Cannot write protected client configuration.');
    $args = array_merge([$client, '--defaults-extra-file='.$temporary, '--lock-all-tables', '--quick', '--routines', '--events', '--triggers', '--hex-blob', '--databases'], $names);
    // SQL goes only to the controller's protected export stream. stderr stays suppressed.
    $process = proc_open($args, [0=>['file','/dev/null','r'], 1=>STDOUT, 2=>['file','/dev/null','w']], $pipes);
    if (!is_resource($process) || proc_close($process) !== 0) throw new RuntimeException('Database export failed.');
} catch (Throwable $e) {
    fwrite(STDERR, "Database backup operation failed; private details suppressed.\n");
    $exitCode = 1;
} finally {
    if (is_string($temporary) && is_file($temporary)) unlink($temporary);
}

exit($exitCode);
