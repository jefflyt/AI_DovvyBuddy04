# Lead Capture Setup Guide

Complete setup instructions for the PR4 Lead Capture & Delivery system.

---

## Prerequisites

- Python backend installed and running (`backend`)
- PostgreSQL database configured
- Database migrations up to date

---

## 1. Resend Account Setup

### Create Account

1. Go to https://resend.com
2. Click "Sign Up" or "Get Started"
3. Create an account with your email
4. Verify your email address

### Generate API Key

1. Log in to your Resend dashboard
2. Navigate to **API Keys** section (https://resend.com/api-keys)
3. Click "Create API Key"
4. Name it: `DovvyBuddy Production` (or `DovvyBuddy Development` for testing)
5. Select permissions: **Full Access** (required for sending emails)
6. Click "Create"
7. **Copy the API key immediately** (you won't be able to see it again)
8. Store it securely

### Configure Domain (Optional but Recommended)

For production use with custom sender email:

1. Go to **Domains** section (https://resend.com/domains)
2. Click "Add Domain"
3. Enter your domain: `dovvybuddy.com`
4. Add the provided DNS records to your domain:
   - SPF record (TXT)
   - DKIM record (TXT)
5. Wait for DNS propagation (can take up to 48 hours)
6. Verify the domain in Resend dashboard

**Without domain verification:**

- You can only send from `onboarding@resend.dev`
- Emails may be more likely to land in spam
- Recommended for testing only

**With domain verification:**

- Send from `leads@dovvybuddy.com` or any address on your domain
- Better deliverability and trust
- Professional appearance

---

## 2. Environment Configuration

### Environment (Primary)

Edit project root `.env.local`:

```bash
# Lead Capture & Delivery Configuration
RESEND_API_KEY=re_xxxxxxxxxxxx           # Your Resend API key
LEAD_EMAIL_TO=leads@yourdiveshop.com     # Where to receive lead notifications
LEAD_EMAIL_FROM=leads@dovvybuddy.com     # Sender email (requires domain verification)
LEAD_WEBHOOK_URL=                        # Optional: future webhook integration
```

**Required:**

- `RESEND_API_KEY` - API key from step 1
- `LEAD_EMAIL_TO` - Email address where partner will receive lead notifications

**Optional:**

- `LEAD_EMAIL_FROM` - Custom sender email (defaults to `leads@dovvybuddy.com`)
  - Requires domain verification (see step 1)
  - Without verification, Resend will use `onboarding@resend.dev`
- `LEAD_WEBHOOK_URL` - For future CRM webhook integration

### Frontend Environment (Reference)

The root `.env.local` also has these variables for reference:

```bash
# Lead Capture & Delivery (PR4)
RESEND_API_KEY=re_xxxxxxxxxxxx
LEAD_EMAIL_TO=leads@yourdiveshop.com
LEAD_EMAIL_FROM=leads@dovvybuddy.com
LEAD_WEBHOOK_URL=
```

**Note:** The Python backend reads from project root `.env.local`.

---

## 3. Install Dependencies

### Backend Dependencies

```bash
cd src/backend
pip install -e .
```

This installs `resend>=0.8.0` and all other required packages.

### Verify Installation

```bash
python -c "import resend; print(resend.__version__)"
```

Should output version `0.8.0` or higher.

---

## 4. Database Migration

Run the lead schema migration:

```bash
cd src/backend
alembic upgrade head
```

This applies migration `002_update_leads` which updates the `leads` table structure:

- Adds `type` field (training/trip)
- Adds `request_details` JSONB field
- Adds `diver_profile` JSONB field
- Removes legacy fields

### Verify Migration

Check migration status:

```bash
alembic current
```

Should show: `002_update_leads (head)`

Verify table structure in PostgreSQL:

```sql
\d leads
```

Should show columns: `id`, `type`, `request_details`, `diver_profile`, `created_at`

---

## 5. Test Email Delivery

### Start Backend Server

```bash
cd src/backend
uvicorn app.main:app --reload --port 8000
```

### Send Test Lead (cURL)

```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "type": "training",
    "data": {
      "name": "Test User",
      "email": "test@example.com",
      "phone": "+1234567890",
      "certification_level": "Open Water",
      "interested_certification": "Advanced Open Water",
      "message": "This is a test lead submission"
    }
  }'
```

**Expected Response (201):**

```json
{
  "success": true,
  "lead_id": "uuid-here"
}
```

### Verify Email Received

1. Check inbox at `LEAD_EMAIL_TO` address
2. Look for email with subject: `[DovvyBuddy] New training Lead: Test User [...]`
3. Verify email contains:
   - Contact information (name, email, phone)
   - Training details (certification levels)
   - Message content
   - Professional formatting

### Check Resend Dashboard

1. Go to https://resend.com/emails
2. Find your test email in the list
3. Check delivery status:
   - ✅ **Delivered** - Success!
   - 📤 **Sent** - In transit
   - ⚠️ **Bounced** - Check email address
   - 🚫 **Spam** - Check content/domain
4. Review delivery logs for any issues

---

## 6. Troubleshooting

### Issue: "Email service not configured" (500 error)

**Cause:** `RESEND_API_KEY` not set in environment

**Solution:**

1. Verify root `.env.local` exists
2. Check `RESEND_API_KEY` is set and not empty
3. Restart backend server to pick up new environment variables
4. Verify with: `echo $RESEND_API_KEY` (in backend terminal)

### Issue: "Lead delivery email not configured" (500 error)

**Cause:** `LEAD_EMAIL_TO` not set

**Solution:**

1. Set `LEAD_EMAIL_TO` in `.env.local`
2. Restart backend server
3. Must be a valid email address

### Issue: Email not received

**Possible causes:**

1. **Spam folder** - Check spam/junk folder
2. **Invalid email** - Verify `LEAD_EMAIL_TO` is correct
3. **Domain not verified** - Use `onboarding@resend.dev` or verify your domain
4. **Rate limit** - Check Resend dashboard for limits (100 emails/day on free tier)
5. **Bounced** - Check Resend dashboard for bounce notification

**Debug steps:**

1. Check Resend dashboard (https://resend.com/emails)
2. Look for email in sent list
3. Check delivery status and logs
4. Try sending to a different email address
5. Check backend logs for errors: `tail -f logs/app.log`

### Issue: Email goes to spam

**Solutions:**

1. **Verify domain** - Add SPF/DKIM records (see step 1)
2. **Use custom domain** - Don't use `@resend.dev` sender
3. **Professional content** - Email templates are already optimized
4. **Warm up domain** - Start with low volume, gradually increase
5. **Check reputation** - Use https://mxtoolbox.com/domain/ to check domain reputation

### Issue: API key invalid

**Symptoms:** 401 Unauthorized from Resend

**Solutions:**

1. Verify API key is correct (no extra spaces)
2. Check API key hasn't been revoked in Resend dashboard
3. Regenerate API key if necessary
4. Update `.env.local` with new key
5. Restart backend server

### Issue: Rate limit exceeded

**Symptoms:** 429 Too Many Requests

**Solutions:**

1. **Free tier limit:** 100 emails/day, 3,000/month
2. **Upgrade plan:** Go to https://resend.com/pricing
3. **Implement queue:** Add Redis queue for high volume (future enhancement)
4. **Monitor usage:** Check Resend dashboard regularly

---

## 7. Testing Checklist

Before deploying to production:

- [ ] Resend account created and verified
- [ ] API key generated and stored securely
- [ ] Domain verified (for production)
- [ ] Environment variables set in root `.env.local`
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Database migration applied (`alembic upgrade head`)
- [ ] Backend server starts without errors
- [ ] Test lead submitted successfully (201 response)
- [ ] Email received at `LEAD_EMAIL_TO` address
- [ ] Email displays correctly in multiple clients (Gmail, Outlook, etc.)
- [ ] Reply-to works (replying goes to lead's email)
- [ ] Resend dashboard shows successful delivery
- [ ] Database contains lead record with correct data
- [ ] No errors in backend logs

---

## 8. Production Deployment

### Environment Variables

Set these in your production environment:

```bash
# Production Resend API key (different from development)
RESEND_API_KEY=re_prod_xxxxxxxxxxxxx

# Production email destination
LEAD_EMAIL_TO=leads@yourcompany.com

# Custom sender (requires verified domain)
LEAD_EMAIL_FROM=leads@dovvybuddy.com
```

### Security Best Practices

1. **API Key Security:**
   - Never commit API keys to git
   - Use environment variables or secrets manager
   - Rotate keys periodically
   - Use separate keys for dev/staging/production

2. **Email Security:**
   - Verify domain for SPF/DKIM/DMARC
   - Monitor bounce rates
   - Implement email validation
   - Add unsubscribe links (if bulk sending)

3. **Rate Limiting:**
   - Implement rate limiting on API endpoint (future PR)
   - Monitor for abuse/spam
   - Set up alerts for unusual activity

### Monitoring

1. **Resend Dashboard:**
   - Check daily delivery rates
   - Monitor bounce/spam rates
   - Review delivery logs

2. **Application Logs:**
   - Monitor for delivery failures
   - Check error rates
   - Set up alerts for critical errors

3. **Database:**
   - Monitor lead capture rate
   - Check for data quality issues
   - Set up analytics queries

---

## 9. Cost Considerations

### Resend Pricing (as of January 2026)

**Free Tier:**

- 100 emails/day
- 3,000 emails/month
- Good for: Testing, small volume

**Pro Plan ($20/month):**

- 50,000 emails/month
- Good for: Small to medium businesses

**Enterprise:**

- Custom volume
- Dedicated IP
- SLA guarantees

### Expected Usage

**Conservative estimate (10 leads/day):**

- 300 leads/month
- Fits in free tier

**Growth scenario (100 leads/day):**

- 3,000 leads/month
- Still fits in free tier!

**High volume (200 leads/day):**

- 6,000 leads/month
- Need Pro plan ($20/month)

---

## 10. Next Steps

### Immediate

- [ ] Set up monitoring and alerts
- [ ] Test email delivery to multiple providers
- [ ] Document lead follow-up process for partners
- [ ] Train team on lead notification emails

### Future Enhancements

- [ ] Rate limiting on API endpoint (prevent abuse)
- [ ] CAPTCHA integration (PR5 - frontend)
- [ ] Lead deduplication logic
- [ ] Webhook delivery to CRM
- [ ] SMS notifications via Twilio
- [ ] Admin dashboard for lead management
- [ ] Lead status tracking (contacted, converted)

---

## Support & Resources

### Documentation

- **Implementation Guide:** `docs/project-management/PR4-Implementation-Guide.md`
- **API Reference:** `src/backend/docs/LEAD_API_REFERENCE.md`
- **Project Summary:** `docs/project-management/PR4-Implementation-Summary.md`

### External Resources

- **Resend Docs:** https://resend.com/docs
- **Resend Dashboard:** https://resend.com/home
- **Resend Status:** https://status.resend.com
- **Resend Support:** support@resend.com

### Getting Help

1. Check Resend documentation first
2. Review backend application logs
3. Check Resend dashboard for delivery issues
4. Test with curl to isolate frontend vs backend issues
5. Contact Resend support for delivery problems

---

**Setup Date:** January 8, 2026  
**Last Updated:** January 8, 2026  
**Version:** 1.0
