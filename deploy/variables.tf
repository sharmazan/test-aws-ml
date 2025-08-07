variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "s3_bucket" {
  description = "S3 bucket for Titanic data and model"
  type        = string
}

variable "titanic_data_key" {
  description = "S3 key for Titanic dataset"
  type        = string
  default     = "datasets/titanic.csv"
}

variable "model_s3_key" {
  description = "S3 key for trained model"
  type        = string
  default     = "models/titanic_rf.pkl"
}

variable "environment" {
  description = "Environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}
