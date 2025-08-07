# AWS Titanic Machine Learning Project

This project implements a machine learning model to predict survival on the Titanic using a Random Forest classifier. The model is trained on data retrieved from an S3 bucket and is designed to be deployed in an AWS Lambda environment.

## Project Structure

```
aws-titanic-ml
├── src
│   └── train_titanic_lambda.py  # Main logic for training the model
├── requirements.txt              # Python dependencies
├── Dockerfile                     # Instructions to build the Docker image
├── .env.example                   # Example environment variables
└── README.md                      # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd aws-titanic-ml
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Export the required variables or copy `.env.example` to `.env` and fill in the values:
   ```
   AWS_S3_BUCKET=<your-s3-bucket>
   TITANIC_DATA_KEY=<path-to-titanic-data>
   MODEL_S3_KEY=<path-to-save-model>
   ```

## Usage

To train the model, you can invoke the `lambda_handler` function defined in `src/train_titanic_lambda.py`. This function will read the Titanic dataset from S3, preprocess the data, train the Random Forest model, and save the trained model back to S3.

## Docker

To build the Docker image, run the following command in the project root:
```bash
docker build -t aws-titanic-ml .
```

To run the Docker container:
```bash
docker run -e AWS_S3_BUCKET=<your-s3-bucket> -e TITANIC_DATA_KEY=<path-to-titanic-data> -e MODEL_S3_KEY=<path-to-save-model> aws-titanic-ml
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.