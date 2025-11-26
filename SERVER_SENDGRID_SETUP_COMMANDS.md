# SendGrid Setup Commands for Server

Run these commands on your server to set up and test SendGrid:

## Step 1: Pull Latest Changes

```bash
cd /var/www/clink-backend
git pull origin main
```

## Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 3: Install/Update Libraries

```bash
pip install -r requirements.txt
```

Or if you just need to ensure SendGrid is installed:

```bash
pip install sendgrid==6.11.0 requests==2.31.0
```

## Step 4: Verify SendGrid API Key in .env

```bash
grep SENDGRID_API_KEY .env
```

Should show:
```
SENDGRID_API_KEY=your-sendgrid-api-key-here
```

If not found, add it:
```bash
sudo nano .env
```

Add these lines:
```env
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
SENDGRID_FROM_NAME=Tailored Psychology
```

## Step 5: Test SendGrid Connection (Direct API)

```bash
python test_sendgrid_direct.py
```

This will:
- Check if API key is configured
- Test network connectivity
- Send a test email
- Show detailed results

## Step 6: Test via Django Shell (Alternative)

```bash
python manage.py shell
```

Then in Python:
```python
from core.email_service import test_email_configuration
result = test_email_configuration()
print(result)
```

## Expected Output

If successful, you should see:
```
✅ Email sent successfully!
📧 Check your inbox at: noreply@tailoredpsychology.com.au
   Also check SendGrid Dashboard → Activity
```

## Troubleshooting

If you get timeout errors:
1. Check network: `curl -I https://api.sendgrid.com/v3/`
2. Check firewall: `sudo ufw status`
3. Try the direct test script: `python test_sendgrid_direct.py`

---

**Ready to test!** 🚀

