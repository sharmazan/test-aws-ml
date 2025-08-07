terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.3.0"
  
  # Add remote backend configuration (uncomment and configure)
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "titanic-ml/terraform.tfstate"
  #   region         = "eu-central-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "titanic-ml"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Rest of the configuration remains similar but with added outputs

resource "aws_iam_role" "lambda_exec" {
  name = "titanic_lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "titanic_lambda_s3_policy"
  description = "Allow Lambda to access S3 buckets"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# Variable for the Lambda Layer ARN
variable "layer_arn" {
  description = "ARN of the Lambda Layer containing dependencies"
  type        = string
}

resource "aws_lambda_function" "titanic_train" {
  function_name = "titanic-train"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "train_titanic_lambda.lambda_handler"
  runtime       = "python3.11"
  filename      = "function.zip"
  timeout       = 300  # Increased timeout for ML training
  memory_size   = 1024  # Increased memory for ML processing

  # Use the layer from the variable
  layers = [var.layer_arn]

  environment {
    variables = {
      AWS_S3_BUCKET    = var.s3_bucket
      TITANIC_DATA_KEY = var.titanic_data_key
      MODEL_S3_KEY     = var.model_s3_key
      PYTHONPATH       = "/opt/python"  # Important for Lambda to find the layer modules
    }
  }

  # Ensure the function has enough resources and time to complete
  ephemeral_storage {
    size = 1024  # 1GB of /tmp space
  }
}
