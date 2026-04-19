#!/usr/bin/env bash
set -euo pipefail

wait_for_deployment() {
  local namespace="$1"
  local name="$2"

  until kubectl get deployment "$name" -n "$namespace" >/dev/null 2>&1; do
    sleep 2
  done

  kubectl rollout status deployment/"$name" -n "$namespace" --timeout=300s
}

eval "$(minikube -p minikube docker-env --shell bash)"
docker build --pull=false -t my-app:latest .

minikube addons enable istio-provisioner
minikube addons enable istio

wait_for_deployment istio-operator istio-operator
wait_for_deployment istio-system istiod
wait_for_deployment istio-system istio-ingressgateway

kubectl label namespace default istio-injection=enabled --overwrite

kubectl apply -f kube_task/configmap.yaml

kubectl delete pod my-test-pod --ignore-not-found
kubectl apply -f kube_task/pod.yaml
kubectl wait --for=condition=Ready pod/my-test-pod --timeout=180s

kubectl apply -f kube_task/deployment.yaml
kubectl apply -f kube_task/service.yaml
kubectl rollout restart deployment/my-app
kubectl rollout status deployment/my-app --timeout=300s

kubectl apply -f kube_task/daemonset-log-agent.yaml
kubectl rollout status daemonset/my-log-agent --timeout=180s

kubectl apply -f kube_task/cronjob-backup.yaml
kubectl apply -f kube_task/gateway.yaml
kubectl apply -f kube_task/virtualservice.yaml
kubectl apply -f kube_task/destinationrule.yaml
