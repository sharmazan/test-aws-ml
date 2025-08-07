variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "s3_bucket" {
  description = "S3 bucket for Titanic data and model"
  type        = string
}

variable "titanic_data_path" {
  description = "S3 path for Titanic dataset"
  type        = string
  default     = "datasets/titanic.csv"
}

variable "model_s3_path" {
  description = "S3 path for trained model"
  type        = string
  default     = "models/titanic_rf.pkl"
}

variable "environment" {
  description = "Environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}
