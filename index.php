<?php
  function can_upload($file){
    if($file['name'] == '')
		return 'Вы не выбрали файл.';
	if($file['size'] == 0)
		return 'Файл слишком большой.';
	$getMime = explode('.', $file['name']);
	$mime = strtolower(end($getMime));
	$types = array('jpg', 'jpeg');
	if(!in_array($mime, $types))
		return 'Недопустимый тип файла.';
	return true;
  }
  
  function make_upload($file, $num){
	if ($num == 0) {
		$fd = fopen("seecode/file1name.txt", 'w');
		copy($file['tmp_name'], "seecode/0.jpg");
	} else {
		$fd = fopen("seecode/file2name.txt", 'w');
		copy($file['tmp_name'], "seecode/1.jpg");
	}
	fwrite($fd, $file['name']);
	fclose($fd);
  }
?>
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Camera Recogniser</title>
	<style>
		body {
			min-width: 740px;
			margin: 0;
		}
		.top-text {
			font-family: "Times New Roman";
			color: brown;
			text-align: center;
			margin-block-start: 0;
			margin-block-end: 10px;
		}
		.tparent {
			display: flex;
			align-items: flex-start;
			justify-content: center;
			flex-wrap: wrap;
		}
		.tchild {
			font-family: sans-serif;
			font-weight: bold;
			font-size: 14pt;
			color: darkblue;
			text-align: center;
			margin-left: 10px;
			margin-right: 10px;
			margin-bottom: 20px;
			background-color: bisque;
			border: 4px ridge #8B8B8B;
		}
		form {
			font-size: 12pt;
			font-family: sans-serif;
			text-align: left;
			color: black;
			margin-top: 5px;
		}
		.fileerr {
			color: darkred;
			font-weight: bold;
			font-size: 12px
		}
		.filesc {
			color: darkgreen;
			font-size: 12px
		}
	</style>
</head>
<body>
	<h1 class="top-text">Camera Recogniser</h1>
	<div class="tparent">
		<div class="tchild">Recognised photos</div>
		<div class="tchild">
			<iframe style="display:block; border: 1px solid black;" src="https://open.ivideon.com/embed/v2/?server=100-OumTZ&amp;camera=0&amp;width=&amp;height=&amp;lang=ru" width="640" height="360" frameborder="0" allowfullscreen></iframe>
			Camera stream</div>
		<div class="tchild">Loaded photos
			<form action=index.php method=post enctype=multipart/form-data>
			<input type=file name=file1>
				<?php 
				  if(isset($_FILES['file1'])) {
				  $res = can_upload($_FILES['file1']);
    			  if($res === true){   
    			    make_upload($_FILES['file1'], 0);
    			    echo "<div class=\"filesc\">Файл успешно загружен!</div>";
    			  } else {
   			        echo "<div class=\"fileerr\">Произошла ошибка: ".$res."</div>";
   			      }
   			    }?> <br>
			<input type=file name=file2>
				<?php
			    if (isset($_FILES['file2'])) {
					$res = can_upload($_FILES['file2']);
				  if($res === true){ 
    			    make_upload($_FILES['file2'], 1);
    			    echo "<div class=\"filesc\">Файл успешно загружен!</div>";
    			  } else {
   			        echo "<div class=\"fileerr\">Произошла ошибка: ".$res."</div>";
   			      }
				}
   			 ?>
			<div style="text-align: right;"><input type=submit value=Загрузить style="text-align: right;"></div>
			</form>
			
		</div>
	</div>
</body>
</html>