<?php
$output = shell_exec("python ../python/pagerank.py ../data/output/recommenderdata.gexf " . $_GET["storyid"] . " " . $_GET["userid"] . " 2>&1");
echo $output;
?>
