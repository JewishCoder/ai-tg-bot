# Secrets Management для Production Deployment

## Введение

Управление секретами (secrets management) - критически важный аспект безопасности приложения в production. Секреты включают:

- API ключи (Telegram Token, OpenRouter Key)
- Database credentials (пароли, connection strings)
- Admin tokens для регистрации
- Encryption keys
- OAuth secrets

**⚠️ Никогда не храните секреты в коде или git репозитории!**

---

## Текущий подход (Development)

В development режиме мы используем `.env` файлы через `pydantic-settings`:

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    TELEGRAM_TOKEN: str = Field(..., description="Telegram Bot API token")
    DB_PASSWORD: SecretStr = Field(..., description="Database password")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
```

**Недостатки для production:**
- ❌ Секреты хранятся в plain text на диске
- ❌ Нет ротации ключей
- ❌ Нет аудита доступа
- ❌ Сложно управлять доступом для команды

---

## Решения для Production

### 1. HashiCorp Vault

**Что это:** Централизованное хранилище секретов с динамической генерацией credentials, ротацией и аудитом.

**Преимущества:**
- ✅ Dynamic secrets (автоматическая генерация и ротация)
- ✅ Encryption at rest и in transit
- ✅ Детальный audit log
- ✅ Fine-grained access control (ACL)
- ✅ Поддержка множества backend (AWS, Azure, GCP, Kubernetes)

**Интеграция с Python:**

```bash
pip install hvac
```

```python
import hvac
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    VAULT_ADDR: str = "https://vault.example.com"
    VAULT_TOKEN: str  # Получаем через Kubernetes ServiceAccount или AppRole
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets_from_vault()
    
    def _load_secrets_from_vault(self):
        """Загружает секреты из HashiCorp Vault."""
        client = hvac.Client(url=self.VAULT_ADDR, token=self.VAULT_TOKEN)
        
        # Read secrets
        secrets = client.secrets.kv.v2.read_secret_version(
            path="ai-tg-bot/prod"
        )
        
        data = secrets["data"]["data"]
        self.TELEGRAM_TOKEN = data["telegram_token"]
        self.DB_PASSWORD = data["db_password"]
        self.OPENROUTER_KEY = data["openrouter_key"]
```

**Best Practices:**
- Используйте AppRole authentication для production
- Настройте TTL для secrets (например, 24 часа)
- Включите audit logging
- Используйте namespaces для изоляции окружений

---

### 2. AWS Secrets Manager

**Что это:** Managed сервис AWS для хранения и управления секретами с автоматической ротацией.

**Преимущества:**
- ✅ Fully managed (нет инфраструктуры)
- ✅ Интеграция с AWS IAM
- ✅ Автоматическая ротация для RDS, DocumentDB
- ✅ Encryption через AWS KMS
- ✅ Cross-region replication

**Интеграция с Python:**

```bash
pip install boto3
```

```python
import boto3
import json
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    AWS_REGION: str = "us-east-1"
    SECRET_NAME: str = "ai-tg-bot/prod"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets_from_aws()
    
    def _load_secrets_from_aws(self):
        """Загружает секреты из AWS Secrets Manager."""
        client = boto3.client(
            service_name="secretsmanager",
            region_name=self.AWS_REGION
        )
        
        response = client.get_secret_value(SecretId=self.SECRET_NAME)
        secrets = json.loads(response["SecretString"])
        
        self.TELEGRAM_TOKEN = secrets["telegram_token"]
        self.DB_PASSWORD = secrets["db_password"]
        self.OPENROUTER_KEY = secrets["openrouter_key"]
```

**Стоимость:**
- $0.40 за секрет в месяц
- $0.05 за 10,000 API calls

**Best Practices:**
- Используйте IAM roles вместо access keys
- Настройте автоматическую ротацию для database credentials
- Используйте resource-based policies для least privilege
- Включите CloudTrail logging

---

### 3. Kubernetes Secrets

**Что это:** Native mechanism Kubernetes для управления секретами в кластере.

**Преимущества:**
- ✅ Native интеграция с Kubernetes
- ✅ Автоматический inject в Pod через volumes или env vars
- ✅ RBAC для доступа
- ✅ Бесплатно (часть Kubernetes)

**Недостатки:**
- ⚠️ Secrets хранятся в base64 (не encrypted по умолчанию)
- ⚠️ Нет built-in ротации
- ⚠️ Менее безопасен чем Vault или AWS Secrets Manager

**Создание Secret:**

```bash
# Из literal values
kubectl create secret generic ai-tg-bot-secrets \
  --from-literal=telegram-token=your_token \
  --from-literal=db-password=your_password \
  --from-literal=openrouter-key=your_key \
  -n production

