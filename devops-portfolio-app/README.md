# DevOps Portfolio App

A deliberately small Flask app used as the payload for a CI/CD + Docker + AWS
pipeline. The app itself does almost nothing — one homepage, a `/health`
endpoint, and a `/api/info` endpoint — because the point of this repo is
everything *around* the app, not the app.

## What this demonstrates

- **Docker**: multi-stage build, non-root user, `HEALTHCHECK`, small final image
- **CI**: automated lint + test on every push/PR (GitHub Actions)
- **CD**: build → push to Amazon ECR → deploy to AWS App Runner, gated on tests passing
- **AWS auth without long-lived keys**: GitHub OIDC federation instead of stored `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`
- **Infrastructure as Code**: the AWS side (ECR repo, App Runner service, IAM roles) is defined in Terraform, not clicked together in the console

## Project structure

```
devops-portfolio-app/
├── app/
│   ├── main.py              # Flask app: /, /health, /api/info
│   ├── templates/index.html # homepage template
│   ├── requirements.txt     # runtime deps
│   └── requirements-dev.txt # + pytest/flake8 for CI
├── tests/
│   └── test_main.py         # pytest suite CI runs on every push
├── infra/terraform/
│   ├── provider.tf          # AWS provider + backend config
│   ├── variables.tf         # region, app name, github org/repo
│   ├── main.tf              # ECR repo, App Runner service, IAM/OIDC role
│   └── outputs.tf           # values to copy into GitHub secrets
├── .github/workflows/
│   └── ci-cd.yml            # test -> build & push -> deploy
├── Dockerfile                # multi-stage build, runs as non-root on :8080
├── docker-compose.yml         # `docker compose up` for local dev
├── .dockerignore
└── .gitignore
```

### Why each file exists

| File | Purpose |
|---|---|
| `app/main.py` | The whole application. `/health` is what Docker's `HEALTHCHECK`, App Runner's health check, and the pipeline's smoke test all call. `/api/info` reports the deployed version so you can confirm a deploy actually shipped. |
| `Dockerfile` | Two stages: a `builder` stage installs Python deps into a venv, and a slim `runtime` stage copies only that venv + app code — keeps the final image small and free of build tooling. Runs as a non-root `app` user and serves via `gunicorn`, not Flask's dev server. |
| `docker-compose.yml` | One command (`docker compose up`) to build and run the container locally with the same health check as production. |
| `.dockerignore` | Keeps `.git`, tests, and docs out of the build context so builds are faster and images don't leak source history. |
| `tests/test_main.py` | Exercises all three routes. This is what `pytest` runs in CI before anything is allowed to build or deploy. |
| `.github/workflows/ci-cd.yml` | Three jobs, each gating the next: `test` (lint + pytest) → `build-and-push` (only on `main`, builds the Docker image, tags it with the git SHA, pushes to ECR) → `deploy` (triggers an App Runner deployment, waits for it to stabilize, then hits `/health` as a smoke test). Uses OIDC (`aws-actions/configure-aws-credentials` with `role-to-assume`) instead of storing AWS keys as secrets. |
| `infra/terraform/main.tf` | The AWS side as code: an ECR repo with image scanning + a lifecycle policy (keep last 10 images), an App Runner service that pulls from that repo, and the IAM OIDC trust relationship GitHub Actions assumes to deploy. |
| `infra/terraform/outputs.tf` | Prints the two values (`AWS_ROLE_ARN`, `APP_RUNNER_SERVICE_ARN`) you paste into GitHub repo secrets after `terraform apply`. |

## Running locally

```bash
docker compose up --build
curl http://localhost:8080/health
```

## Deploying the AWS infrastructure

```bash
cd infra/terraform
terraform init
terraform apply -var="github_org=<your-username>" -var="github_repo=devops-portfolio-app"
```

Copy the `github_actions_role_arn` and `app_runner_service_arn` outputs into
your GitHub repo's **Settings → Secrets and variables → Actions** as
`AWS_ROLE_ARN` and `APP_RUNNER_SERVICE_ARN`. Push to `main` and the pipeline
takes it from there.

## Pipeline flow

```
push to main
     │
     ▼
 [test]  lint (flake8) + unit tests (pytest)
     │  (must pass)
     ▼
 [build-and-push]  docker build → tag with commit SHA → push to ECR
     │
     ▼
 [deploy]  aws apprunner start-deployment → wait for stable → curl /health
```
