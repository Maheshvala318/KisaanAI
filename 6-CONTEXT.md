# 6-CONTEXT.md — Phase 6: Project Deployment

## Discovery Summary
The goal is to move the KisaanAI project from a loose collection of scripts to a production-hardened Docker Compose environment suitable for real-world deployment.

## Locked Decisions

### 1. Architectural Standards
- **Multi-Service Isolation**: Each core component (Rasa, Actions, Plant API, Frontend) must run in its own container with minimal footprint.
- **Communication Layer**: Use a dedicated Docker network (`kisaan-network`) with internal DNS resolution.
- **Reverse Proxy**: Nginx will eventually serve the frontend and route API calls, but for Phase 6 local stability, we will focus on direct service access with CORS enabled.

### 2. Production Hardening
- **Health Checks**: Every service MUST have a Docker-native health check.
- **Logging**: Implement centralized logging via stdout for container visibility.
- **Secrets Management**: Strict validation of `.env` variables before startup. No service should start if critical API keys are missing.

### 3. Build & Performance
- **Layer Optimization**: Use multi-stage builds where applicable (frontend).
- **Caching**: Enable caching for development stability, but ensure `.dockerignore` prevents bloat.

## Gray Areas Resolved (Production Defaults)
- **Error Handling**: Fail fast. If the Action Server or Plant API is down, Rasa should not attempt to process requests.
- **Scalability**: While running on a single host now, the configuration will use standard environment variables to allow for easy migration to Kubernetes/ECS later.
