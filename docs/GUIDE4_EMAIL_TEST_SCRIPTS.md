# Email Testing Scripts Comparison

## 📧 Available Test Scripts

### 1. test_gmail.py - Gmail SMTP Testing
Test your Gmail SMTP configuration

**Usage:**
```bash
# Basic test (sends to specified email)
python test_gmail.py recipient@example.com

# Custom subject and message
python test_gmail.py recipient@example.com "My Subject" "My Message"

# Test to your own Gmail
python test_gmail.py sanin.nitcalicut.ece@gmail.com
```

**What it tests:**
- ✅ Gmail SMTP connection
- ✅ Authentication with App Password
- ✅ TLS encryption
- ✅ Email delivery
- ✅ HTML email formatting

**Limits:**
- 🚫 500 emails/day (free Gmail)
- 🚫 Not suitable for bulk sending

---

### 2. test_sendgrid.py - SendGrid API Testing
Test your SendGrid API configuration

**Usage:**
```bash
# Basic test
python test_sendgrid.py recipient@example.com

# Custom subject and message
python test_sendgrid.py recipient@example.com "Subject" "Message"

# Test with your verified domain
python test_sendgrid.py sanin.fun@gmail.com
```

**What it tests:**
- ✅ SendGrid API connection
- ✅ API key validity
- ✅ Email delivery
- ✅ HTML email formatting
- ✅ Domain authentication (if configured)

**Limits:**
- ✅ 100 emails/day (free tier)
- ✅ Scalable to millions (paid plans)
- ✅ High deliverability

---

## 📊 Quick Comparison

| Feature | test_gmail.py | test_sendgrid.py |
|---------|---------------|------------------|
| **Setup Time** | 5 minutes | 15 minutes |
| **Requires** | Gmail account, App Password | SendGrid account, API key |
| **Free Tier** | 500 emails/day | 100 emails/day |
| **Paid Options** | Google Workspace (2k/day) | Scalable to millions |
| **Best For** | Testing, low volume | Production, high volume |
| **Domain Auth** | Not required | Recommended |
| **Deliverability** | Good (85-90%) | Excellent (95%+) |

---

## 🚀 Which Should You Use?

### For Development/Testing:
```bash
# Use Gmail - Quick and easy
python test_gmail.py your@email.com
```

### For Production (200k emails):
```bash
# Use SendGrid - Professional and scalable
python test_sendgrid.py your@email.com
```

---

## ⚙️ Configuration Required

### Gmail (test_gmail.py)
```properties
# .env file
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=sanin.nitcalicut.ece@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=sanin.nitcalicut.ece@gmail.com
```

### SendGrid (test_sendgrid.py)
```properties
# .env file
SENDGRID_API_KEY=SG.your-api-key-here
SENDGRID_FROM_EMAIL=noreply@codewithsanin.online
SENDGRID_FROM_NAME=Campaign Mailer
DEFAULT_FROM_EMAIL=noreply@codewithsanin.online
```

---

## 🧪 Testing Workflow

### Step 1: Test Gmail First (Quick Setup)
```bash
python test_gmail.py sanin.nitcalicut.ece@gmail.com
```

### Step 2: Test SendGrid (Production Ready)
```bash
python test_sendgrid.py sanin.fun@gmail.com
```

### Step 3: Choose Based on Volume

**If sending < 500 emails/day:**
- ✅ Use Gmail
- ✅ Free
- ✅ Simple setup

**If sending 500-100k+ emails/day:**
- ✅ Use SendGrid
- ✅ Better deliverability
- ✅ Professional features
- ✅ Analytics & tracking

---

## 📝 Example Output

### Successful Gmail Test:
```
==========================================
Testing Gmail SMTP Configuration
==========================================

📧 Gmail SMTP Settings:
   Host: smtp.gmail.com
   Port: 587
   Username: sanin.nitcalicut.ece@gmail.com
   Use TLS: True

📨 Sending test email...
⏳ Connecting to smtp.gmail.com:587...
🔒 Starting TLS encryption...
🔐 Authenticating...
📤 Sending email...

==========================================
✅ SUCCESS! Email sent successfully!
==========================================

📬 Check the inbox: recipient@example.com
🎉 Gmail SMTP configuration is working correctly!
```

### Successful SendGrid Test:
```
==========================================
Testing SendGrid API Configuration
==========================================

📧 SendGrid Settings:
   API Key: SG.imE***ylk
   From Email: noreply@codewithsanin.online
   From Name: Campaign Mailer

📨 Sending test email...
   To: recipient@example.com

==========================================
✅ SUCCESS! Email sent successfully!
==========================================

📬 Message ID: abc123xyz
📧 Check the inbox: recipient@example.com
🎉 SendGrid is working correctly!
```

---

## 🔧 Troubleshooting

### Gmail Issues:

**"Authentication Failed"**
```bash
# Solution: Use App Password, not regular password
# 1. Enable 2-Step Verification
# 2. Generate App Password
# 3. Update .env with App Password
```

**"Connection Refused"**
```bash
# Solution: Check port and TLS settings
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### SendGrid Issues:

**"Unauthorized"**
```bash
# Solution: Check API key
# 1. Verify API key in SendGrid dashboard
# 2. Ensure it has "Mail Send" permissions
# 3. Copy the full key to .env
```

**"Domain Not Verified"**
```bash
# Solution: Verify your domain
# 1. Add DNS records in GoDaddy
# 2. Wait 10-30 minutes
# 3. Verify in SendGrid dashboard
```

---

## ✅ Success Checklist

### Before Testing:
- [ ] Environment variables configured in .env
- [ ] Django settings updated
- [ ] Email provider account created
- [ ] Credentials obtained

### After Testing:
- [ ] Test script runs successfully
- [ ] Test email received
- [ ] HTML formatting works
- [ ] Ready for production use

---

## 🎯 Next Steps

1. **Test Gmail:**
   ```bash
   python test_gmail.py your@email.com
   ```

2. **Test SendGrid:**
   ```bash
   python test_sendgrid.py your@email.com
   ```

3. **Choose provider** based on your needs

4. **Start sending campaigns!** 🚀

---

## 💡 Pro Tips

1. **Always test before production** - Run both scripts to ensure everything works
2. **Use SendGrid for high volume** - Better deliverability and analytics
3. **Gmail for development** - Quick and easy for testing
4. **Monitor limits** - Stay within daily sending quotas
5. **Authenticate domains** - Better deliverability with SendGrid

---

Happy Testing! 📧✨
