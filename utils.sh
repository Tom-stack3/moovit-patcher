#!/bin/bash
source secrets
ADB="/mnt/c/Program Files/Genymobile/Genymotion/tools/adb.exe"
FRIDA="/mnt/c/Users/$USERNAME/AppData/Local/Programs/Python/Python312/Scripts/frida.exe"
PATCHES_PROJECT="~/dev/moovit/moovit-patcher"

create_rev_proxy_first_time() {
    mkdir -p /tmp/burp && cd /tmp/burp
    if [ "$(ls -A /tmp/burp)" ]; then
        rm /tmp/burp/*
    fi
    echo "[+] Go to Burp Suite -> Proxy -> Options -> Proxy Listeners -> Add -> Bind to port 8081 (All interfaces)"
    echo "[+] Export the certificate in DER format and save it as burp.der in Documents"
    echo "[+] Press Enter when you are ready..."
    read
    "$ADB" shell settings put global http_proxy localhost:3333
    "$ADB" reverse tcp:3333 tcp:8081
    cp /mnt/c/Temp/burp.der .
    echo "[+] Certificate saved as burp.der"
    openssl x509 -inform DER -in burp.der -out burp.pem
    HASH=$(openssl x509 -inform PEM -subject_hash_old -in burp.pem | head -1)
    mv burp.pem $HASH.0
    echo "[+] Certificate renamed to: $HASH"
    "$ADB" root
    "$ADB" remount || "[-] Unable to remount /system, device might not be rooted! Consider using Android 9.0 or lower in Genymotion"
    "$ADB" push $HASH.0 /sdcard/
    "$ADB" shell mv /sdcard/$HASH.0 /system/etc/security/cacerts/
    "$ADB" shell chmod 644 /system/etc/security/cacerts/$HASH.0
    echo "[+] Certificate installed successfully!"
}

create_rev_proxy_when_cert_installed() {
    echo "[+] Go to Burp Suite -> Proxy -> Options -> Proxy Listeners -> Add -> Bind to port 8081 (All interfaces)"
    echo "[+] Press Enter when you are ready..."
    read
    "$ADB" shell settings put global http_proxy localhost:3333
    "$ADB" reverse tcp:3333 tcp:8081
    echo "[+] Proxy created successfully!"
}

apply_patches() {
    cd $PATCHES_PROJECT
    echo "[+] Applying patches..."
    python main.py -p ./moovit_5.145.apk -o moovitpatched_5.145.apk
    echo "[+] Patches applied successfully!"
    install_patched_apk
}

install_patched_apk() {
    echo "[+] Uninstalling app and installing patched APK..."
    "$ADB" uninstall com.tranzmate && echo "Uninstalled original app successfully" || echo "[-] Original app not found!"
    echo "[+] Installing patched APK..."
    "$ADB" install -r moovitpatched_5.145.apk && echo "[+] Patched APK installed successfully" || echo "[-] Failed to install patched APK"
}

install_original_apk() {
    echo "[+] Uninstalling app and installing original APK..."
    "$ADB" uninstall com.tranzmate && echo "Uninstalled original app successfully" || echo "[-] Original app not found!"
    echo "[+] Installing original APK..."
    "$ADB" install -r moovit_5.145.apk && echo "[+] Patched APK installed successfully" || echo "[-] Failed to install patched APK"
}

run_app_with_frida() {
    echo "[+] Running app with Frida..."
    "$FRIDA" -U -f com.tranzmate -l frida.js
}

if [ "$1" == "1" ]; then
    create_rev_proxy_first_time
fi
if [ "$1" == "2" ]; then
    create_rev_proxy_when_cert_installed
fi
if [ "$1" == "3" ]; then
    apply_patches
fi
if [ "$1" == "4" ]; then
    install_patched_apk
fi
if [ "$1" == "5" ]; then
    install_original_apk
fi
if [ "$1" == "6" ]; then
    run_app_with_frida
fi
if [ -z "$1" ]; then
    echo "Usage: $0 <1|2>"
    echo "1 - Create reverse proxy with Burp Suite for the first time"
    echo "2 - Create reverse proxy with Burp Suite when certificate is already installed on the device"
    echo "3 - Apply patches to app and install patched APK"
    echo "4 - Install patched APK"
    echo "5 - Install original APK"
    echo "6 - Run app with Frida"
fi
