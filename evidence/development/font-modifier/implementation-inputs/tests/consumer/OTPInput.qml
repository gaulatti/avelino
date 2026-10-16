import QtQuick
import Avelino

Window {
    id:window;width:840;height:580;visible:true;title:"Avelino OTP input"
    color:BleeckerTheme.palette.background
    readonly property real fixtureTextScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    property var model:({code:"",length:6,disabled:false,observeOnly:false,publishesWrites:false,deferredOwner:false})
    property var requests:[]
    property var pendingWrites:[]
    Component.onCompleted:{BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=fixtureTextScale;BleeckerTheme.reducedMotion=true}
    function writeCode(value){model=Object.assign({},model,{code:value});if(model.publishesWrites)otp.notifyCodeWrite()}
    function flushWrites(){const values=pendingWrites;pendingWrites=[];for(const value of values)writeCode(value)}
    function externalCode(value){model=Object.assign({},model,{code:value})}
    function externalLength(value){model=Object.assign({},model,{length:value})}
    BleeckerOTPInput {
        id:otp;objectName:"consumerOTP";x:24;y:30
        code:window.model.code;length:window.model.length;enabled:!window.model.disabled
        onCodeRequested:value=>{
            window.requests=window.requests.concat([value])
            if(window.model.observeOnly)return
            if(window.model.deferredOwner)window.pendingWrites=window.pendingWrites.concat([value])
            else window.writeCode(value)
        }
    }
    BleeckerOTPInput {objectName:"otpPartial";x:24;y:120;code:"123";onCodeRequested:value=>code=value}
    BleeckerOTPInput {objectName:"otpUnicode";x:24;y:210;code:"𝟙1️⃣一٢";onCodeRequested:value=>code=value}
    BleeckerOTPInput {objectName:"otpZero";x:24;y:300;code:"A12345";length:0;onCodeRequested:value=>code=value}
    BleeckerOTPInput {objectName:"otpNarrow";x:440;y:30;width:12;code:"123456";onCodeRequested:value=>code=value}
    BleeckerOTPInput {objectName:"otpDisabled";x:440;y:120;code:"A12345";enabled:false}
    BleeckerOTPInput {objectName:"otpObserve";x:440;y:210;code:"12"}
    BleeckerOTPInput {objectName:"otpRtl";x:440;y:300;code:"١٢٣٤";LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true;onCodeRequested:value=>code=value}
    BleeckerTextField {objectName:"otpOutsideField";x:24;y:450;width:320;placeholderText:"Continue editing"}
}
