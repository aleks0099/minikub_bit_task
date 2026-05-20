#!/usr/bin/env bash
set -euo pipefail

MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-minikube}"
MINIKUBE_DRIVER="${MINIKUBE_DRIVER:-docker}"

wait_for_deployment_object() {
  local namespace="$1"
  local name="$2"

  until kubectl get deployment "$name" -n "$namespace" >/dev/null 2>&1; do
    sleep 2
  done
}

wait_for_deployment() {
  local namespace="$1"
  local name="$2"

  wait_for_deployment_object "$namespace" "$name"
  kubectl rollout status deployment/"$name" -n "$namespace" --timeout=300s
}

patch_istio_resource_requests() {
  wait_for_deployment_object istio-system istiod
  kubectl patch deployment istiod -n istio-system --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/cpu","value":"100m"},{"op":"replace","path":"/spec/template/spec/containers/0/resources/requests/memory","value":"512Mi"}]'
}

wait_for_istiod() {
  for _ in 1 2 3 4 5; do
    patch_istio_resource_requests
    if kubectl rollout status deployment/istiod -n istio-system --timeout=120s; then
      return 0
    fi
  done
  return 1
}

minikube start -p "$MINIKUBE_PROFILE" --driver="$MINIKUBE_DRIVER"

eval "$(minikube -p "$MINIKUBE_PROFILE" docker-env --shell bash)"
DOCKER_BUILDKIT=0 docker build --pull=false -t my-app:latest .

minikube -p "$MINIKUBE_PROFILE" addons enable istio-provisioner
minikube -p "$MINIKUBE_PROFILE" addons enable istio

wait_for_deployment istio-operator istio-operator
wait_for_istiod
kubectl delete pod -n istio-system -l app=istio-ingressgateway --ignore-not-found
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
kubectl apply -f kube_task/prometheus.yaml
wait_for_deployment default prometheus
