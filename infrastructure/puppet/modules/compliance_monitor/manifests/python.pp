# infrastructure/puppet/modules/compliance_monitor/manifests/python.pp
# Ensures Python and required packages are installed

class compliance_monitor::python {

  # Install Python 3
  package { 'python3':
    ensure => '3.11.0',
  }

  # Install pip
  package { 'python3-pip':
    ensure  => present,
    require => Package['python3'],
  }

  # Install PyYAML (required by compliance checker)
  exec { 'install-pyyaml':
    command => 'pip3 install pyyaml>=6.0',
    path    => ['/usr/bin', '/usr/local/bin'],
    unless  => 'pip3 show pyyaml',
    require => Package['python3-pip'],
  }

  # Install pytest for running tests
  exec { 'install-pytest':
    command => 'pip3 install pytest pytest-cov',
    path    => ['/usr/bin', '/usr/local/bin'],
    unless  => 'pip3 show pytest',
    require => Package['python3-pip'],
  }

  # Install pylint for code quality
  exec { 'install-pylint':
    command => 'pip3 install pylint',
    path    => ['/usr/bin', '/usr/local/bin'],
    unless  => 'pip3 show pylint',
    require => Package['python3-pip'],
  }

}