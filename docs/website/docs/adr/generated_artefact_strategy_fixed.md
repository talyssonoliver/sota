# ADR‑CLN‑01 – Generated Artifact Strategy

**Status**              : Proposed
**Date**                : 2025‑06‑27
**Supersedes / Amends** : –
**Authors**             : Platform & DevEx Guild
**Reviewers**           : Security, QA, DevOps
**Decision Window**     : ≤ 2025‑07‑31

---

## 1 | Context

* Hexagonal architecture mandates a clean **core domain**; generated / ephemeral output must not leak into VCS.
* Current repo (≈ 1 704 files, 269 k LOC) contains ≈ 61 % runtime artefacts (logs, test outputs, archives, CI reports).
* Pollution inflates clone time, diff noise, and Sonar metrics; obscures true defect density and slows pipelines.

## 2 | Problem Statement

> **Goal** — Eliminate non‑source artefacts from the **primary code surface** while preserving traceability & auditability.

## 3 | Decision Drivers

|  ID   |  Driver                    | Rationale                                              |
| ----- | -------------------------- | ------------------------------------------------------ |
|  D‑01 | Maintain **Sonar ≥ A**     | Metrics skew when artefacts included.                  |
|  D‑02 | **Test determinism**       | Tests must write to isolated temp paths.               |
|  D‑03 | **Regulatory audit trail** | Logs retained ≥ 90 days (PCI‑DSS §10).                 |
|  D‑04 | **CI runtime ≤ 12 min**    | Large repos slow checkout & diff‑based jobs.           |
|  D‑05 | **Zero Dev friction**      | Local workflow unchanged; `pytest` still "just works". |

## 4 | Considered Options

|  Option                                     | Keep in VCS | Move to Git LFS | External Storage (S3) |
| ------------------------------------------- | ----------- | --------------- | --------------------- |
|  A. Status Quo                              | ✔           | –               | –                     |
|  B. Git LFS for artefacts                   | Partial     | ✔               | –                     |
|  C. **Dedicated artefact buckets** (chosen) | –           | –               | ✔                     |

*Option C* chosen – aligns with DevOps bucket policy, avoids LFS friction, meets audit retention.

## 5 | Decision

1. **Classify** artefacts via glob rules (see §6).
2. **.gitignore** hardened – artefacts never committed.
3. **CI pipeline:**

   * Stage `cleanup` purges working tree; fails build if dirty.
   * Stage `archive` uploads artefacts to **S3 `ai‑system‑logs`** (90‑day lifecycle).
4. **Local dev:** `pytest` fixture writes to `$TMPDIR/ai‑system‑outputs` (auto‑clean).
5. **Pre‑commit hook** blocks additions matching new ignore list unless `ALLOW_GENERATED=1` env‑flag present.

## 6 | Specification

### 6.1 Directory Layout

```
/build/artifacts/&lt;CI_JOB_ID&gt;/ …      # CI‑only outputs
/tmp/ai‑system‑outputs/             # local test runs (ignored)
```

### 6.2 . gitignore (glob delta)

```gitignore
# ─── Generated / Ephemeral ───
outputs/**
src/**/outputs/**
tests/outputs/**
logs/**
build/**/logs/**
runtime/cache/**
*.jsonl
coverage.json
bandit-report.json
security_scan.json
validation_report*.json
archives/**
*.tar.gz
*.backup
*_backup.*
*.html
*.sql
```

### 6.3 CI Pipeline Snippet (`.ci/jobs/cleanup.yml`)

```yaml
cleanup:
  stage: cleanup
  script:
    - poetry run python scripts/enhanced_cleanup.py --ttl 14d
    - |
      if ! git diff --quiet; then
        echo "Working tree dirty after cleanup. Commit generated artefact rules." && exit 1
      fi
```

### 6.4 Retention / Access Control

|  Bucket               | Lifecycle              | Encryption | IAM Role                 |
| --------------------- | ---------------------- | ---------- | ------------------------ |
|  `ai-system-logs`     | Delete after 90 days   | SSE‑KMS    | `ai‑ci‑artifacts‑upload` |
|  `ai-system-archives` | Glacier after 180 days | SSE‑KMS    | `ai‑repo‑admin`          |

### 6.5 Testing Adjustments

* `tests/conftest.py` fixture `artifact_path` points to `tmp_path_factory`.
* Assert **no writes** outside tmp via `pytest‑filesystem‑audit` plugin.

## 7 | Quality Gates

| Gate                   | Threshold | Enforcer            |
| ---------------------- | --------- | ------------------- |
| Repo file count        | &lt; 700     | CI Job `repo‑stats` |
| LOC (analysis surface) | &lt; 170 k   | Sonar metric filter |
| Coverage               | ≥ 92 %    | Coveralls           |
| Lint errors            | 0         | Ruff + MyPy         |

## 8 | Security & Compliance

* **OWASP ASVS V7 & V12** – sensitive logs excluded from repo, encryption at rest in S3.
* **GDPR** – personal data only in transient logs; purged ≤ 30 days via TTL.

## 9 | Migration Plan

|  Step  | Task ID                         | Owner          | Blocking |
| ------ | ------------------------------- | -------------- | -------- |
|  1     | Draft ADR (this doc)            | Platform Guild | –        |
|  2     | Approve via guild vote          | Architects     |  1       |
|  3     | Implement `.gitignore` (CLN‑02) | DevEx          |  2       |
|  4     | CI cleanup stage (CLN‑03, 07)   | DevOps         |  3       |
|  5     | S3 bucket + IAM                 | SecOps         |  2       |
|  6     | Rewrite repo history (CLN‑04)   | DevOps         |  3,5     |
|  7     | Deduplicate task YAML (CLN‑06)  | Backend        |  4       |
|  8     | Tag `pre‑cleanup‑2025‑07‑27`    | DevOps         |  6       |

## 10 | Rollback Plan

* **Tag** preserves pre‑cleanup state.
* Set env `SKIP_CLEANUP=true` to bypass pipeline stage.
* Restore artefact paths via Helm values (`generatedOutput.enabled=true`).

## 11 | Open Issues

* GitHub search index may still show purged paths for \~24 h.
* Some legacy scripts hard‑code `outputs/`; need lint scan.

## 12 | References

* Hexagonal Architecture Guide – v3.2 §4 (File boundaries)
* PCI‑DSS v4 §10 – Log retention
* ADR Template – adr.github.io

---

> **Decided when merged to `main`.  Migration completes within the 2025‑08 sprint.**
