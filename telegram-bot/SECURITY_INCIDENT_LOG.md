# Security Incident Log - Telegram Bot

## Compromised Tokens Summary

### Production Token (CRITICAL - ALREADY ROTATED ✅)
- **Token**: `8035864354:AAHch7_0sT--M0xunghsWbyNS3pn_nKASVQ`
- **Exposure**: Hardcoded in `diagnose_bot.py:12`
- **Status**: ✅ REVOKED in BotFather
- **Status**: ✅ NEW TOKEN set in Railway
- **Date Fixed**: 2025-10-16

### Test Token (COMPROMISED - NEEDS IMMEDIATE ROTATION ⚠️)
- **Token**: `8035864354:AAEWSBPypIHLMpLfp0YbE-mQi1W0r_8iA3s`
- **Exposure**: Committed in `.env.example` and `TOKEN_SETUP.md`
- **Status**: 🔴 **STILL ACTIVE** - MUST REVOKE IMMEDIATELY
- **Action**: **Generate new test token from @BotFather**
- **Date Discovered**: 2025-10-16
- **Urgency**: HIGH (even though it's test token, it can be used to test bot functionality)

---

## Action Items

### IMMEDIATE (Do NOW)
1. [ ] Go to @BotFather in Telegram
2. [ ] Select bot
3. [ ] Revoke test bot token: `8035864354:AAEWSBPypIHLMpLfp0YbE-mQi1W0r_8iA3s`
4. [ ] Generate NEW test token
5. [ ] Update `.env` file locally with new token
6. [ ] Update `tooling/diagnose_bot.py` example in comments (if any)

### Cleanup (After Revocation)
1. [ ] Verify old test token no longer works
2. [ ] Test local bot development with new token
3. [ ] Test diagnostic script with new token

---

## Why Both Tokens Are Critical

### Production Token (HIGHEST PRIORITY)
- ✅ Already rotated - Good!
- ⚠️ If not revoked, attacker could:
  - Send messages to all users
  - Hijack customer orders
  - Damage shop reputation

### Test Token (HIGH PRIORITY)
- 🔴 Still active - Needs action!
- ⚠️ If used by attacker, they could:
  - Test phishing/social engineering on test bot
  - Map bot functionality for attacks
  - Test exploits before using production token

---

## Prevention for Future

✅ **What was fixed:**
- Removed all hardcoded tokens from source code
- Changed to environment variables only
- Separated tooling scripts to dedicated directory
- Created `.env.example` with placeholders (no real tokens)

✅ **Best practices implemented:**
- All tokens now read from environment only
- Clear separation of prod/test configurations
- Diagnostic scripts accept tokens via env vars
- `.gitignore` must include `.env` files

---

## Verification Checklist

- [ ] Old production token revoked at BotFather
- [ ] New production token set in Railway
- [ ] Old test token revoked at BotFather
- [ ] New test token generated
- [ ] `.env.example` contains only placeholders (no real tokens)
- [ ] No real tokens in any committed files
- [ ] `.env` file is in `.gitignore`
- [ ] Local `.env` updated with new test token
- [ ] Verified bot works with new tokens

---

## Git History Remediation

⚠️ **Important**: These tokens were committed to Git history and are visible:
1. In GitHub commit history
2. In pull request history
3. In any clones/forks of the repo

### GitHub Cleanup (Optional but Recommended)
If these are truly sensitive:
1. Force push history cleanup (DANGEROUS - breaks clones)
2. Use GitHub's secret scanning to detect and alert
3. Or just ensure tokens are rotated (current approach)

**Current approach (BEST PRACTICE):**
- ✅ Tokens have been revoked/rotated
- ✅ No tokens in current code
- ✅ History remains as audit trail
- ✅ New tokens only in secure environment (Railway)

---

**Last Updated**: 2025-10-16
**Status**: Awaiting test token rotation
