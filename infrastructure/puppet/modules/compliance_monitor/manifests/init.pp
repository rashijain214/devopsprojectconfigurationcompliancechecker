# infrastructure/puppet/modules/compliance_monitor/manifests/init.pp
# Main class for compliance_monitor module

class compliance_monitor {

  $app_name    = 'compliance-checker'
  $app_version = '1.0.0'
  $app_port    = 8080
  $app_dir     = '/opt/compliance-checker'
  $log_dir     = '/var/log/compliance-checker'
  $report_dir  = '/var/reports/compliance-checker'

  # Ensure log and report directories exist
  file { $log_dir:
    ensure => directory,
    mode   => '0755',
    owner  => 'appuser',
    group  => 'appuser',
  }

  file { $report_dir:
    ensure => directory,
    mode   => '0755',
    owner  => 'appuser',
    group  => 'appuser',
  }

  # Create application user (non-root - follows DF003 rule)
  user { 'appuser':
    ensure     => present,
    managehome => true,
    shell      => '/bin/bash',
    comment    => 'Compliance Checker Application User',
  }

}