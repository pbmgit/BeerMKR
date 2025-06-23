<?php
$tbag=68;
$tgrain=-15;
$tempC1=$tbag;
$tempC2=$tgrain;
$tempF1 = ($tempC1 -32) * 5 / 9;
$tempF2 = ($tempC2 - 32) * 5 / 9;
$myfile = fopen("/home/BeerPi/statusfile", "r") or die("Unable to open file!");
$L1 = fgets($myfile);
$L2 = fgets($myfile);
$L3 = fgets($myfile);

fclose($myfile);
$report_time = $L1;
$brewstatus = $L2;
$marlinstatus = $L3;

$pat = '~T:([^ ]*) /([^ ]*) B:([^ ]*) /([^ ]*) [^P]*P@:([A-Z])~U';
$pat = '~T:([^ ]*) /([^ ]*) B:([^ ]*) /([^ ]*) [^:]*:([^ ]*) [^:]*:([^ ]*) [^P]*P@:([A-Z])~U';

//print $pat;

preg_match($pat,$marlinstatus,$matches);
//print_r($matches);


$tgrain = (float)$matches[1];
//echo $tgrain;

$grainset = (float)$matches[2];
$bagt = (float)$matches[3];
$bagset = (float)$matches[4];
$HeatPower = $matches[5];
$PeltPower = $matches[6];
$peltdir = $matches[7];

$tempC1=$tbag;
$tempC2=$tgrain;
$tempF1 = ($tempC1 -32) * 5 / 9;
$tempF2 = ($tempC2 - 32) * 5 / 9;


$tempC1 = $matches[3] . " / " . $matches[4];
$tempF1 = ($tempC1 * 9 / 5) + 32;
$tempF2 = ($tempC2 * 9 / 5) + 32;
$peltcolor = "heating";



if ($PeltPower > 0) {
	print $PeltPower;
	if (strcmp($peltdir,"H")==0) 
		$peltcolor = "heating";
	elseif (strcmp($peltdir,"C")==0) 
		$peltcolor = "cooling";
}
else {
	if (strcmp($peltdir,"H")==0) 
		$peltcolor = "hot";
	elseif (strcmp($peltdir,"C")==0) 
		$peltcolor = "cold";
}

$DisplayTempF2 = number_format($tempF2,1) . " °F";
//$DisplayTempF2 = $DisplayTempF2 . " °F";
$DisplayTempC2 = number_format($tempC2,2) . " / " . number_format($grainset,2) . " C";
//$DisplayTempF2 = "Hard";
//$DisplayTempC2 = "Code";
//print $peltcolor;

if ($HeatPower > 0){
	$heatcolor = "heating";
}
else {
	$heatcolor = "hot";
}
if ($tgrain < 0) {
	$heatcolor = "disco";
	$DisplayTempF2 = "Disco";
	$DisplayTempC2 = " ";

}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	<meta http-equiv="refresh" content="10; url="<?php echo $_SERVER['PHP_SELF']; ?>">
    <title>BeerMKR Resurrection</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: Arial, sans-serif;
        }
        .container {
            display: flex;
            justify-content: center;
            width: 80%;
        }
        .temperature-box {
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            width: 200px;
        }
        .spacer-box {
            width: 40px;
            padding: 20px;
            text-align: center;

        }
        .heating {
			background-color: #ff5555;
		}
		.hot {
            background-color: #ffcccc;
        }
        .cold {
            background-color: #B0E0E6;
        }
		.cooling {
			background-color: #0000FF;
			color: #FFFFFF;
		}
		
		.disco {
			background-color: #505050;
		}
        .large {
            font-size: 48px;
        }
        .small {
            font-size: 24px;
        }
        .title-small }
            font-size:24px;
        }
    </style>
</head>
<body>

    <h1>BeerMKR Resurrection</h1>
    <p>Marlin Status Date: <?php echo $report_time; ?></p>
    <p>Current Date: <?php echo date('Y-m-d H:i:s'); ?></p>
    <p>Process Status: <?php echo $brewstatus; ?></p>

    <div class="container">
        <div class="temperature-box <?php echo $peltcolor; ?>">
            <div class="title-small">Brew Bag Temperature</div>
            <div class="large"><?php echo number_format($tempF1,1); ?>°F</div>
            <div class="small"><?php echo $tempC1; ?>°C</div>
        </div>
        <div class="spacer-box">
        </div>
        <div class="temperature-box <?php echo $heatcolor; ?>">
            <div class="title-small">Grain Temperature</div>
            <div class="large"><?php echo $DisplayTempF2; ?></div>
            <div class="small"><?php echo $DisplayTempC2; ?></div>
        </div>
    </div>

</body>
</html>


