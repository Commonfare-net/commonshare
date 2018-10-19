<?php
$output = shell_exec("python pagerank.py data/newdata.gexf " . $_GET["userid"]);
echo $output;
?>
