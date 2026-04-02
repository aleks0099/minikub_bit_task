#!/usr/bin/env bash
set -euo pipefail
eval "$(minikube docker-env)"
docker build -t my-app:latest .
kubectl apply -f kube_task/configmap.yaml
kubectl apply -f kube_task/pod.yaml
kubectl wait --for=condition=Ready pod/my-test-pod --timeout=180s
kubectl apply -f kube_task/deployment.yaml
kubectl apply -f kube_task/service.yaml
kubectl rollout restart deployment/my-app
kubectl rollout status deployment/my-app --timeout=180s
kubectl apply -f kube_task/daemonset-log-agent.yaml
kubectl apply -f kube_task/cronjob-backup.yaml
kubectl rollout status daemonset/my-log-agent --timeout=180s
