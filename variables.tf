
# SES Sender Email (Verified SES email)
variable "ses_email" {
  description = "Verified SES sender email address"
  type        = string
  sensitive   = true
}

# SES Recipient Email (Verified SES email)
variable "recipient_email" {
  description = "Verified SES recipient email address"
  type        = string
  sensitive   = true
}

# API Key for sportsdata.io to fetch NBA scores
variable "sports_api_key" {
  description = "API key for accessing sportsdata.io to fetch NBA game data"
  type        = string
  sensitive   = true
}
