# Titanic MLOps Pipeline (AWS + MLflow)

## Передумови

- Python 3.8+
- AWS обліковий запис, S3 bucket
- Встановлені бібліотеки: `boto3`, `pandas`, `scikit-learn`, `mlflow`, `python-dotenv`

## Налаштування змінних середовища

Скрипти використовують змінні середовища для конфігурації. Їх можна задати у файлі `.env` або експортувати безпосередньо в оболонці.

Приклад `.env` файлу:

```
AWS_S3_BUCKET=your-bucket-name
TITANIC_DATA_PATH=datasets/titanic.csv
MODEL_S3_PATH=models/titanic_rf.pkl
LAMBDA_FUNCTION_NAME=titanic-train
```

## Кроки

Вкажіть ваш bucket та шляхи у `.env` файлі.

Налаштуйте Amazon Lambda
```bash
bash deploy/deploy_lambda.sh
```

### 1. Повний пайплайн: завантаження датасету, тренування моделі та збереження в S3

Встановіть залежності:
```bash
uv sync
```
Запустіть скрипт:

```bash
uv run train_and_upload.py
```

Скрипт автоматично завантажить Titanic датасет, завантажить його в S3, натренує модель `RandomForestClassifier` та збереже її до S3 за шляхом `MODEL_S3_PATH`.

### 2. Запуск локального MLflow сервера (опціонально)

```bash
mlflow server --backend-store-uri ./mlruns --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000
```

Інтерфейс MLflow буде доступний на [http://localhost:5000](http://localhost:5000).

### 3. Перегляд результатів

Всі експерименти, параметри, метрики та моделі будуть доступні через MLflow UI.

### 4. Передбачення через Lambda

```bash
uv run predict_lambda.py
```

Скрипт випадково обирає пасажира з тестової вибірки Titanic, виводить його дані,
викликає Lambda-функцію `LAMBDA_FUNCTION_NAME` і показує як передбачення, так і
фактичний результат.

---

**Примітка:** Для доступу до S3 потрібні налаштовані AWS credentials (`~/.aws/credentials`).

