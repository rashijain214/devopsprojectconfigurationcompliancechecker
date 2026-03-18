# infrastructure/puppet/modules/compliance_monitor/manifests/app.pp
# Deploys the compliance checker application files and scheduled runs

class compliance_monitor::app {

  $app_dir    = '/opt/compliance-checker'
  $report_dir = '/var/reports/compliance-checker'

  # Create app directory
  file { $app_dir:
    ensure => directory,
    owner  => 'appuser',
    group  => 'appuser',
    mode   => '0755',
  }

  # Deploy the compliance checker script
  file { "${app_dir}/compliance_checker.py":
    ensure => file,
    owner  => 'appuser',
    group  => 'appuser',
    mode   => '0755',
    source => 'puppet:///modules/compliance_monitor/compliance_checker.py',
  }

  # Create a wrapper shell script for scheduled runs
  file { '/usr/local/bin/run_compliance_check.sh':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    content => @("SCRIPT")
      #!/bin/bash
      # Puppet-managed: run compliance check and save report
      TIMESTAMP=$(date +%Y%m%d_%H%M%S)
      REPORT_FILE="${report_dir}/report_${TIMESTAMP}.json"

      python3 ${app_dir}/compliance_checker.py \
        /etc/compliance-checker/Dockerfile \
        /etc/compliance-checker/docker-compose.yml \
        /etc/compliance-checker/deployment.yaml \
        --output "${REPORT_FILE}"

      echo "Report saved: ${REPORT_FILE}"
      | SCRIPT
    require => File[$app_dir],
  }

  # Schedule compliance check every hour via cron
  cron { 'hourly-compliance-check':
    ensure  => present,
    command => '/usr/local/bin/run_compliance_check.sh',
    user    => 'appuser',
    hour    => '*',
    minute  => '0',
    require => File['/usr/local/bin/run_compliance_check.sh'],
  }

}