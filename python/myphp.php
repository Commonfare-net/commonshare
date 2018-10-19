<html>
<body>

<?php echo $_GET["userid"]; 
$output = shell_exec("python pagerank.py " . $_GET["objectid|"]);
echo $output;
?><br>
</body>
</html>