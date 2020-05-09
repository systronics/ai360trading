<?php session_start();
if(isset($_POST['submit'])) {
$youremail = 'amit@mediorganics.in';
$fromsubject = 'Contact Form';
$name = $_POST['name'];
$mail = $_POST['email'];
$subject = $_POST['subject']; 
$message = $_POST['message']; 
$to = $youremail; 
$headers  = 'MIME-Version: 1.0' . "\r\n";
$headers .= 'Content-type:text/html; charset=UTF-8' . "\r\n";
$headers .= "From: ".$_POST['name']."<".$_POST['Email'].">\r\n"; 
$headers .= "Reply-To: ".$_POST["email"]."\r\n";
$mailsubject = 'Messsage recived for'.$fromsubject.' Contact Page';
$body = $fromsubject.'
	
	The person that contacted you is  '.$name.'
	 E-mail: '.$mail.'
	 Subject: '.$subject.'
	
	 Message: 
	 '.$message.'	
	|---------END MESSAGE----------|'; 
echo "Thank you fo your feedback. I will contact you shortly if needed.<br/>Go to <a href='/index.php'>Home Page</a>"; 
								mail($to, $subject, $body,$headers);
 } else { 
echo "You must write a message. </br> Please go to <a href='/index.html'>Home Page</a>"; 
}
?> 