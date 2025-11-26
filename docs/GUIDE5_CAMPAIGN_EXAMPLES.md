# 📧 Campaign Model - Sample Data & HTML Templates

This guide provides complete values for creating Campaign objects in Django admin.

---

## 📋 Campaign Model Fields Reference

```python
class Campaign(models.Model):
    name = models.CharField(max_length=255)              # Campaign title
    subject = models.CharField(max_length=255)           # Email subject line
    content = models.TextField()                          # HTML email content
    scheduled_time = models.DateTimeField(null=True)     # When to send (IST)
    status = models.CharField(default=DRAFT)             # draft/scheduled/in_progress/completed
    created_by = models.ForeignKey(User)                 # Who created it
    created_on = models.DateTimeField(auto_now_add=True) # Auto-set
```

---

## 🎯 Campaign Example 1: Welcome Email Campaign

### Values for Django Admin:

**Name:** `Welcome Email Campaign - November 2025`

**Subject:** `🎉 Welcome to Campaign Mailer - Let's Get Started!`

**Content:** (Copy from `email_templates/welcome_email.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Our Community</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #f4f4f4;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            text-align: center;
        }
        .header h1 {
            color: #ffffff;
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .content {
            padding: 40px 30px;
        }
        .content h2 {
            color: #333333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .content p {
            color: #666666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .button {
            display: inline-block;
            padding: 14px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            margin: 20px 0;
        }
        .features {
            background-color: #f9f9f9;
            padding: 30px;
            margin: 20px 0;
            border-radius: 8px;
        }
        .feature-item {
            margin-bottom: 15px;
        }
        .feature-item h3 {
            color: #667eea;
            font-size: 18px;
            margin: 0 0 5px 0;
        }
        .feature-item p {
            margin: 0;
            color: #666666;
        }
        .footer {
            background-color: #333333;
            color: #ffffff;
            padding: 30px;
            text-align: center;
            font-size: 14px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Welcome Aboard!</h1>
        </div>
        <div class="content">
            <h2>Hello!</h2>
            <p>We're thrilled to have you join our community! You've just taken the first step towards an amazing journey with us.</p>
            <p>At <strong>Campaign Mailer</strong>, we're dedicated to helping you stay informed, engaged, and ahead of the curve.</p>
            <div class="features">
                <div class="feature-item">
                    <h3>📧 Regular Updates</h3>
                    <p>Get the latest news, tips, and insights delivered right to your inbox.</p>
                </div>
                <div class="feature-item">
                    <h3>🎁 Exclusive Offers</h3>
                    <p>Be the first to know about special promotions and member-only deals.</p>
                </div>
                <div class="feature-item">
                    <h3>💡 Expert Resources</h3>
                    <p>Access curated content, guides, and resources to help you succeed.</p>
                </div>
            </div>
            <p style="text-align: center;">
                <a href="https://codewithsanin.online/get-started" class="button">Get Started Now</a>
            </p>
            <p>Best regards,<br><strong>The Campaign Mailer Team</strong></p>
        </div>
        <div class="footer">
            <p>© 2025 Campaign Mailer. All rights reserved.</p>
            <p style="font-size: 12px; color: #999999; margin-top: 20px;">
                Campaign Mailer<br>123 Email Street, Digital City, IN 560001
            </p>
        </div>
    </div>
</body>
</html>
```

**Scheduled Time:** `2025-11-26 18:00:00` (IST - 6 PM today)

**Status:** `scheduled`

---

## 🔥 Campaign Example 2: Flash Sale Campaign

### Values for Django Admin:

**Name:** `Black Friday Flash Sale - 50% OFF`

**Subject:** `⚡ FLASH SALE: 50% OFF Everything - Only 24 Hours Left!`

**Content:** (Copy from `email_templates/flash_sale_email.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin: 0; padding: 0; font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; }
        .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 50px 20px; text-align: center; }
        .header h1 { color: #ffffff; margin: 0; font-size: 36px; font-weight: 700; }
        .countdown { background-color: rgba(255, 255, 255, 0.2); color: #ffffff; padding: 15px; margin-top: 20px; border-radius: 8px; font-size: 18px; font-weight: 600; }
        .content { padding: 40px 30px; text-align: center; }
        .discount-badge { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #ffffff; font-size: 48px; font-weight: 700; padding: 30px; border-radius: 50%; display: inline-block; width: 150px; height: 150px; line-height: 150px; margin: 20px 0; }
        .cta-button { display: inline-block; padding: 18px 50px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #ffffff; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 18px; margin: 30px 0; }
        .features { background-color: #fff5f7; padding: 30px; margin: 30px 0; border-radius: 8px; }
        .feature-item { padding: 10px 0; font-size: 16px; color: #666666; }
        .feature-item::before { content: "✓ "; color: #f5576c; font-weight: 700; font-size: 18px; }
        .footer { background-color: #333333; color: #ffffff; padding: 30px; text-align: center; font-size: 14px; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>⚡ FLASH SALE ⚡</h1>
            <div class="countdown">🕐 Only 24 Hours Left!</div>
        </div>
        <div class="content">
            <div class="discount-badge">50% OFF</div>
            <h2 style="color: #333333; font-size: 28px;">Limited Time Offer!</h2>
            <p style="font-size: 20px; color: #f5576c; font-weight: 600;">Don't Miss Out - Sale Ends Tomorrow!</p>
            <div class="features">
                <div class="feature-item">Free shipping on all orders</div>
                <div class="feature-item">30-day money-back guarantee</div>
                <div class="feature-item">24/7 customer support</div>
                <div class="feature-item">Exclusive member benefits</div>
            </div>
            <a href="https://codewithsanin.online/flash-sale" class="cta-button">🛍️ SHOP NOW</a>
            <p style="font-size: 14px; color: #999999; margin-top: 30px;">
                Use code: <strong style="color: #f5576c; font-size: 18px;">FLASH50</strong> at checkout
            </p>
        </div>
        <div class="footer">
            <p>© 2025 Campaign Mailer. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
```

**Scheduled Time:** `2025-11-27 10:00:00` (IST - 10 AM tomorrow)

**Status:** `scheduled`

---

## 📰 Campaign Example 3: Monthly Newsletter

### Values for Django Admin:

**Name:** `Monthly Newsletter - November 2025`

**Subject:** `📰 Your November Newsletter: Email Marketing Trends & Tips`

**Content:** (Copy from `email_templates/newsletter_email.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; padding: 0; font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f4f4; }
        .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
        .header { background-color: #2c3e50; padding: 30px 20px; text-align: center; }
        .logo { color: #ffffff; font-size: 32px; font-weight: 700; margin: 0; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 60px 20px; text-align: center; color: white; }
        .hero h1 { font-size: 36px; margin: 0 0 15px 0; }
        .content { padding: 40px 30px; }
        .article { margin-bottom: 40px; border-bottom: 1px solid #eeeeee; padding-bottom: 30px; }
        .article h2 { color: #2c3e50; font-size: 24px; }
        .article p { color: #666666; font-size: 16px; line-height: 1.6; }
        .read-more { color: #667eea; text-decoration: none; font-weight: 600; }
        .cta-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 40px 30px; text-align: center; border-radius: 8px; }
        .cta-button { display: inline-block; padding: 14px 35px; background-color: #ffffff; color: #667eea; text-decoration: none; border-radius: 5px; font-weight: 600; }
        .footer { background-color: #2c3e50; color: #ecf0f1; padding: 30px; text-align: center; }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1 class="logo">📰 Campaign Mailer</h1>
        </div>
        <div class="hero">
            <h1>November 2025 Newsletter</h1>
            <p>The latest trends, tips, and updates</p>
        </div>
        <div class="content">
            <div class="article">
                <h2>🚀 10 Email Marketing Strategies That Work in 2025</h2>
                <p>Discover the latest strategies that top marketers are using to achieve open rates above 40%.</p>
                <a href="https://codewithsanin.online/blog/strategies" class="read-more">Read More →</a>
            </div>
            <div class="cta-section">
                <h3>Ready to Scale Your Email Campaigns?</h3>
                <p>Join thousands of marketers who trust Campaign Mailer.</p>
                <a href="https://codewithsanin.online/get-started" class="cta-button">Get Started Free</a>
            </div>
            <p>Best regards,<br><strong>The Campaign Mailer Team</strong></p>
        </div>
        <div class="footer">
            <p>© 2025 Campaign Mailer. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
```

**Scheduled Time:** `2025-11-28 09:00:00` (IST - 9 AM day after tomorrow)

**Status:** `scheduled`

---

## 🎯 Campaign Example 4: Simple Text Campaign (Testing)

### Values for Django Admin:

**Name:** `Test Campaign - Gmail SMTP Test`

**Subject:** `Test Email from Campaign Mailer - Please Verify`

**Content:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        p {
            color: #666666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #667eea;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eeeeee;
            text-align: center;
            color: #999999;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ Test Email - Campaign System Working!</h1>
        
        <p>Hello,</p>
        
        <p>This is a test email from the Campaign Mailer system. If you're receiving this, it means:</p>
        
        <ul>
            <li>✅ Email configuration is correct</li>
            <li>✅ SMTP/API connection is working</li>
            <li>✅ Campaign system is operational</li>
            <li>✅ Ready for production use</li>
        </ul>
        
        <p style="text-align: center;">
            <a href="https://codewithsanin.online" class="button">Visit Website</a>
        </p>
        
        <p>If you received this email successfully, the system is ready to handle your campaigns!</p>
        
        <p>Best regards,<br>
        <strong>Campaign Mailer Automated System</strong></p>
        
        <div class="footer">
            <p>© 2025 Campaign Mailer · Test Email · System Check</p>
        </div>
    </div>
</body>
</html>
```

**Scheduled Time:** `2025-11-26 16:00:00` (IST - 4 PM today - should be at least 1 hour from now)

**Status:** `scheduled`

---

## 📝 Quick Copy-Paste Values for Django Admin

### Option 1: Welcome Campaign
```
Name: Welcome Email Campaign - November 2025
Subject: 🎉 Welcome to Campaign Mailer - Let's Get Started!
Content: [Copy HTML from email_templates/welcome_email.html]
Scheduled Time: 2025-11-26 18:00:00
Status: scheduled
```

### Option 2: Flash Sale Campaign
```
Name: Black Friday Flash Sale - 50% OFF
Subject: ⚡ FLASH SALE: 50% OFF Everything - Only 24 Hours Left!
Content: [Copy HTML from email_templates/flash_sale_email.html]
Scheduled Time: 2025-11-27 10:00:00
Status: scheduled
```

### Option 3: Newsletter Campaign
```
Name: Monthly Newsletter - November 2025
Subject: 📰 Your November Newsletter: Email Marketing Trends & Tips
Content: [Copy HTML from email_templates/newsletter_email.html]
Scheduled Time: 2025-11-28 09:00:00
Status: scheduled
```

### Option 4: Test Campaign
```
Name: Test Campaign - Gmail SMTP Test
Subject: Test Email from Campaign Mailer - Please Verify
Content: [Copy HTML from email_templates/test_email.html]
Scheduled Time: 2025-11-26 16:00:00
Status: scheduled
```

---

## ⚠️ Important Notes

### 1. Scheduled Time Rules:
- Must be in **IST (Asia/Kolkata)** timezone
- Must be **at least 1 hour from now** (form validation)
- Must have **1 hour gap** between campaigns
- Format: `YYYY-MM-DD HH:MM:SS`

### 2. Current Time Reference (IST):
Today is **November 26, 2025**

Safe scheduling times:
- ✅ `2025-11-26 16:00:00` (4 PM today)
- ✅ `2025-11-26 18:00:00` (6 PM today)
- ✅ `2025-11-27 10:00:00` (10 AM tomorrow)
- ✅ `2025-11-28 09:00:00` (9 AM day after)

### 3. Status Options:
- `draft` - Not ready to send
- `scheduled` - Will be sent at scheduled_time
- `in_progress` - Currently being sent (auto-set by system)
- `completed` - Finished sending (auto-set by system)

### 4. HTML Content Tips:
- ✅ Always use complete `<!DOCTYPE html>` structure
- ✅ Include inline CSS styles (email clients don't support external CSS)
- ✅ Use tables for layout if needed (better email client support)
- ✅ Test with both Gmail and SendGrid
- ✅ Keep images hosted externally (use CDN or website)
- ✅ Include unsubscribe link (best practice)

---

## 🚀 How to Create Campaign in Django Admin

1. **Go to Django Admin:**
   ```
   http://localhost:8000/admin/
   ```

2. **Navigate to Campaigns:**
   - Click "Campaigns" → "Add Campaign"

3. **Fill in the form:**
   - **Name:** Copy from examples above
   - **Subject:** Copy from examples above
   - **Content:** Copy entire HTML template
   - **Scheduled Time:** Use date/time picker (remember 1-hour rule!)
   - **Status:** Select "scheduled"
   - **Created by:** Auto-filled with your user

4. **Click "Save"**

5. **Verify:**
   - Check campaign appears in list
   - Status shows "Scheduled"
   - Scheduled time is correct

---

## ✅ Testing Workflow

### Step 1: Create Test Campaign (Small Scale)
```
Name: Test Campaign - 10 Recipients
Subject: Test Email - Please Verify
Content: [Use simple HTML above]
Scheduled Time: [1 hour from now]
Status: scheduled
```

### Step 2: Upload Test Recipients
- Use `sample_recipients.csv` (10 recipients)
- Or upload via bulk upload in admin

### Step 3: Wait for Celery Beat
- Celery beat runs every minute
- Will trigger campaign at scheduled time
- Check logs for execution

### Step 4: Verify Delivery
- Check recipient inboxes
- Review DeliveryLog in admin
- Check campaign status → "completed"

### Step 5: Scale Up
- Once test works, create campaigns with more recipients
- Upload `sample_recipients_100k.csv`
- Schedule high-volume campaigns

---

Happy Campaigning! 🚀📧
