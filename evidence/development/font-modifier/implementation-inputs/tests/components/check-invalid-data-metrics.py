#!/usr/bin/env python3
"""Reject malformed data-display contracts through real QML construction."""
from pathlib import Path
import resource,subprocess,sys,tempfile
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
runner,imports=sys.argv[1:]
icon='icon:Component {Item {implicitWidth:18;implicitHeight:18}}'
cases=[('BleeckerMetric {label:"Readers";value:1;format:"unknown"}',b'Unknown Bleecker metric format'),('BleeckerMetric {label:"Readers";value:1;maximumWidth:-2}',b'Text maximum width must be nonnegative or -1'),('BleeckerIconBadge {size:"sm";'+icon+'}',b'Unknown icon-badge size'),('BleeckerIconBadge {variant:"unknown";'+icon+'}',b'Unknown icon-badge variant'),('BleeckerStatCard {label:"Readers";value:1;delta:"wrong";'+icon+'}',b'Stat-card delta must be a number or null'),('BleeckerStatCard {label:"Readers";value:1;maximumWidth:-2;'+icon+'}',b'Text maximum width must be nonnegative or -1'),('BleeckerKbd {key:"K";maximumWidth:-2}',b'Text maximum width must be nonnegative or -1')]
for declaration,expected in cases:
 with tempfile.TemporaryDirectory(prefix='avelino-invalid-metrics-') as folder:
  p=Path(folder)/'tst_invalid.qml';p.write_text('import QtQuick\nimport QtTest\nimport Avelino\nItem {width:400;height:300\n'+declaration+'\nTestCase {when:windowShown;function test_refusal(){fail("Invalid metric accepted")}}}')
  result=subprocess.run([runner,'-import',imports,'-input',str(p)],capture_output=True);assert result.returncode!=0 and expected in result.stdout+result.stderr,(declaration,result.stdout+result.stderr)
print('Data-display startup refused seven invalid size/variant/format/delta/width contracts')
