#!/bin/bash
source secrets
ADB="/mnt/c/Program Files/Genymobile/Genymotion/tools/adb.exe"
FRIDA="/mnt/c/Users/$USERNAME/AppData/Local/Programs/Python/Python312/Scripts/frida.exe"
OBJECTION="/mnt/c/Users/$USERNAME/AppData/Local/Programs/Python/Python312/Scripts/objection.exe"
PACKAGE_NAME="com.tranzmate"

create_rev_proxy_first_time() {
    mkdir -p /tmp/burp && cd /tmp/burp
    if [ "$(ls -A /tmp/burp)" ]; then
        rm /tmp/burp/*
    fi
    echo "[+] Go to Burp Suite -> Proxy -> Proxy Settings -> Proxy Listeners -> Add -> Bind to port 8081 (All interfaces)"
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
    echo "[+] Applying patches..."
    python main.py --skip-prompts -p ./moovit_5.145.apk -o moovitpatched_5.145.apk -gakey "$CUSTOM_GOOGLE_API_KEY"
    echo "[+] Patches applied successfully!"
    install_patched_apk
}

install_patched_apk() {
    echo "[+] Uninstalling app and installing patched APK..."
    "$ADB" uninstall "$PACKAGE_NAME" && echo "Uninstalled original app successfully" || echo "[-] Original app not found!"
    echo "[+] Installing patched APK..."
    "$ADB" install -r moovitpatched_5.145.apk && echo "[+] Patched APK installed successfully" || echo "[-] Failed to install patched APK"
}

install_original_apk() {
    echo "[+] Uninstalling app and installing original APK..."
    "$ADB" uninstall "$PACKAGE_NAME" && echo "Uninstalled original app successfully" || echo "[-] Original app not found!"
    echo "[+] Installing original APK..."
    "$ADB" install -r moovit_5.145.apk && echo "[+] Patched APK installed successfully" || echo "[-] Failed to install patched APK"
}

run_app_with_frida() {
    echo "[+] Running app with Frida..."
    "$FRIDA" -U -f "$PACKAGE_NAME" -l frida.js
}

run_frida_server() {
    "$ADB" shell ps | grep frida-server && echo "Frida server is already running!" && return
    echo "[+] Running Frida on the device..."
    echo "/data/local/tmp/frida-server &" | "$ADB" shell su
}

run_app_with_objection() {
    echo "[+] Running app with Objection..."
    "$OBJECTION" --gadget "$PACKAGE_NAME" explore
}

if [ "$1" == "1" ]; then
    create_rev_proxy_first_time
elif [ "$1" == "2" ]; then
    create_rev_proxy_when_cert_installed
elif [ "$1" == "3" ]; then
    apply_patches
elif [ "$1" == "4" ]; then
    install_patched_apk
elif [ "$1" == "5" ]; then
    install_original_apk
elif [ "$1" == "6" ]; then
    run_frida_server
elif [ "$1" == "7" ]; then
    run_app_with_frida
elif [ "$1" == "8" ]; then
    run_app_with_objection
else
    echo "Usage: $0 <option>"
    echo "1 - Create reverse proxy with Burp Suite for the first time"
    echo "2 - Create reverse proxy with Burp Suite when certificate is already installed on the device"
    echo "3 - Apply patches to app and install patched APK"
    echo "4 - Install patched APK"
    echo "5 - Install original APK"
    echo "6 - Run Frida server on the device"
    echo "7 - Run app with Frida script"
    echo "8 - Run app with Objection"
fi
