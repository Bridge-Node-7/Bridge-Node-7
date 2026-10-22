#!/usr/bin/env python3
"""Minimal regression checks without embedding live identifiers."""
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("privacy",Path(__file__).resolve().parent/"privacy_preflight.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test():
    assert "personal-email" in m.categories("example@"+"gmail.com")
    assert "personal-email" not in m.categories("security@enterprise.example")
    assert "phone-number" in m.categories("213"+"-555-"+"0199")
    assert "local-home-path" in m.categories("C:"+chr(92)+"Users"+chr(92)+"example")
    assert "private-key" in m.categories("-----BEGIN "+"PRIVATE KEY-----")
    assert "service-credential" in m.categories("AKIA"+"A"*16)
    assert "github-token" in m.categories("ghp_"+"a"*40)
    assert "sensitive-file" in m.path_categories(".env")
    assert not m.path_categories(".env.example")
    assert "sensitive-filetype" in m.path_categories("credential.p12")
    workflow=(Path(__file__).resolve().parents[1]/".github/workflows/privacy-preflight.yml").read_text(encoding="utf-8")
    assert "ref: main" not in workflow
    assert "policy_ref:" in workflow
    assert "required: true" in workflow
    assert 'ref: ${{ inputs.policy_ref }}' in workflow
    assert 'ref: ${{ github.event.pull_request.head.sha || github.sha }}' in workflow
    print("PASS privacy preflight smoke checks")
if __name__=="__main__":
    test()
