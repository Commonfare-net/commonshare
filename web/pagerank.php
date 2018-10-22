<?php
$output = shell_exec("python pagerank.py data/newdata.gexf " . $_GET["storyid"] . " " . $_GET["userid"]);
echo $output;
?>
