<?php
$dir    = __DIR__;
$files1 = scandir($dir);
$res = '';
foreach ($files1 as $value) {
    if(stristr($value, '.') === FALSE) {
        $res = $res . $value . ';';
    }
  }

header('Content-Type: application/json; charset=utf-8');
echo json_encode($files1);
die();
?>