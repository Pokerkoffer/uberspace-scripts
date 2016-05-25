<?php
class setNameOnCreateUser extends rcube_plugin
{
    //public $task = 'login';

    function init()
    {
        error_reporting(E_ERROR);
        $this->add_hook('user_create', array($this, 'user_created'));
    }

    function user_created($args)
    {
        $email = $args['user'];
        $mailwithouthost = explode("@", $email)[0];
        $parts = explode(".", $mailwithouthost);

        // email is not like firstname.lastname so skip this
        if (count($parts) < 2) {
           return $args;
        }
        $first_name = $parts[0];
        $first_name = ucfirst($first_name);

        $last_name = $parts[1];
        $last_name = ucfirst($last_name);

        $user_name = $first_name . " " . $last_name;
        $user_name = str_replace("ae", "ä", $user_name);
        $user_name = str_replace("ue", "ü", $user_name);
        $user_name = str_replace("oe", "ö", $user_name);
        $user_name = str_replace("Ae", "Ä", $user_name);
        $user_name = str_replace("Ue", "Ü", $user_name);
        $user_name = str_replace("Oe", "Ö", $user_name);
        $user_name = str_replace("ss", "ß", $user_name);

        $args['user_name'] = $user_name;

        return $args;
    }
}