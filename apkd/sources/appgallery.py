from datetime import datetime
from uuid import uuid4

import requests
from user_agent import generate_user_agent

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource

import string
import random
from urllib.parse import urlencode
import time
import json


class Source(BaseSource):
    headers: dict

    def __init__(self) -> None:
        super().__init__()
        self.name = 'AppGallery'
        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US;q=0.5',
            'network-out': 'NWK(time/20240319173023017)',
            'net-msg-id': str(uuid4()),
            'network-vendor': 'NWK',
            'network-in': 'NWK(time/20240319173023016)',
            'sysUserAgent': 'Mozilla/5.0 (Linux; Android 14; 23127PN0CG Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.106 Mobile Safari/537.36',
        }

        # 'advPlatform=0&apsid=1710869752000&arkMaxVersion=0&arkMinVersion=0&arkSupport=0&authorization=%7B%22deviceId%22%3A%220580df6fffb017a9fea864161b0fdc3d8e31ad0cbda34f8dc6479a0c458852f6%22%2C%22deviceType%22%3A%223%22%2C%22serviceToken%22%3A%22sid%3A1027162%3A0dd65f9111c732c5e274984d2ba56ac3a4065a6e3c27bfc0%22%7D&brand=Xiaomi&callType=default&callWay=2&callerAppSigns=%5B%5D&clickAreaType=0&clientPackage=com.huawei.appmarket&cno=4010001&code=0200&contentPkg=&deviceId=0580df6fffb017a9fea864161b0fdc3d8e31ad0cbda34f8dc6479a0c458852f6&deviceIdRealType=3&deviceIdType=9&deviceSpecParams=%7B%22abis%22%3A%22arm64-v8a%22%2C%22deviceFeatures%22%3A%22U%2C0g%2CP%2C1O%2CB%2C0c%2Ce%2C0J%2Cp%2Ca%2Cb%2C04%2CA%2Cm%2C08%2C03%2CC%2CS%2C0G%2C1Q%2Cq%2C1F%2CL%2C2%2C6%2CY%2CZ%2C1P%2C0M%2C1G%2C2L%2C1B%2Cf%2C1%2C07%2C8%2C9%2C2K%2C1H%2C1I%2CO%2CH%2C0E%2CW%2Cx%2CG%2Co%2C06%2C3%2CR%2Cd%2CQ%2Cn%2Cy%2CT%2Ci%2Cr%2Cu%2Cl%2C4%2CN%2CM%2C01%2C09%2CV%2C7%2C5%2C0H%2Cg%2Cc%2CF%2Ct%2C0L%2C0W%2C1N%2C0X%2Ck%2C00%2Cz%2C19%2CK%2C0K%2CE%2C0A%2C02%2CI%2C1E%2CJ%2C1C%2Cj%2CD%2Ch%2C05%2C1A%2CX%2Cv%2C0e%2Ccom.quicinc.voice.assist.asr%2Ccom.quicinc.voice.assist.uvr%2Candroid.software.telecom%2Candroid.hardware.telephony.subscription%2Candroid.hardware.telephony.data%2Candroid.hardware.telephony.mbms%2Candroid.hardware.sensor.dynamic.head_tracker%2Candroid.software.erofs%2Candroid.software.device_lock%2Ccom.google.android.feature.PIXEL_2017_EXPERIENCE%2Ccom.google.lens.feature.CAMERA_INTEGRATION%2Cxiaomi.hardware.p2p_getlinklayer%2Ccom.google.android.feature.PIXEL_2018_EXPERIENCE%2Candroid.hardware.telephony.messaging%2Ccom.google.android.feature.PIXEL_2019_EXPERIENCE%2Candroid.hardware.telephony.calling%2Candroid.software.window_magnification%2Candroid.hardware.telephony.radio.access%2Ccom.google.android.feature.GOOGLE_BUILD%2Cxiaomi.hardware.p2p_165chan%2Candroid.software.ipsec_tunnel_migration%2Ccom.android.se%2Ccom.google.android.feature.PIXEL_EXPERIENCE%2Candroid.software.sdksandbox.sdk_install_work_profile%2Candroid.software.credentials%2Candroid.software.device_id_attestation%2Ccom.qualcomm.qti.feature.DCF_OFFLOAD%2Ccom.google.android.feature.PIXEL_2019_MIDYEAR_EXPERIENCE%2Cxiaomi.hardware.p2p_staticip%2Ccom.google.lens.feature.IMAGE_INTEGRATION%2Ccom.google.android.apps.dialer.call_recording_audio%2Ccom.google.android.apps.dialer.SUPPORTED%2Ccom.google.android.feature.GOOGLE_EXPERIENCE%2Ccom.google.android.feature.EXCHANGE_6_2%2Ccom.quicinc.voice.assist%2Candroid.software.virtualization_framework%2Cxiaomi.hardware.p2p_160m%2Candroid.hardware.keystore.app_attest_key%2Ccom.google.android.feature.PREMIER_TIER%22%2C%22dpi%22%3A480%2C%22glVersion%22%3A%22OpenGL%20ES%203.2%20V%400744.12%20%28GIT%4062c1f322ce%2C%20Id0077aad60%2C%201700555917%29%20%28Date%3A11%5C%2F21%5C%2F23%29%22%2C%22openglExts%22%3A%22%22%2C%22preferLan%22%3A%22en%22%2C%22usesLibrary%22%3A%221Q%2C3F%2C5%2C6%2C23%2C4%2C2c%2C2l%2C1H%2C1f%2C1s%2Cn%2C2Z%2CG%2CG%2C2m%2C04%2C0y%2C3P%2C13%2C3Q%2C3R%2C3S%2C10%2C3%2C09%2C0r%2CA%2C0U%2C9%2C8%2C03%2C28%2C2%2Cb%2C0I%2C3i%2C0H%2C0J%2C08%2C7%2CF%2Cd%2C0V%2CD%2CB%2C3l%2CC%2C0X%2C3n%2C05%2C0Y%2C0Z%2C21%2Cvendor.qti.ims.connection-V1.0-java%2Ccom.android.hotwordenrollment.common.util%2Cvendor.xiaomi.hardware.misys-V1.0-java%2Cvendor.qti.ims.rcsuce-V1.0-java%2Ccom.qualcomm.qti.uimGba.uimgbalibrary%2Cvendor.qti.ims.rcsuce-V1.1-java%2Clibxmi_slow_motion_mein.so%2Cvendor.qti.ims.rcsuce-V1.2-java%2Cdpmapi%2Ccamerax-vendor-extensions.jar%2Ccom.qualcomm.qti.uimGbaManager.uimgbamanagerlibrary%2Cglobal-cleaner-empty.jar%2Ccom.qualcomm.qmapbridge%2Clibmisys_jni.xiaomi.so%2Cvendor.qti.ims.datachannelservice-V1-java%2ClibQEGA.qti.so%2Ccom.qualcomm.qti.remoteSimlock.manager.remotesimlockmanagerlibrary%2Cvendor.xiaomi.hardware.misys-V4.0-java%2Ccom.miui.system%2Cvendor.qti.ims.connectionaidlservice-V1-java%2Clibmialgo_utils.so%2Cvendor.qti.ims.rcsuceaidlservice-V1-java%2Ccom.wapi.wapicertstore%2Cvendor.xiaomi.hardware.misys.V3_0%2Ccom.st.android.nfc_extensions%2Csecurity-device-credential-sdk.jar%2Ccom.nxp.nfc.nq%2Cdatachannellib%2Cvendor.xiaomi.hardware.misys-V2.0-java%2CMiuiSettingsSearchLib.jar%2Cvendor.qti.ims.rcssipaidlservice-V1-java%2Ccom.qualcomm.qti.uim.uimservicelibrary%2Ccom.xiaomi.nfc%2Cvendor.qti.ims.factory-V2.0-java%2Cvendor.qti.ims.factory-V2.1-java%2Ccom.xiaomi.slalib%2Cvendor.qti.ims.factory-V2.2-java%2Clibmialgo_ai_vision.so%2Ccom.xiaomi.NetworkBoost%2Cvendor.xiaomi.hardware.bgservice-V1.0-java%2ClibQOC.qti.so%2Cgson.jar%2ClibSNPE.so%2Ccom.google.android.dialer.support%2Clibmiphone_capture_bokeh.so%2Cvendor.qti.ims.rcssip-V1.0-java%2Cvendor.qti.ims.rcssip-V1.1-java%2Cvendor.qti.ims.rcssip-V1.2-java%2Cmiui-cameraopt%2Clibmiocr.so%2Cvendor.qti.ims.factoryaidlservice-V1-java%2Cmicloud-sdk%22%7D&downloadFlag=0&fid=0&gaid=fd4ce8d2-18af-4e73-b66c-7f3174e92580&globalTrace=null&gradeLevel=0&gradeType=&hardwareType=0&installedVersionCode=2016008943&installedVersionName=124.0&isSupportPage=1&manufacturer=Xiaomi&maxResults=25&method=client.agdSecurityVerification&net=1&oaidTrack=1&originalDeeplink=market%3A%2F%2Fdetails%3Fid%3D{pkg}&osv=14&outside=0&pkgName={pkg}&recommendSwitch=-1&reqPageNum=1&roamingTime=0&runMode=2&serviceType=0&shellApkVer=0&sid=1710869752500&sign=u90035905i0121062000001007u003500a0000000500200000010000000010000070230b0100011000000%4046CC28CBB85C45259311A01057E9CB41&translateFlag=0&ts=1710869752700&uriParams=%7B%22callType%22%3A%22default%22%2C%22cdcParams%22%3A%22%7B%5C%22accessID%5C%22%3A%5C%22%5C%22%2C%5C%22channelId%5C%22%3A%5C%22%5C%22%2C%5C%22detailType%5C%22%3A%5C%22%5C%22%2C%5C%22extraParam%5C%22%3A%5C%22%5C%22%2C%5C%22id%5C%22%3A%5C%22{pkg}%5C%22%2C%5C%22initParam%5C%22%3A%5C%22%5C%22%2C%5C%22s%5C%22%3A%5C%22%5C%22%7D%22%2C%22downloadParams%22%3A%22%22%2C%22installType%22%3A%22%22%7D&ver=1.1'

    def get_app_info(self, pkg: str) -> App:
        app: App = super().get_app_info(pkg)
        response = requests.post('https://store-drru.hispace.dbankcloud.ru/hwmarket/api/clientApi', headers=self.headers, data=urlencode({
            'callWay': '2',
            'clientPackage': 'com.huawei.appmarket',
            'code': '0200',
            'deviceId': self.generate_device_id(),
            'deviceIdType': 9,
            'method': 'client.agdSecurityVerification',
            'net': 1,
            'pkgName': pkg,
            'sign': 'u90035905i0121062000001007u003500a0000000500200000010000000010000070230b0100011000000@46CC28CBB85C45259311A01057E9CB41',
            'ts': round(time.time()),
            'uriParams': json.dumps({
                'callType': 'default',
                'cdcParams': json.dumps({
                    'accessID': '',
                    'channelId': '',
                    'detailType': '',
                    'extraParam': '',
                    'id': pkg,
                    'initParam': '',
                    's': ''
                }),
                'downloadParams': '',
                'installType': ''
            }),
            'ver': '1.1'
        }))
        json_code = response.json()
        if 'titleType' not in json_code or json_code['titleType'] is None:
            raise AppNotFoundError()
        data = None
        for layout_data in json_code['layoutData']:
            if data is not None:
                break
            # apps direct from appgallery has appid from 10 characters - "C" + 9 digits
            # apps from third-party services has appid from 19 characters - "C" + 18 digits
            for data_list in layout_data['dataList']:
                if 'appid' in data_list and len(data_list['appid']) == 10 and 'package' in data_list and data_list['package'] == pkg:
                    data = data_list
                    break

        if data is None:
            raise AppNotFoundError()
        version_name = data['versionName']
        version_code = int(data['versionCode'])
        file_size = data['fullSize']
        download_url = data['downurl']

        app.set_versions(
            [AppVersion(version_name, version_code, file_size, self, download_link=download_url)])
        return app

    def generate_device_id(self) -> str:
        template = [*(string.digits + string.ascii_lowercase)] * 2
        random.shuffle(template)
        return ''.join(template[:64])