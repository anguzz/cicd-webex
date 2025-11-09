

# cicd-webex

This project demonstrates a local CI/CD pipeline using Jenkins, GitHub webhooks, and a WebEx bot for build notifications. The goal is to show a full integration flow where a code commit automatically triggers a Jenkins build, runs Python unit tests, and posts the results to a WebEx space.

---

## Requirements

* GitHub repository
* Docker installed
* Ngrok for exposing Jenkins to the internet
* WebEx bot credentials

---

## Directory Structure

```
cicd-webex/
├── calculator.py
├── test_calculator.py
├── Jenkinsfile
├── dockerfile
├── requirements.txt
├── .gitignore
├── .env
├── README.md
└── project.txt
```



## Docker Setup (Linux / Mint OS)

Below are the installation steps adapted from the official Docker documentation.

```bash
# Add Docker’s GPG key and repository
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify Docker is running:

```bash
sudo systemctl status docker
```

If it is inactive, start it:

```bash
sudo systemctl start docker
```

To avoid using `sudo` with Docker commands:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## Ngrok Setup

Ngrok creates a secure tunnel so GitHub webhooks can reach your local Jenkins instance.

Install ngrok using the official repository:

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null

echo "deb https://ngrok-agent.s3.amazonaws.com bookworm main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list

sudo apt update && sudo apt install ngrok
```

Add your authentication token:

```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
```

Start the tunnel:

```bash
ngrok http 8080
```

Example output:

```
Forwarding  https://example-subdomain.ngrok-free.app -> http://localhost:8080
```

The HTTPS forwarding URL will be used when setting up the GitHub webhook.

---

## WebEx Bot Setup

Create a WebEx bot at [https://developer.webex.com](https://developer.webex.com).
After generating your access token and identifying your target space (room), create a `.env` file in your project root:

```
WEBEX_BOT_TOKEN=your_bot_token_here
WEBEX_ROOM_ID=your_room_id_here
```

Make sure the bot is a member of the WebEx room it will post to.

---

## Running Jenkins in Docker

Instead of using the default Jenkins image, build one that already includes Python and Git.

**Dockerfile:**

```dockerfile
FROM jenkins/jenkins:lts-jdk17

USER root
RUN apt-get update && \
    apt-get install -y git python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

USER jenkins
```

**Build and run the container:**

```bash
docker build -t jenkins-python .
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v $(pwd):/workspace \
  jenkins-python
```

Access Jenkins at `http://localhost:8080`.
Retrieve the admin password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Install the recommended plugins and create an admin account.

---

## Adding WebEx Credentials in Jenkins

1. Navigate to
   Manage Jenkins → Credentials → System → Global credentials (unrestricted)
2. Add the following credentials:

**WebEx Bot Token**

* Kind: Secret text
* Secret: `WEBEX_BOT_TOKEN` value
* ID: `WEBEX_BOT_TOKEN`
* Description: WebEx Bot API Token

**WebEx Room ID**

* Kind: Secret text
* Secret: `WEBEX_ROOM_ID` value
* ID: `WEBEX_ROOM_ID`
* Description: WebEx Room ID

---

## Creating the Jenkins CI/CD Pipeline

1. Go to Jenkins → New Item → Pipeline
2. Name the job `cicd-webex-pipeline`
3. Under **Pipeline Definition**, select **Pipeline script from SCM**
4. Set SCM to **Git**
5. Repository URL: `https://github.com/anguzz/cicd-webex.git`
6. Branch: `*/main`
7. Script path: `Jenkinsfile`
8. Under **Build Triggers**, enable **GitHub hook trigger for GITScm polling**
9. Disable **Lightweight checkout** (important for proper webhook handling)
10. Save the configuration.

---

## GitHub Webhook Setup

In your GitHub repository:

1. Go to **Settings → Webhooks → Add Webhook**
2. Fill out the form:

| Field        | Value                                                           |
| ------------ | --------------------------------------------------------------- |
| Payload URL  | `https://<your-ngrok-subdomain>.ngrok-free.app/github-webhook/` |
| Content type | `application/json`                                              |
| Secret       | leave blank                                                     |
| Event type   | Just the push event                                             |
| Active       | checked                                                         |

After saving, confirm that GitHub returns a **200 OK** on the test delivery.

---

## Quick CI/CD and WebEx Checklist

**Jenkins**

* Container is running and accessible at `http://localhost:8080`
* Job name is `cicd-webex-pipeline`
* SCM points to the GitHub repository on the `main` branch
* Trigger enabled for GitHub hook polling
* Credentials set for `WEBEX_BOT_TOKEN` and `WEBEX_ROOM_ID`
* Lightweight checkout disabled

**Ngrok**

* Tunnel started with `ngrok http 8080`
* URL forwards correctly to `http://localhost:8080`

**GitHub**

* Webhook configured for push events
* Payload URL uses the current ngrok URL with `/github-webhook/`
* Recent deliveries show **Response 200 OK**

**WebEx**

* Bot and room credentials are valid
* Bot successfully posts after builds

---

## Testing the Pipeline

Commit and push a small change to your repository:

```bash
git add .
git commit -m "Trigger CI/CD test"
git push
```

You should see:

* The ngrok terminal logging a POST from GitHub
* Jenkins automatically starting a new build
* The WebEx space receiving a success or failure message

---

## Troubleshooting

**Issue:** Webhook POSTs appear in Jenkins logs, but the build does not start
**Fix:** Disable “Lightweight checkout” in the pipeline configuration. This prevents the SCM from misinterpreting webhook payloads and skipping triggers.

**Issue:** Jenkins cannot delete or create jobs after container rebuild
**Fix:** Reset permissions on the `jenkins_home` volume:

```bash
docker run --rm -u root -v jenkins_home:/var/jenkins_home alpine sh -c "chown -R 1000:1000 /var/jenkins_home"
docker restart jenkins
```

**Issue:** GitHub webhook shows 404 or “Failed to connect”
**Fix:**

* Ensure ngrok is running and the correct HTTPS URL is set in GitHub
* The webhook endpoint must be `/github-webhook/` with a trailing slash

**Issue:** Jenkins builds run but WebEx notifications show `null` or are missing
**Fix:**

* Recheck WebEx credentials in Jenkins under Global Credentials
* Confirm the bot is added to the correct room
* Restart Jenkins after updating credentials

**Issue:** Jenkins lost connection after container rebuild
**Fix:**

* Rebuild the image using the provided Dockerfile
* Recreate the pipeline configuration
* Verify that the “GitHub hook trigger for GITScm polling” is enabled

---

