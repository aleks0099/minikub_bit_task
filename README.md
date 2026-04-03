```bash
bash deploy.sh
```

---

### 1.Смотрю состояние кластера

![Общее состояние кластера](imgs/image1.png)

---

### 2. Пробросил порт

![Port-forward к сервису](imgs/image2.png)

---

### 3. Поотрпарлял запросы

![Проверка API curl](imgs/image3.png)

---

### 4. Как видно балансировка работает

![Балансировка между pod](imgs/image4.png)

---

### 5. DaemonSet


![DaemonSet и pod log-agent](imgs/image5.png)

---

### 6. Вывел smthing (перед этим записав smthing)


![Логи log-agent](imgs/image6.png)

---

### 7. CronJob

![Статус CronJob](imgs/image7.png)

---

### 8. Тут я создал Job `manual-run-2` из шаблона CronJob. при этом сделал так чтобы он жил 10 минут после выполнения. Проверил, что он выполнил создание архива и посмотрел его содержимое

![Ручная Job и логи backup](imgs/image8.png)

![Содержимое tar.gz](imgs/image9.png)
