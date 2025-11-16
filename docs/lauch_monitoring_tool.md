moitoring tool is sentry
you have to create an account on sentry.io
then create a new project for your application
after creating the project, you will get a DSN (Data Source Name) URL


after that you need to install Self-Hosted Sentry

```
VERSION=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/getsentry/self-hosted/releases/latest)
VERSION=${VERSION##*/}
git clone https://github.com/getsentry/self-hosted.git
cd self-hosted
git checkout ${VERSION}
./install.sh
# After installation, run the following to start Sentry:
docker compose up --wait
```