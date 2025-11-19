# 🔒 DigitalOcean Database Encryption Guide

## Overview
DigitalOcean Managed PostgreSQL clusters support disk-level encryption (AES‑256) for data at rest. If you plan to store PHI or medical records, enable this feature before going live.

---

## 1. Create / Migrate to Encrypted Cluster

1. Log in to DigitalOcean dashboard → Databases.
2. Click **Create Database Cluster**.
3. Choose **PostgreSQL** and select the latest LTS version.
4. Under **Security**, ensure “Data encryption at rest” is enabled (default for new clusters).
5. If you already have a cluster without encryption:
   - Create a new encrypted cluster.
   - Take a pg_dump backup of the old cluster.
   - Restore into the new encrypted cluster.
   - Update `DATABASE_URL` in `.env`.

---

## 2. Document Encryption Status

Add to `settings.py` (already scaffolded):

```python
DATA_ENCRYPTION_AT_REST = {
    'database': {
        'provider': 'DigitalOcean Managed PostgreSQL',
        'status': 'enabled',
        'notes': 'Disk-level AES-256 encryption managed by DO'
    }
}
```

Update `COMPLIANCE_QUICK_CHECKLIST.md` once the new cluster is live.

---

## 3. Rotate Credentials

After migrating:

1. Generate a new database password in DigitalOcean.
2. Update `.env` (`DATABASE_URL`).
3. Restart backend services.

---

## 4. Optional: Field-Level Encryption

For extra protection on progress notes or intake forms, use `django-fernet-fields` or `django-pgcrypto-fields` so data stays encrypted even before it hits the database storage.

---

## 5. Verification Checklist

- [ ] New DigitalOcean cluster shows “Encrypted at rest” in dashboard.
- [ ] Application uses the new cluster (`DATABASE_URL` updated).
- [ ] Old cluster destroyed after verifying data.
- [ ] Documentation updated (compliance guide + security section).

---

**Last Updated:** November 19, 2025

