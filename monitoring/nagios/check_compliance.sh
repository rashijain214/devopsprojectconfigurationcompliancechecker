#!/bin/bash
# Custom Nagios plugin — checks compliance report status
# Puppet deploys this to /usr/lib/nagios/plugins/

REPORT_DIR="/var/reports/compliance-checker"
CRITICAL_THRESHOLD=2   # hours
WARNING_THRESHOLD=1    # hours

# Check if report directory exists
if [ ! -d "$REPORT_DIR" ]; then
  echo "CRITICAL: Report directory $REPORT_DIR not found"
  exit 2
fi

# Find most recent report
LATEST_REPORT=$(ls -t "$REPORT_DIR"/*.json 2>/dev/null | head -1)

if [ -z "$LATEST_REPORT" ]; then
  echo "CRITICAL: No compliance reports found in $REPORT_DIR"
  exit 2
fi

# Check report age
REPORT_AGE=$(( ($(date +%s) - $(stat -c %Y "$LATEST_REPORT")) / 3600 ))

if [ "$REPORT_AGE" -ge "$CRITICAL_THRESHOLD" ]; then
  echo "CRITICAL: Latest report is ${REPORT_AGE} hours old: $LATEST_REPORT"
  exit 2
elif [ "$REPORT_AGE" -ge "$WARNING_THRESHOLD" ]; then
  echo "WARNING: Latest report is ${REPORT_AGE} hours old: $LATEST_REPORT"
  exit 1
fi

# Check report content for critical violations
CRITICAL_COUNT=$(python3 -c "
import json, sys
with open('$LATEST_REPORT') as f:
    data = json.load(f)
print(data['summary']['critical'])
" 2>/dev/null)

if [ "$CRITICAL_COUNT" -gt "0" ]; then
  echo "CRITICAL: ${CRITICAL_COUNT} critical compliance violations found!"
  exit 2
fi

VIOLATIONS=$(python3 -c "
import json
with open('$LATEST_REPORT') as f:
    data = json.load(f)
print(data['summary']['total_violations'])
" 2>/dev/null)

if [ "$VIOLATIONS" -gt "0" ]; then
  echo "WARNING: ${VIOLATIONS} compliance violations found in latest report"
  exit 1
fi

echo "OK: Compliance check passed - 0 violations. Report: $LATEST_REPORT"
exit 0