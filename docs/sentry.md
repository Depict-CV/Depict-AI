# monitoring tool is sentry

**Sentry** is an open-source application monitoring and error-tracking platform. It helps you **detect, diagnose, and fix errors and performance issues** in your applications in real time. It captures exceptions and crashes from your app (backend, frontend, mobile, etc.), groups them, shows stack traces, and provides context (user, release, environment, breadcrumbs, etc.) so you can understand why something broke.


# Install sentry
 
 sentry is run under wsl : open wsl 

You can run it:

---


## 🚀 Getting started with Sentry locally (simple)

 **Clone Sentry self-hosted**

   ```bash
   git clone https://github.com/getsentry/onpremise.git
   cd onpremise
   ./install.sh
   ```

---

## 📦 Example: Minimal Python app error reporting

Install SDK:

```bash
pip install sentry-sdk
```

Init and trigger an event:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="http://<your_public_dsn>@localhost:9000/<project_id>",
    traces_sample_rate=1.0
)

1 / 0  # this will be reported to Sentry
```
---

## 🐳 Running on Docker (quick)

Once installed via the Sentry on-premise repo:

```bash
docker compose up -d
```





# use sentry
