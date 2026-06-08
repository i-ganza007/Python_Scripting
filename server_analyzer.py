import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from email_sender import email_sender
import requests
from dotenv import dotenv_values


CONFIG_KEYS = ["HEALTHY", "SLOW", "FAILING", "VALID"]
MAIL_KEYS = ["EMAIL_SENDER", "EMAIL_PASSWORD", "EMAIL_RECIPIENT"]
CONFIG_FILE = Path(__file__).with_name(".env")


def clean_value(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in ('"', "'", "`"):
        cleaned = cleaned[1:-1]
    return cleaned or None


def load_servers():
    env_values = {key: clean_value(os.getenv(key)) for key in CONFIG_KEYS}
    if all(env_values.values()):
        return [env_values[key] for key in CONFIG_KEYS]

    file_values = dotenv_values(CONFIG_FILE) if CONFIG_FILE.exists() else {}
    servers = []
    missing_keys = []

    for key in CONFIG_KEYS:
        value = env_values[key] or clean_value(file_values.get(key))
        if value is None:
            missing_keys.append(key)
        else:
            servers.append(value)

    if missing_keys:
        raise RuntimeError(
            "Missing server configuration. Set HEALTHY, SLOW, FAILING, and VALID as environment variables "
            f"or define them in {CONFIG_FILE.name}. Missing: {', '.join(missing_keys)}"
        )

    return servers


def load_mail_config():
    env_values = {key: clean_value(os.getenv(key)) for key in MAIL_KEYS}
    file_values = dotenv_values(CONFIG_FILE) if CONFIG_FILE.exists() else {}

    mail_config = {}
    missing_keys = []

    for key in MAIL_KEYS:
        value = env_values[key] or clean_value(file_values.get(key))
        if value is None:
            missing_keys.append(key)
        else:
            mail_config[key] = value

    if missing_keys:
        raise RuntimeError(
            "Missing email notification config. Set EMAIL_SENDER, EMAIL_PASSWORD, and EMAIL_RECIPIENT "
            f"as environment variables or define them in {CONFIG_FILE.name}. Missing: {', '.join(missing_keys)}"
        )

    return mail_config


def notify_failure(result):
    mail_config = load_mail_config()
    message = (
        f"Service check failed for {result['url']}\n"
        f"Status: {result['status'].upper()}\n"
        f"Status code: {result['status_code']}\n"
        f"Attempts: {result['attempts']}\n"
        f"Error: {result['error']}\n"
    )
    email_sender(
        mail_config["EMAIL_SENDER"],
        mail_config["EMAIL_PASSWORD"],
        mail_config["EMAIL_RECIPIENT"],
        message,
    )


def check_server(url, retries=2, timeout=5):
    attempts = retries + 1
    last_error = None
    last_status_code = None
    last_response_time = 0.0

    for attempt in range(1, attempts + 1):
        start = time.perf_counter()
        try:
            response = requests.get(url, timeout=timeout)
            last_status_code = response.status_code
            last_response_time = (time.perf_counter() - start) * 1000
            if 200 <= response.status_code <= 299:
                return {
                    "url": url,
                    "status": "healthy",
                    "status_code": response.status_code,
                    "response_time_ms": last_response_time,
                    "attempts": attempt,
                    "slow": last_response_time >= 500,
                    "error": None,
                }
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_response_time = (time.perf_counter() - start) * 1000
            last_error = str(exc)
            last_status_code = None

        if attempt < attempts:
            continue

    return {
        "url": url,
        "status": "failing",
        "status_code": last_status_code,
        "response_time_ms": last_response_time,
        "attempts": attempts,
        "slow": False,
        "error": last_error,
    }


def check_all_servers():
    servers = load_servers()
    with ThreadPoolExecutor(max_workers=len(servers)) as executor:
        return list(executor.map(check_server, servers))


def format_result(result):
    if result["status"] == "healthy":
        output = f'{result["url"]}    — OK ({result["status_code"]})    — {result["response_time_ms"]:.0f}ms'
        if result["slow"]:
            output += "  [slow]"
        return output

    if result["status_code"] is None:
        return f'{result["url"]}    — TIMEOUT'

    return f'{result["url"]}    — DOWN ({result["status_code"]})'


def main():
    results = check_all_servers()
    failed_results = []

    for result in results:
        print(format_result(result))
        if result["status"] != "healthy":
            failed_results.append(result)
            notify_failure(result)

    if failed_results:
        print()
        print("Failed services: " + ", ".join(result["url"] for result in failed_results))


if __name__ == "__main__":
    main()
