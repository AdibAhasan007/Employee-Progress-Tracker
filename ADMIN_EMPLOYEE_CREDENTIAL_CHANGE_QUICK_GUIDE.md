# ⚡ Admin & Employee Credential Change - Quick Reference

## 🎯 Feature Summary

Company Admins and Employees can now change their own **Username** and **Password** securely.

---

## 📍 How to Access

### For Company Admin
1. Login to Admin Dashboard
2. Click **"⚙️ Account Settings"** in sidebar footer
3. Choose option:
   - **Change Password** - Update your login password
   - **Change Username** - Update your login username

### For Employee
1. Login to Employee Dashboard
2. Click **"⚙️ Account Settings"** in sidebar footer
3. Choose option:
   - **Change Password** - Update your login password
   - **Change Username** - Update your login username

---

## 🔐 Change Password

### Steps
1. Go to Account Settings → Change Password
2. Enter **Current Password** (required for verification)
3. Enter **New Password** (6+ characters)
4. Confirm new password
5. Click **"Change Password"**

### Rules
- ✓ Current password must be correct
- ✓ New password minimum 6 characters
- ✓ New and confirm password must match
- ✓ New password cannot be same as old password

### After Change
- ✅ You stay logged in (no re-login needed)
- ✅ Use new password for next login
- ❌ Old password no longer works

---

## 👤 Change Username

### Steps
1. Go to Account Settings → Change Username
2. Enter **Current Password** (required for verification)
3. Enter **New Username**
4. Click **"Change Username"**

### Rules
- ✓ Current password must be correct
- ✓ Username length 3-150 characters
- ✓ Only letters, numbers, underscore (_), hyphen (-)
- ✓ New username must be different from current
- ✓ Username must be unique (no duplicates)

### After Change
- ✅ Username changed successfully
- ⚠️ Use new username to login next time
- ❌ Old username no longer works

### Real-Time Validation
As you type, you'll see:
- ✓ Green checkmark = Rule passed
- ✗ Red X = Rule failed

Rules shown:
- Length (3-150 chars)
- Format (alphanumeric, _, -)
- Must be different from current

---

## 🛡️ Security Features

| Feature | Description |
|---------|-------------|
| **Password Verification** | Always required before changes |
| **Password Hashing** | Secure PBKDF2 algorithm |
| **Session Safe** | You stay logged in after password change |
| **Strength Indicator** | Real-time password strength rating |
| **Audit Logging** | All changes logged for compliance |
| **Validation** | Both client & server validation |

---

## ⚠️ Important Notes

### Password Change
- Your password is hashed and secured
- Never share your password
- Use a mix of uppercase, lowercase, numbers, symbols
- Change password every 3 months

### Username Change
- You'll need new username to login next time
- Can contain: letters, numbers, underscore, hyphen
- Cannot contain: spaces, special chars (!@#$%)
- Must be between 3-150 characters

### If You Forget
- ❌ **Password**: Ask Owner to reset your credentials
- ❌ **Username**: Ask Owner to reset your credentials

---

## 🎨 User Interface Examples

### Password Strength Indicator
```
❌ Weak      └─ Less than 3 rules met
⚠️  Fair      └─ 3-4 rules met (orange)
✅ Good      └─ 5 rules met (green)
🔒 Strong    └─ 6 rules met (blue)
```

### Username Validation
```
✓ Length (3-150 chars)          ← Shows green when met
✓ Format (letters, numbers, _, -) ← Shows green when met
✓ Different from current         ← Shows green when met
```

---

## 📞 Support

**Issue**: Password verification fails
- ℹ️ Ensure you entered current password correctly (case-sensitive)

**Issue**: Username already taken
- ℹ️ Choose a different username (must be unique)

**Issue**: Can't login after changes
- ℹ️ Use your NEW password or NEW username
- ℹ️ Old credentials no longer work

**Issue**: Account locked after multiple failed attempts
- ℹ️ Contact your Owner/Admin for password reset

---

## ✅ Checklist for First Time

- [ ] Go to Account Settings
- [ ] Review your current account info
- [ ] Change password to something strong
- [ ] (Optional) Change username if desired
- [ ] Logout and login again with new credentials
- [ ] Verify everything works

---

## 🔗 Related Pages

- Account Overview - View account information
- Audit Log - See history of changes
- Admin Dashboard - Main admin area
- Help & Support - Get additional help

---

**Last Updated**: February 2, 2026  
**Status**: ✅ Ready to Use

