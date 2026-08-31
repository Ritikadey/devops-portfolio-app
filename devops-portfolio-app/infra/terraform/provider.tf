terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Recommended for a real project: a remote backend (S3 + DynamoDB lock)
  # so state isn't sitting on a laptop.
  #
  # backend "s3" {
  #   bucket         = "your-tfstate-bucket"
  #   key            = "devops-portfolio-app/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}
