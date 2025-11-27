#!/bin/bash
# Test SendGrid DNS Records
# Run this on your Droplet to verify DNS records are correctly configured

echo "=========================================="
echo "Testing SendGrid DNS Records"
echo "=========================================="
echo ""

# Test 1: Email CNAME
echo "1. Testing Email CNAME (em2613)..."
dig em2613.tailoredpsychology.com.au CNAME +short
echo ""

# Test 2: DKIM Selector 1
echo "2. Testing DKIM Selector 1 (s1._domainkey)..."
dig s1._domainkey.tailoredpsychology.com.au CNAME +short
echo ""

# Test 3: DKIM Selector 2
echo "3. Testing DKIM Selector 2 (s2._domainkey)..."
dig s2._domainkey.tailoredpsychology.com.au CNAME +short
echo ""

# Test 4: DMARC TXT
echo "4. Testing DMARC TXT (_dmarc)..."
dig _dmarc.tailoredpsychology.com.au TXT +short
echo ""

echo "=========================================="
echo "Expected Results:"
echo "=========================================="
echo "1. em2613 should return: u57558855.wl106.sendgrid.net."
echo "2. s1._domainkey should return: s1.domainkey.u57558855.wl106.sendgrid.net."
echo "3. s2._domainkey should return: s2.domainkey.u57558855.wl106.sendgrid.net."
echo "4. _dmarc should return: \"v=DMARC1; p=none;\""
echo ""

