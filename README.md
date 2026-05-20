```bash
bash deploy.sh
```

---

### 1. Развернул сервисы и открыл Prometheus

![Prometheus port-forward](imgs/image15.png)

---

### 2. Проверил сбор метрик Prometheus

![Prometheus targets](imgs/image16.png)

---

### 3. Проверил работу `/log`

![Log request](imgs/image17.png)

---

### 4. Проверил счетчик вызовов `/log`

В Prometheus доступна метрика `app_log_requests_total`.

![Log requests metric](imgs/image18.png)

---

### 5. Проверил среднее время обработки запроса

Среднее время обработки `/log` `app_log_request_processing_seconds_sum / app_log_request_processing_seconds_count`.

![Average processing time metric](imgs/image19.png)