# Из файла
kubectl create secret generic ai-tg-bot-secrets \
  --from-file=.env.production \
  -n production
```

**Использование в Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-tg-bot
spec:
  template:
    spec:
      containers:
      - name: bot
        image: ai-tg-bot:latest
        env:
        - name: TELEGRAM_TOKEN
          valueFrom:
            secretKeyRef:
              name: ai-tg-bot-secrets
              key: telegram-token
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ai-tg-bot-secrets
              key: db-password
        - name: OPENROUTER_KEY
          valueFrom:
            secretKeyRef:
              name: ai-tg-bot-secrets
              key: openrouter-key
```

**Улучшение безопасности:**

1. **Encryption at rest:**
```bash
# Включить encryption в etcd
kubectl create secret generic encryption-config \
  --from-file=encryption-config.yaml
```

2. **External Secrets Operator:**
Интеграция с внешними хранилищами (Vault, AWS Secrets Manager):

```bash
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system
```

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "ai-tg-bot"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: ai-tg-bot-secrets
spec:
  secretStoreRef:
    name: vault-backend
  target:
    name: ai-tg-bot-secrets
  data:
  - secretKey: telegram-token
    remoteRef:
      key: ai-tg-bot/prod
      property: telegram_token
```

---

## Best Practices

### 1. Ротация ключей

**Частота:**
- Database passwords: 90 дней
- API keys: 180 дней
- Admin tokens: 30 дней

**Процесс:**
1. Генерация нового ключа
2. Добавление нового ключа в приложение (dual-key период)
3. Обновление всех клиентов
4. Удаление старого ключа
5. Мониторинг ошибок

### 2. Минимальные права доступа (Least Privilege)

```yaml
# Пример IAM policy для AWS Secrets Manager
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:ai-tg-bot/prod-*"
      ]
    }
  ]
}
```

### 3. Аудит и мониторинг

- Логируйте все обращения к секретам
- Настройте алерты на необычную активность
- Регулярно review access logs
- Используйте централизованное логирование (CloudTrail, Vault audit)

### 4. Разделение окружений

```
vault/
├── development/
│   └── ai-tg-bot/
├── staging/
│   └── ai-tg-bot/
└── production/
    └── ai-tg-bot/
```

Каждое окружение должно иметь:
- Отдельные секреты
- Отдельные access policies
- Отдельный audit trail

### 5. Никогда не логируйте секреты

```python
# ❌ ПЛОХО
logger.info(f"Connecting with password: {password}")

# ✅ ХОРОШО
logger.info("Connecting to database")

# ✅ ХОРОШО (SecretStr скрывает значение)
from pydantic import SecretStr
password: SecretStr = SecretStr("secret")
logger.info(f"Password object: {password}")  # Выведет: **********
```

---

## Рекомендации для AI TG Bot

### Для небольших deployment (< 10 инстансов)

**Рекомендация:** Kubernetes Secrets + External Secrets Operator

**Почему:**
- Простота настройки
- Нативная интеграция с Kubernetes
- Бесплатно
- External Secrets Operator добавляет безопасность

### Для средних deployment (10-100 инстансов)

**Рекомендация:** AWS Secrets Manager или HashiCorp Vault

**Почему:**
- Автоматическая ротация
- Managed service (меньше операционных затрат)
- Хорошая интеграция с CI/CD
- Audit logging

### Для крупных enterprise deployment (> 100 инстансов)

**Рекомендация:** HashiCorp Vault

**Почему:**
- Dynamic secrets
- Fine-grained access control
- Multi-cloud support
- Advanced features (namespaces, sentinel policies)

---

## Checklist для Production Deployment

### Перед deployment:

- [ ] Все секреты удалены из git истории
- [ ] `.env` файлы в `.gitignore`
- [ ] Секреты загружаются из безопасного хранилища
- [ ] Настроена ротация ключей
- [ ] Включен audit logging
- [ ] Настроены минимальные права доступа
- [ ] Протестирован процесс ротации
- [ ] Команда обучена работе с secrets manager

### После deployment:

- [ ] Мониторинг доступа к секретам настроен
- [ ] Алерты на необычную активность работают
- [ ] Резервные копии секретов созданы (в безопасном месте)
- [ ] Документация по recovery процессу готова
- [ ] Runbook для incident response создан

---

## Дополнительные ресурсы

### Документация:
- [HashiCorp Vault](https://www.vaultproject.io/docs)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [External Secrets Operator](https://external-secrets.io/)

### Best Practices:
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App: Config](https://12factor.net/config)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

---

**Последнее обновление:** 2025-10-18  
**Автор:** AI TG Bot Team

