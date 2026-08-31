output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "app_runner_service_url" {
  value = aws_apprunner_service.app.service_url
}

output "app_runner_service_arn" {
  description = "Set this as the APP_RUNNER_SERVICE_ARN secret in GitHub"
  value       = aws_apprunner_service.app.arn
}

output "github_actions_role_arn" {
  description = "Set this as the AWS_ROLE_ARN secret in GitHub"
  value       = aws_iam_role.github_actions.arn
}
