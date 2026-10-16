import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
Item {
 width:760;height:250
 T.Button {id:before;x:10;y:10;width:100;height:40;text:"Before";focusPolicy:Qt.StrongFocus}
 BleeckerOTPInput {id:otp;x:150;y:10;code:"";onCodeRequested:value=>code=value}
 T.Button {id:after;x:450;y:10;width:100;height:40;text:"After";focusPolicy:Qt.StrongFocus}
 TestCase {name:"OTPFocusProbe";when:windowShown
  function test_traversal(){
   before.forceActiveFocus();verify(before.activeFocus)
   keyClick(Qt.Key_Tab);verify(otp.editor.activeFocus,"Forward tab into editor")
   keyClick(Qt.Key_Tab);verify(after.activeFocus,"Forward tab out")
   keyClick(Qt.Key_Backtab);verify(otp.editor.activeFocus,"Backtab into editor")
   keyClick(Qt.Key_Backtab);verify(before.activeFocus,"Backtab out")
  }
 }
}
