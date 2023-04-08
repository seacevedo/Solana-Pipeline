
variable "GOOGLE_CLOUD_PROJECT_ID" {
  description = "ID of your google cloud project"
  type = string
}

variable "GOOGLE_CLOUD_REGION" {
  description = "Region that your google cloud project is hosted in"
  type = string
  default = "us-central1"
}

variable "GOOGLE_CLOUD_BUCKET_NAME" {
  description = "Bucket name you want to add csv file to"
  type = string
}

variable "GOOGLE_CLOUD_BUCKET_STORAGE_CLASS" {
  description = "Class of your GCS bucket"
  type = string
  default = "STANDARD"
}

variable "BQ_DATASET_ID" {
  description = "ID of your bigquery dataset"
  type = string
  default = "solana_subreddit_posts"
}

variable "COMPUTE_VM_NAME" {
  description = "Name of your cloud VM environment"
  type = string
}

variable "COMPUTE_VM_MACHINE_TYPE" {
  description = "Machine type of your cloud VM environment"
  type = string
  default = "e2-standard-4"
}

variable "COMPUTE_VM_IMG" {
  description = "Image of your cloud VM environment"
  type = string
  default = "ubuntu-2204-jammy-v20230302"
}

variable "COMPUTE_VM_REGION" {
  description = "Region of your cloud VM environment"
  type = string
  default = "us-central1-a"
}

variable "SERVICE_ACCOUNT_EMAIL" {
  description = "Email of your service account"
  type = string
}

variable "SSH_USER" {
  description = "User of the cloud VM environment"
  type = string
}

variable "SSH_PUBLIC_KEY_PATH" {
  description = "Path where your SSH public key is located"
  type = string
}

variable "SETUP_SCRIPT_PATH" {
  description = "Path where your setup.sh script is located"
  type = string
}

variable "SERVICE_ACCOUNT_FILE_PATH" {
  description = "Path where your service account keyfile JSON file is located"
  type = string
}

