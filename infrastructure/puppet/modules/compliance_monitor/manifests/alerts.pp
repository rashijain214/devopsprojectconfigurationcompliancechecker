# infrastructure/puppet/modules/compliance_monitor/manifests/alerts.pp
# Configures alert rules and notification contacts

class compliance_monitor::alerts {

  $contacts_cfg = '/etc/nagios4/conf.d/contacts.cfg'

  # Deploy contacts config (who gets alerted)
  file { $contacts_cfg:
    ensure  => file,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
    content => template('compliance_monitor/contacts.cfg.erb'),
    notify  => Service['nagios4'],
  }

  # Deploy alert script
  file { '/usr/local/bin/compliance_alert.sh':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    content => @("SCRIPT")
      #!/bin/bash
      # Puppet-managed alert script
      # Called by Nagios when compliance check fails

      SERVICE_STATE=$1
      SERVICE_OUTPUT=$2
      CONTACT_EMAIL=$3

      if [ "$SERVICE_STATE" = "CRITICAL" ]; then
        echo "CRITICAL: Compliance violation detected
      Details: ${SERVICE_OUTPUT}" | \
        mail -s "COMPLIANCE ALERT: Critical Violation Found" \
        "${CONTACT_EMAIL}"
      fi
      | SCRIPT
  }

}