<?php
/**
 * Quota
 *
 * Qutoa Plugin
 *
 * @version 1.0
 * @author Pokerkoffer
 */
class quota extends rcube_plugin
{
    public $task = 'mail';
    public $quota_hard_regex = "/Hard-Quota: (\\d+)/";
    public $directory_regex = "/Directory: (.+)/";


    function init()
    {
        $RCMAIL = rcmail::get_instance();
        $RCMAIL->output->set_env('quota', true);
        $this->add_hook('quota', array($this, 'calculate_quota'));
    }

    function calculate_quota($args)
    {
        $username = $_SESSION['username'];
        $username = explode('@', $username)[0];

        $user_atts = $this->get_user_vars($username);
        $hard_quota = round($user_atts['hard_quota']/1024);

        // remove . at beginning and add ~
        $user_dir = "~" . substr($user_atts['directory'], 1);
        $du = $this->get_disk_usage($user_dir);

        if ($hard_quota === 0) {
            $percent = 0;
        } else {
            $percent = $du/$hard_quota*100;
        }

        $args = array(
            'total' => $hard_quota,
            'used' => $du,
            'percent' => round($percent),
            'all' => ''
        );
        return $args;
    }

    // returns disk usage of folder in byte
    function get_disk_usage($folder) {
        $handle = popen('du -sb '.$folder.' 2>&1', 'r');
        $read = fread($handle, 2096);
        pclose($handle);
        if(preg_match("/(\\d+)/",$read,$match)) {
            return round($match[1]/1024);
        } else {
            return 0;
        }
    }

    function get_user_vars($username)
    {
        $attr = array(
            'hard_quota' => 0,
            'directory' => ""
        );

        $handle = popen('dumpvuser ' . $username . ' 2>&1', 'r');
        $read = fread($handle, 2096);
        pclose($handle);

        if (preg_match($this->directory_regex, $read, $matches)) {
            $attr['directory'] = $matches[1];
        }

        if (preg_match($this->quota_hard_regex, $read, $matches)) {
            $attr['hard_quota'] = $matches[1];
        }
        return $attr;
    }
}