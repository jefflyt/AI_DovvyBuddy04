# Database Setup Guide for DovvyBuddy

**Purpose:** Set up a Neon Postgres instance with pgvector extension for DovvyBuddy V1.  
**Required Before:** PR1 (Database Schema & Migrations) implementation.  
**Estimated Time:** 15-20 minutes.

---

## Prerequisites

- [ ] GitHub account (for Neon sign-in, or use email).
- [ ] Email address for account verification.
- [ ] Credit card (optional, Neon free tier is sufficient for V1).

---

## Step 1: Create a Neon Account

1. **Navigate to Neon:**
   - Go to https://neon.tech

2. **Sign Up:**
   - Click "Sign Up" or "Get Started".
   - Choose sign-in method:
     - **GitHub** (recommended for developer workflow).
     - **Google**.
     - **Email** (requires verification).

3. **Verify Email (if using email sign-up):**
   - Check your inbox for verification email.
   - Click verification link.

4. **Complete Onboarding:**
   - You'll be taken to the Neon console dashboard.

---

## Step 2: Create a New Project

1. **Create Project:**
   - Click "Create a project" or "New Project" button.

2. **Configure Project Settings:**
   - **Project Name:** `dovvybuddy` (or `dovvybuddy-dev` for development).
   - **Postgres Version:** 16 or 17 (latest stable, both support pgvector).
   - **Region:** Choose closest to your location or target users:
     - **US East (Ohio)** — `us-east-2` (good for North America).
     - **US West (Oregon)** — `us-west-2`.
     - **Europe (Frankfurt)** — `eu-central-1`.
     - **Asia Pacific (Singapore)** — `ap-southeast-1`.
   - **Compute Size:**
     - **Free Tier (0.25 CU)** — Sufficient for V1 development and testing.
     - Scale up later if needed.

3. **Click "Create Project":**
   - Neon will provision your database (takes ~30 seconds).

---

## Step 3: Get Your Connection String

1. **Navigate to Connection Details:**
   - After project creation, you'll see the "Connection Details" panel.
   - Or click on your project → "Dashboard" → "Connection Details".

2. **Copy Connection String:**
   - **Connection String Format:** Select **"Connection string"** tab.
   - **Database:** Use the default `neondb` database (or rename if preferred).
   - **Role:** Use the default role (usually `<your-username>`).
   - Copy the full connection string. It will look like:
     ```
     postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
     ```

3. **Save Connection String:**
   - Store this securely. You'll add it to `.env` in Step 5.
   - **Important:** This contains your database password. Do not commit to git.

---

## Step 4: Enable pgvector Extension

Neon supports pgvector, but it must be enabled for your database.

1. **Open SQL Editor:**
   - In the Neon console, navigate to your project.
   - Click "SQL Editor" in the left sidebar.
   - Or use the "Query" tab.

2. **Run Extension Enable Command:**
   - Paste and execute the following SQL:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```

3. **Verify Extension:**
   - Run this query to confirm:
     ```sql
     SELECT * FROM pg_extension WHERE extname = 'vector';
     ```
   - Expected result: One row with `extname = 'vector'`.

4. **Enable UUID Extension (Optional but Recommended):**
   - Run:
     ```sql
     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
     ```
   - This enables `uuid_generate_v4()` function for primary keys.

---

## Step 5: Configure Local Environment

1. **Create `.env` File:**
   - In your project root (`AI_DovvyBuddy04/`), create a `.env` file:
     ```bash
     touch .env
     ```

2. **Add Database URL:**
   - Open `.env` in your editor.
   - Add the connection string from Step 3:
     ```env
     DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
     ```

3. **Verify `.gitignore`:**
   - Ensure `.env` is listed in `.gitignore` (should already be there from PR0).
   - **Never commit `.env` to git.**

---

## Step 6: Test Connection (Optional)

Before implementing PR1, verify your local environment can connect to Neon.

### Option A: Using `psql` (Command Line)

1. **Install `psql` (if not already installed):**
   - **macOS:** `brew install postgresql` (or `postgresql@16`).
   - **Linux:** `sudo apt-get install postgresql-client`.
   - **Windows:** Download from https://www.postgresql.org/download/windows/

2. **Connect to Neon:**

   ```bash
   psql "postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require"
   ```

3. **Run Test Query:**

   ```sql
   SELECT version();
   ```

   - Expected: Postgres version info.

4. **Exit:**
   ```sql
   \q
   ```

### Option B: Using Neon SQL Editor (Web)

1. Navigate to Neon console → SQL Editor.
2. Run:
   ```sql
   SELECT current_database(), current_user;
   ```
3. Expected: Shows `neondb` (or your database name) and your username.

---

## Step 7: Understand Neon Limits (Free Tier)

For V1 development, the free tier is sufficient. Be aware of limits:

- **Compute Hours:** ~100 hours/month (auto-suspends after inactivity).
- **Storage:** 3 GiB.
- **Branches:** 10 branches (useful for testing migrations).
- **No Credit Card Required:** For free tier.

**Upgrade if needed:**

- V1 production may require "Launch" or "Scale" tier.
- Monitor usage in Neon console → "Usage" tab.

---

## Step 8: (Optional) Create a Separate Database for Testing

If you want isolated test environment:

1. **Create New Database:**
   - In Neon SQL Editor, run:
     ```sql
     CREATE DATABASE dovvybuddy_test;
     ```

2. **Create Test Connection String:**
   - Replace `/neondb` with `/dovvybuddy_test` in your connection string.
   - Add to `.env`:
     ```env
     DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/neondb?sslmode=require
     DATABASE_URL_TEST=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/dovvybuddy_test?sslmode=require
     ```

3. **Enable Extensions in Test Database:**
   - Connect to `dovvybuddy_test` and run:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
     ```

