<?php
class rcube_vpasswd_password
{
    public function save($currpass, $newpass)
    {
        $username = $_SESSION['username'];
        $username = explode('@', $username)[0];
        print $username;
        $handle = popen('vpasswd '.$username.' 2>&1', 'w');
        fwrite($handle, $newpass."\n");
        fwrite($handle, $newpass."\n");
        if (pclose($handle) == 0) {
            return PASSWORD_SUCCESS;
        }
        return PASSWORD_ERROR;
    }
}    
?>