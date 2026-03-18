# infrastructure/puppet/manifests/site.pp
# Main Puppet manifest for Configuration Compliance Checker project
# Applies all modules to configure monitoring

node default {

  # Step 1: Ensure Python is available
  class { 'compliance_monitor::python': }

  # Step 2: Install and configure Nagios monitoring
  class { 'compliance_monitor::nagios': }

  # Step 3: Deploy compliance checker application
  class { 'compliance_monitor::app': }

  # Step 4: Set up alerting
  class { 'compliance_monitor::alerts': }

  # Enforce order
  Class['compliance_monitor::python']
  -> Class['compliance_monitor::nagios']
  -> Class['compliance_monitor::app']
  -> Class['compliance_monitor::alerts']

}