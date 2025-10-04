# Security CI Vulnerable Playground

This repository intentionally contains insecure infrastructure-as-code, application code, and configuration so that you can validate static and dynamic security analysis tools.

## Contents

| Area | Location | Example Issues |
| --- | --- | --- |
| Container image | [`Dockerfile`](Dockerfile) | Outdated base image, hard-coded secrets, unnecessary packages |
| Docker Compose | [`docker-compose.yml`](docker-compose.yml) | Privileged containers, plaintext secrets, host mounts |
| Python web app | [`app/`](app/) | SQL injection, command injection, unsafe `exec`, debug mode |
| Node.js service | [`node-app/`](node-app/) | `eval` usage, directory traversal, outdated dependencies |
| Ruby service | [`ruby-app/`](ruby-app/) | Insecure cookies, command execution, outdated gems |
| Go service | [`go-app/`](go-app/) | SQL injection, command execution, hard-coded credentials |
| Shell scripts | [`scripts/`](scripts/) | Unquoted variables, plaintext secrets, destructive `rm -rf` |
| Java sample | [`java/src/com/example/vulnerable/Vulnerable.java`](java/src/com/example/vulnerable/Vulnerable.java) | SQL injection, command execution |
| Terraform IaC | [`terraform/main.tf`](terraform/main.tf) | Public S3 bucket, open security group, hard-coded credentials |
| Additional IaC | [`iac/`](iac/) | Insecure CloudFormation and Kubernetes manifests |
| SonarQube config | [`sonar-project.properties`](sonar-project.properties) | Points scanners to vulnerable sources |

## Suggested Scans

Use the files in this repository to exercise the following security tools:

- **Checkov, Falcon Cloud Security (IaC), Terrascan:** scan [`terraform/`](terraform/) and [`iac/`](iac/) for misconfigurations and secrets.
- **Trivy, Grype:** scan the [`Dockerfile`](Dockerfile) or the resulting image to detect vulnerable packages and OS issues.
- **Dependency-Track:** import [`app/requirements.txt`](app/requirements.txt), [`node-app/package.json`](node-app/package.json), [`ruby-app/Gemfile`](ruby-app/Gemfile), or [`go-app/go.mod`](go-app/go.mod) to flag outdated libraries.
- **Semgrep:** analyze [`app/main.py`](app/main.py) and [`node-app/server.js`](node-app/server.js) for insecure patterns.
- **Semgrep (multilang):** extend scans to [`ruby-app/insecure.rb`](ruby-app/insecure.rb) and [`go-app/main.go`](go-app/main.go) for additional rule coverage.
- **ShellCheck:** lint [`scripts/insecure.sh`](scripts/insecure.sh) and [`scripts/unsafe_backup.sh`](scripts/unsafe_backup.sh) to find shell scripting mistakes.
- **SonarQube:** run against the repository using [`sonar-project.properties`](sonar-project.properties) to surface code quality and security hotspots.

> **Warning:** Never deploy this code to production. It is intentionally insecure and is provided only for testing and demonstration purposes.
