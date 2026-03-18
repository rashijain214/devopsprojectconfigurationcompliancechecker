# infrastructure/puppet/modules/compliance_monitor/manifests/nagios.pp
# Installs Nagios and configures monitoring for compliance checker

class compliance_monitor::nagios {

  # ── Install Nagios ──────────────────────────────────────────

  package { 'nagios4':
    ensure => present,
  }

  package { 'nagios-plugins':
    ensure  => present,
    require => Package['nagios4'],
  }

  package { 'curl':
    ensure => present,
  }

  # ── Nagios Service ──────────────────────────────────────────

  service { 'nagios4':
    ensure    => running,
    enable    => true,
    hasstatus => true,
    require   => [
      Package['nagios4'],
      File['/etc/nagios4/nagios.cfg'],
    ],
  }

  # ── Main Nagios Config ──────────────────────────────────────

  file { '/etc/nagios4/nagios.cfg':
    ensure  => file,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
    content => template('compliance_monitor/nagios.cfg.erb'),
    notify  => Service['nagios4'],
    require => Package['nagios4'],
  }

  # ── Host Config — monitors localhost ───────────────────────

  file { '/etc/nagios4/conf.d/compliance_checker_host.cfg':
    ensure  => file,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
    content => template('compliance_monitor/host.cfg.erb'),
    notify  => Service['nagios4'],
    require => Package['nagios4'],
  }

  # ── Service Config — monitors app health ───────────────────

  file { '/etc/nagios4/conf.d/compliance_checker_services.cfg':
    ensure  => file,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
    content => template('compliance_monitor/services.cfg.erb'),
    notify  => Service['nagios4'],
    require => Package['nagios4'],
  }

  # ── Commands Config ─────────────────────────────────────────

  file { '/etc/nagios4/conf.d/compliance_checker_commands.cfg':
    ensure  => file,
    owner   => 'nagios',
    group   => 'nagios',
    mode    => '0644',
    content => template('compliance_monitor/commands.cfg.erb'),
    notify  => Service['nagios4'],
    require => Package['nagios4'],
  }

}