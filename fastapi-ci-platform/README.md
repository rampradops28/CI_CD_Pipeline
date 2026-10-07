# 🛠️ fastapi-ci-platform

A centralized, reusable GitHub Actions CI platform for FastAPI microservices.

## 📦 What is This?
This repository contains **shared CI logic** for all FastAPI microservices in the organization. 
Application repositories do not write their own test or Docker build steps; they simply invoke `reusable-pipeline.yml`.

## 🚀 How Microservices Use It
In an application repository (`user-service`, `order-service`), create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  ci:
    uses: rampradops28/fastapi-ci-platform/.github/workflows/reusable-pipeline.yml@v1
    with:
      working-directory: "."
      python-version: "3.11"
      min-coverage: 80
      image-name: "user-service"
      app-port: 8000
      health-endpoint: "/health"
```

## 🏷️ Versioning
* `@v1`: Stable release for version 1.
* When breaking changes occur, release `@v2`. Services can upgrade when ready.
