<span class="current"><?php

$heute = date("Y-m-d");
//$dirs = array_filter(glob('/home/xnfrxkas/public_html/webcamarchive/*'), 'is_dir');
$dirs = array_filter(glob('../www/webcamarchive_y-m-d/*'), 'is_dir');
$lasty = end($dirs);
$dirs = array_filter(glob($lasty .'/*'), 'is_dir');
$lastm = end($dirs);
$dirs = array_filter(glob($lastm .'/*'), 'is_dir');
$lastd = end($dirs);
$files = glob($lastd . '/*.jpeg');
//$files = glob($last . '/*');
foreach($files as $file) {
   $erstes = $file;
   $erstes = str_replace("../www/","../../",$erstes);
   //break;
}

//echo date("Y-m-d--H-i-s");
//echo "../webcamarchive/2018-12-27/2018-12-27--08-30-01.jpeg";
echo $erstes;
?></span>&nbsp;<span class="uhrzeit"><?php

echo substr($erstes,-13,8);

?></span>

<p>

<?php
//echo $last . "<p>";
echo '<img class="currentimg" src="' . $erstes . '">';

?>
<br>
<button class="navigate" id="pd" name="pd" value="pd">previous day</button>

<button class="navigate" id="pi" name="pi" value="pi">previous image</button>

<button class="navigate" id="ni" name="ni" value="ni">next image</button>

<button class="navigate" id="nd" name="nd" value="nd">next day</button>



