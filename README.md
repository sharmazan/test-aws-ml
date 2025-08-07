# Titanic MLOps Pipeline (AWS + MLflow)

## Передумови

- Python 3.8+
- AWS обліковий запис, S3 bucket
- Встановлені бібліотеки: `boto3`, `pandas`, `scikit-learn`, `mlflow`, `python-dotenv`

## Налаштування змінних середовища

Створіть файл `.env` у цій директорії з наступним вмістом:

```
AWS_S3_BUCKET=your-bucket-name
TITANIC_DATA_KEY=datasets/titanic.csv
```

## Кроки

### 1. Завантаження датасету в S3

1. Змініть назву bucket у скрипті на ваш власний.
2. Запустіть скрипт для завантаження датасету (створіть окремий скрипт або використайте AWS CLI):

```bash
aws s3 cp titanic.csv s3://<your-bucket-name>/datasets/titanic.csv
```

### 2. Тренування моделі та логування експерименту

1. Вкажіть ваш bucket та ключ у `.env` файлі.
2. Запустіть скрипт:

```bash
python train_titanic.py
```

### 3. Запуск локального MLflow сервера

```bash
mlflow server --backend-store-uri ./mlruns --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000
```

Інтерфейс MLflow буде доступний на [http://localhost:5000](http://localhost:5000).

### 4. Перегляд результатів

Всі експерименти, параметри, метрики та моделі будуть доступні через MLflow UI.

---

**Примітка:** Для доступу до S3 потрібні налаштовані AWS credentials (`~/.aws/credentials`).

