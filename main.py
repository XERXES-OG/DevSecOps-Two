import requests
import json
from datetime import datetime

# =====================================
# CONFIGURATION
# =====================================

API_KEY = ""

MOBSF_URL = "http://localhost:8000"

APK_URL = ""

APK_FILE = ""

JSON_REPORT = "mobsf-scan.json"

PDF_REPORT = "mobsf-report.pdf"

HEADERS = {
    "X-Mobsf-Api-Key": API_KEY
}


# =====================================
# LOGGING
# =====================================

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# =====================================
# DOWNLOAD APK
# =====================================

def download_apk():
    log("Downloading APK from GitHub")

    response = requests.get(APK_URL)
    response.raise_for_status()

    with open(APK_FILE, "wb") as file:
        file.write(response.content)

    log(f"APK saved as {APK_FILE}")


# =====================================
# UPLOAD APK TO MOBSF
# =====================================
def upload_apk():

    import os

    log("Uploading APK to MobSF")

    print("APK File:", APK_FILE)
    print("APK Size:", os.path.getsize(APK_FILE), "bytes")

    with open(APK_FILE, "rb") as file:

        files = {
            "file": (
                APK_FILE,
                file,
                "application/vnd.android.package-archive"
            )
        }

        response = requests.post(
            f"{MOBSF_URL}/api/v1/upload",
            headers=HEADERS,
            files=files
        )

    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

    response.raise_for_status()

    data = response.json()

    apk_hash = data["hash"]

    log("Upload completed")
    log(f"Hash: {apk_hash}")

    return apk_hash
# =====================================
# SCAN APK
# =====================================

def scan_apk(apk_hash):
    log("Starting MobSF scan")

    response = requests.post(
        f"{MOBSF_URL}/api/v1/scan",
        headers=HEADERS,
        data={
            "hash": apk_hash
        }
    )

    response.raise_for_status()

    scan_result = response.json()

    with open(JSON_REPORT, "w", encoding="utf-8") as report:
        json.dump(scan_result, report, indent=4)

    log(f"JSON report saved -> {JSON_REPORT}")


# =====================================
# DOWNLOAD PDF REPORT
# =====================================

def download_pdf(apk_hash):
    log("Downloading PDF report")

    response = requests.post(
        f"{MOBSF_URL}/api/v1/download_pdf",
        headers=HEADERS,
        data={
            "hash": apk_hash
        }
    )

    response.raise_for_status()

    with open(PDF_REPORT, "wb") as pdf:
        pdf.write(response.content)

    log(f"PDF report saved -> {PDF_REPORT}")


# =====================================
# MAIN PIPELINE
# =====================================

def main():
    try:
        download_apk()

        apk_hash = upload_apk()

        scan_apk(apk_hash)

        download_pdf(apk_hash)

        log("Pipeline completed successfully")

    except Exception as error:
        log("Pipeline failed")
        print(error)


if __name__ == "__main__":
    main()
