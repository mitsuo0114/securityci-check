# Security CI Vulnerable Playground

This repository intentionally contains insecure infrastructure-as-code, application code, and configuration so that you can validate static and dynamic security analysis tools.

## Contents

| Area | Location | Example Issues |
| --- | --- | --- |
| Container image | [`Dockerfile`](Dockerfile) | Outdated base image, hard-coded secrets, unnecessary packages |
| Python web app | [`app/`](app/) | SQL injection, command injection, unsafe `exec`, debug mode |
| Node.js service | [`node-app/`](node-app/) | `eval` usage, directory traversal, outdated dependencies |
| Shell script | [`scripts/insecure.sh`](scripts/insecure.sh) | Unquoted variables, plaintext secrets |
| Java sample | [`java/src/com/example/vulnerable/Vulnerable.java`](java/src/com/example/vulnerable/Vulnerable.java) | SQL injection, command execution |
| Terraform IaC | [`terraform/main.tf`](terraform/main.tf) | Public S3 bucket, open security group, hard-coded credentials |
| SonarQube config | [`sonar-project.properties`](sonar-project.properties) | Points scanners to vulnerable sources |

## Suggested Scans

Use the files in this repository to exercise the following security tools:

- **Checkov, Falcon Cloud Security (IaC), Terrascan:** scan [`terraform/`](terraform/) for misconfigurations and secrets.
- **Trivy, Grype:** scan the [`Dockerfile`](Dockerfile) or the resulting image to detect vulnerable packages and OS issues.
- **Dependency-Track:** import [`app/requirements.txt`](app/requirements.txt) or [`node-app/package.json`](node-app/package.json) to flag outdated libraries.
- **Semgrep:** analyze [`app/main.py`](app/main.py) and [`node-app/server.js`](node-app/server.js) for insecure patterns.
- **ShellCheck:** lint [`scripts/insecure.sh`](scripts/insecure.sh) to find shell scripting mistakes.
- **SonarQube:** run against the repository using [`sonar-project.properties`](sonar-project.properties) to surface code quality and security hotspots.

> **Warning:** Never deploy this code to production. It is intentionally insecure and is provided only for testing and demonstration purposes.
