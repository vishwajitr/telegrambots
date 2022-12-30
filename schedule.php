<?php 
if(isset($_POST['GO']))

{

shell_exec("python3 /Applications/MAMP/htdocs/VishwajitWeb/crawler/scraper__coupons.py");

echo"success";

}

?>