---

## Step 9: Next Steps (Ready for PR1)

Once your database is set up and connection string is in `.env`:

✅ **You are ready to implement PR1: Database Schema & Migrations.**

PR1 will:

- Install Drizzle ORM and dependencies.
- Define schema for 5 tables (destinations, dive_sites, leads, sessions, content_embeddings).
- Generate and run migrations.
- Seed initial data (1 destination, 5-10 dive sites).

**Start PR1:**

```bash
git checkout -b feature/pr1-database-schema
```

Refer to `docs/plans/PR1-Database-Schema.md` for implementation details.

---

## Troubleshooting

### Issue: Connection Timeout or Refused

**Possible Causes:**

- Incorrect connection string (check for typos).
- Network/firewall blocking port 5432.
- Neon project suspended (free tier auto-suspends after inactivity).

**Solutions:**

- Verify connection string in `.env` matches Neon console.
- Check Neon console → "Operations" tab for project status.
- Wake suspended project by visiting Neon dashboard.

### Issue: `extension "vector" does not exist`

**Cause:** pgvector extension not enabled.

**Solution:**

- Run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor (Step 4).

### Issue: `permission denied for database`

**Cause:** Using wrong database or role.

**Solution:**

- Verify database name in connection string matches created database.
- Use the default role provided by Neon (usually your username).

### Issue: SSL Connection Error

**Cause:** `sslmode=require` parameter missing.

**Solution:**

- Ensure connection string includes `?sslmode=require` at the end.

---

## Security Best Practices

1. **Never Commit Credentials:**
   - `.env` must be in `.gitignore`.
   - Use environment variables in CI/CD (GitHub Secrets).

2. **Rotate Passwords Regularly:**
   - Reset password in Neon console → Project → Settings → "Reset password".

3. **Limit Access:**
   - Use Neon's IP allowlist feature (paid tiers) if deploying to production.

4. **Use Read-Only Roles (Future):**
   - For analytics or reporting, create read-only database users.

---

## Additional Resources

- **Neon Documentation:** https://neon.tech/docs
- **pgvector Documentation:** https://github.com/pgvector/pgvector
- **Drizzle ORM + Neon Guide:** https://orm.drizzle.team/docs/get-started-postgresql#neon
- **Postgres Connection Strings:** https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING

---

## Summary Checklist

Before starting PR1, confirm:

- [ ] Neon account created.
- [ ] Postgres project created (`dovvybuddy`).
- [ ] Connection string saved to `.env` as `DATABASE_URL`.
- [ ] pgvector extension enabled (`CREATE EXTENSION vector`).
- [ ] uuid-ossp extension enabled (`CREATE EXTENSION "uuid-ossp"`).
- [ ] Connection tested (via `psql` or Neon SQL Editor).
- [ ] `.env` is in `.gitignore` (not committed).

**You are ready to proceed with PR1! 🚀**

---

**End of Database Setup Guide**
