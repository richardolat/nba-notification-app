provider "aws" {
  region = "us-east-1"
}

# Create the zip file using the `archive_file` data source
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "app"
  output_path = "${path.module}/app/lambda_function.zip"
}

resource "aws_iam_role" "lambda_execution" {
  name = "lambda_execution_role_nba_notification"  # Update the role name to something unique

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "nba_notification" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "nba_notification_function"
  role             = aws_iam_role.lambda_execution.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  environment {
    variables = {
      SPORTS_API_KEY  = var.sports_api_key
      SES_EMAIL       = var.ses_email
      RECIPIENT_EMAIL = var.recipient_email
    }
  }
}

resource "aws_cloudwatch_event_rule" "schedule_rule" {
  name                = "nba_notification_rule"
  schedule_expression = "rate(2 hours)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.schedule_rule.name
  target_id = "nba_lambda"
  arn       = aws_lambda_function.nba_notification.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.nba_notification.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule_rule.arn
}
