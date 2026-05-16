# Threat Model — EPUB Metadata Normalizer
Local‑First AI/ML Metadata Enrichment Pipeline  
Author: Jennifer

This document outlines a lightweight STRIDE‑style threat model for the EPUB Metadata Normalizer.

---

## 1. Scope

- Local execution on a user workstation
- Access to EPUB files stored locally or via OneDrive
- Outbound API calls to an LLM provider
- Local audit logs and state tracking

---

## 2. Assets

| Asset | Description |
|-------|-------------|
| EPUB files | User’s personal ebook library |
| Extracted metadata | Titles, authors, identifiers |
| Text samples | Snippets extracted for AI inference |
| API keys | Stored in `.env` |
| Audit logs | `audit_log.csv` |
| State file | `state.json` |

---

## 3. STRIDE Analysis

### Spoofing
- Risk: Impersonation of AI provider  
- Mitigation: HTTPS, official SDKs, no custom endpoints

### Tampering
- Risk: Local file modification  
- Mitigation: Trusted local environment, human‑readable logs

### Repudiation
- Risk: No record of actions  
- Mitigation: CSV audit log + state file

### Information Disclosure
- Risk: EPUB content sent to LLM  
- Mitigation: Truncated samples, no raw text stored, user‑controlled folder

### Denial of Service
- Risk: Large libraries overwhelm API  
- Mitigation: MAX_FILES, DRY_RUN, state tracking

### Elevation of Privilege
- Risk: Script used for unintended operations  
- Mitigation: No shell execution, no dynamic code loading

---

## Summary

This project is designed for a trusted local environment with controlled outbound API calls.  
Primary goals:

- Protect API keys  
- Avoid unnecessary data exposure  
- Maintain a clear audit trail  
- Prevent accidental reprocessing  
