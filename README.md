# Jobwatcher

## 1) Install Termux + Termux:API
```bash
pkg update -y && pkg upgrade -y
pkg install -y python git termux-api cronie termux-services
termux-setup-storage   # optional
```

## 2) Get the project
```bash
cd ~
# if you downloaded the zip, just unzip; otherwise:
git clone <your-repo-url> jobwatcher
cd jobwatcher
```

## 3) First run (auto-installs pip deps)
```bash
python app/bootstrap.py
```

## 4) Notifications
Requires Termux:API and Android notification permission. Notifications include only the internal job ID.
To view the full job later:
```bash
python tools/fetch_by_id.py 101
```

## 5) Cron every 30 minutes
```bash
sv-enable crond
sv up crond
crontab -e
```
Add:
```
*/20 * * * * /data/data/com.termux/files/usr/bin/python /data/data/com.termux/files/home/jobwatcher/app/bootstrap.py >> /data/data/com.termux/files/home/jobwatcher/cron.log 2>&1
```

## 6) Add real sites
- Create a new file in `app/sites/`.
- Set a unique `SITE_KEY` and implement `scrape()` that yields `Job` objects.
- Update `app/sites/registry.py` to include your module.

> Use a **stable** `external_id` (prefer a site-provided job id; fallback to the job URL).
