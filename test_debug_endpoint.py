#!/usr/bin/env python3
"""Quick script to exercise debug endpoints on the backend"""
import requests

BASE = "http://127.0.0.1:8000"


def run_checks():
    print("GET / ->", requests.get(BASE + "/").text)
    print("GET /debug ->", requests.get(BASE + "/debug").json())
    print("POST /echo ->", requests.post(BASE + "/echo", data="hello world", headers={"Content-Type": "text/plain"}).json())


if __name__ == '__main__':
    run_checks()
