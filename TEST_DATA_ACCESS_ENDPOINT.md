# Test Data Access Endpoint

## Quick Test Commands

### 1. Test with curl (replace YOUR_TOKEN)

```bash
# Test JSON format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Test PDF format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test.pdf

# Test CSV format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?format=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test.csv
```

### 2. Get a Patient Token

```bash
# Login as patient to get token
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "patient@example.com", "password": "password"}'
```

### 3. Check if Endpoint is Registered

```bash
python manage.py show_urls | grep data-access
```

Should show:
```
/api/auth/data-access-request/	users.views.DataAccessRequestView	data-access-request
```

### 4. Check Django Logs

```bash
tail -f logs/django.log | grep data-access
```

---

## Expected Responses

### Success (200):
- JSON: Returns JSON data
- PDF: Downloads PDF file
- CSV: Downloads CSV file

### Errors:
- **401**: Not authenticated (need valid token)
- **403**: Not a patient (only patients can access)
- **404**: Endpoint not found (server needs restart)
- **500**: Server error (check logs)

---

## If Still Getting 404

1. **Kill all Django processes:**
   ```bash
   pkill -f "manage.py runserver"
   ```

2. **Restart server:**
   ```bash
   python manage.py runserver
   ```

3. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

4. **Test again with curl**

