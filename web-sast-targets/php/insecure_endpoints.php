<?php
// Collection of intentionally vulnerable PHP endpoints for SAST evaluation.

if (!function_exists('respond')) {
    function respond($data) {
        header('Content-Type: application/json');
        echo json_encode($data);
    }
}

$db = new PDO('sqlite::memory:');

// SQL injection vulnerabilities (1-10)
if ($_SERVER['REQUEST_URI'] === '/php/sql/login') {
    $user = $_POST['username'] ?? '';
    $pass = $_POST['password'] ?? '';
    $sql = "SELECT * FROM users WHERE username = '$user' AND password = '$pass'";
    $rows = $db->query($sql)->fetchAll();
    respond(['sql' => $sql, 'rows' => $rows]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/search') {
    $term = $_GET['term'] ?? '';
    $sql = "SELECT * FROM products WHERE name LIKE '%$term%'";
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/delete') {
    $id = $_GET['id'] ?? '0';
    $sql = "DELETE FROM orders WHERE id=$id";
    $db->exec($sql);
    respond(['sql' => $sql]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/update') {
    $bio = $_POST['bio'] ?? '';
    $id = $_POST['id'] ?? '0';
    $sql = "UPDATE profiles SET bio='$bio' WHERE id=$id";
    $db->exec($sql);
    respond(['sql' => $sql]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/report') {
    $year = $_GET['year'] ?? '2020';
    $sql = "SELECT * FROM reports WHERE year=$year";
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/export') {
    $table = $_GET['table'] ?? 'users';
    $sql = "SELECT * FROM $table";
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/raw') {
    $sql = file_get_contents('php://input');
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/order') {
    $order = $_GET['order'] ?? 'id';
    $sql = "SELECT * FROM invoices ORDER BY $order";
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/comment') {
    $post = $_POST['post'] ?? '0';
    $body = $_POST['body'] ?? '';
    $sql = "INSERT INTO comments (post_id, body) VALUES ($post, '$body')";
    $db->exec($sql);
    respond(['sql' => $sql]);
}

if ($_SERVER['REQUEST_URI'] === '/php/sql/where') {
    $where = $_POST['where'] ?? '1=1';
    $sql = "SELECT * FROM data WHERE $where";
    respond(['sql' => $sql, 'rows' => $db->query($sql)->fetchAll()]);
}

// Command injection vulnerabilities (11-20)
if ($_SERVER['REQUEST_URI'] === '/php/cmd/ping') {
    $host = $_GET['host'] ?? '';
    $output = shell_exec('ping -c 1 ' . $host);
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/curl') {
    $url = $_POST['url'] ?? '';
    $output = shell_exec('curl ' . $url);
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/git') {
    $repo = $_GET['repo'] ?? '';
    $output = shell_exec("git clone $repo /tmp/repo");
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/tar') {
    $path = $_POST['path'] ?? '.';
    $output = shell_exec('tar -czf archive.tgz ' . $path);
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/convert') {
    $source = $_POST['source'] ?? '';
    $output = shell_exec('convert ' . $source . ' out.png');
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/python') {
    $code = file_get_contents('php://input');
    $output = shell_exec('python -c "' . $code . '"');
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/mysql') {
    $query = $_POST['query'] ?? '';
    $output = shell_exec('mysql -e "' . $query . '"');
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/ps') {
    $filter = $_GET['filter'] ?? '';
    $output = shell_exec('ps aux | grep ' . $filter);
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/mail') {
    $to = $_POST['to'] ?? '';
    $body = $_POST['body'] ?? '';
    $output = shell_exec("sendmail $to <<<'$body'");
    respond(['output' => $output]);
}

if ($_SERVER['REQUEST_URI'] === '/php/cmd/sed') {
    $expr = $_POST['expr'] ?? '';
    $file = $_POST['file'] ?? '';
    $output = shell_exec("sed -n '$expr' $file");
    respond(['output' => $output]);
}

// File handling / path traversal (21-30)
if ($_SERVER['REQUEST_URI'] === '/php/file/read') {
    $path = $_GET['path'] ?? '/etc/passwd';
    respond(['data' => file_get_contents($path)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/write') {
    $path = $_POST['path'] ?? '/tmp/file';
    $data = $_POST['data'] ?? '';
    file_put_contents($path, $data);
    respond(['status' => 'written']);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/delete') {
    $path = $_POST['path'] ?? '/tmp/file';
    unlink($path);
    respond(['status' => 'deleted']);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/list') {
    $dir = $_GET['dir'] ?? '.';
    respond(['entries' => scandir($dir)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/include') {
    $template = $_GET['template'] ?? 'template.php';
    include $template;
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/file/download') {
    $path = $_GET['file'] ?? '/etc/shadow';
    readfile($path);
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/file/config') {
    $config = $_POST['config'] ?? 'config.ini';
    respond(parse_ini_file($config));
}

if ($_SERVER['REQUEST_URI'] === '/php/file/logs') {
    $name = $_GET['name'] ?? 'syslog';
    respond(['log' => file_get_contents('/var/log/' . $name)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/archive') {
    $archive = $_GET['archive'] ?? '/tmp/archive.tgz';
    shell_exec('tar -xzf ' . $archive);
    respond(['status' => 'extracted']);
}

if ($_SERVER['REQUEST_URI'] === '/php/file/template') {
    $template = $_GET['template'] ?? 'page.html';
    $content = str_replace('{{body}}', $_GET['body'] ?? '', file_get_contents($template));
    echo $content;
    exit;
}

// XSS / output encoding issues (31-40)
if ($_SERVER['REQUEST_URI'] === '/php/xss/hello') {
    $name = $_GET['name'] ?? 'guest';
    echo "<h1>Hello $name</h1>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/comment') {
    $comment = $_POST['comment'] ?? '';
    echo "<div class='comment'>$comment</div>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/jsonp') {
    $callback = $_GET['callback'] ?? 'cb';
    $data = json_encode(['status' => 'ok']);
    echo "$callback($data)";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/email') {
    $email = $_GET['email'] ?? '';
    echo "<a href='mailto:$email'>$email</a>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/profile') {
    $bio = $_POST['bio'] ?? '';
    echo "<section>$bio</section>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/preview') {
    $content = file_get_contents('php://input');
    echo "<div class='preview'>$content</div>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/widget') {
    $config = $_GET['config'] ?? '{}';
    echo "<script>var config = $config;</script>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/chat') {
    $message = $_GET['message'] ?? '';
    echo "<span data-msg='$message'>$message</span>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/rss') {
    $title = $_GET['title'] ?? '';
    echo "<item><title>$title</title></item>";
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/xss/iframe') {
    $src = $_GET['src'] ?? '';
    echo "<iframe src='$src'></iframe>";
    exit;
}

// SSRF / server-side request abuse (41-50)
if ($_SERVER['REQUEST_URI'] === '/php/ssrf/proxy') {
    $url = $_GET['url'] ?? 'http://localhost';
    respond(['body' => file_get_contents($url)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/post') {
    $url = $_POST['url'] ?? 'http://localhost';
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'content' => http_build_query($_POST)
        ]
    ]);
    respond(['body' => file_get_contents($url, false, $context)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/auth') {
    $host = $_GET['host'] ?? '169.254.169.254/latest/meta-data/';
    respond(['body' => file_get_contents('http://' . $host)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/download') {
    $url = $_GET['url'] ?? 'http://localhost';
    echo file_get_contents($url);
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/image') {
    $url = $_POST['image_url'] ?? '';
    header('Content-Type: image/png');
    echo file_get_contents($url);
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/notify') {
    $callback = $_POST['callback'] ?? '';
    $context = stream_context_create([
        'http' => [
            'method' => 'POST',
            'content' => $_POST['payload'] ?? ''
        ]
    ]);
    respond(['body' => file_get_contents($callback, false, $context)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/webhook') {
    $target = $_GET['target'] ?? 'http://localhost';
    respond(['body' => file_get_contents($target)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/cache') {
    $resource = $_GET['resource'] ?? 'http://localhost/cache';
    respond(['body' => file_get_contents($resource)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/feed') {
    $feed = $_GET['feed'] ?? 'http://localhost/feed';
    respond(['body' => file_get_contents($feed)]);
}

if ($_SERVER['REQUEST_URI'] === '/php/ssrf/metrics') {
    $endpoint = $_GET['endpoint'] ?? 'http://localhost/metrics';
    respond(['body' => file_get_contents($endpoint)]);
}
