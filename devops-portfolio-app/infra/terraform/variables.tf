variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Name used for the ECR repo and App Runner service"
  type        = string
  default     = "devops-portfolio-app"
}

variable "github_org" {
  description = "GitHub org/user that owns the repo (for the OIDC trust policy)"
  type        = string
}

variable "github_repo" {
  description = "GitHub repo name (for the OIDC trust policy)"
  type        = string
}
