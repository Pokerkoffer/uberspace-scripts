<?php 
class quota_notify extends rcube_plugin {
  public $task = 'mail';

  function init() {
    $this->add_hook('quota', array($this, 'quota_warning_message'));
  }

  function quota_warning_message($args) {
    $rcmail = rcmail::get_instance();
    if($args['percent'] > 99) {
      $rcmail->output->show_message('Deine Mailbox ist voll! Du kannst keine weiteren E-Mails mehr empfangen. Lösche Mails mit großen Anhängen und leere deinen Papierkorb!', 'error');
    } else if($args['percent'] > 90) {
      $rcmail->output->show_message('Deine Mailbox ist fast voll: ' . $args['percent'] . '%. Lösche nicht mehr benötigte E-Mails und leere deinen Papierkorb.', 'warning');
    }
  }
}

