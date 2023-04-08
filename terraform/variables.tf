
variable "GOOGLE_CLOUD_PROJECT_ID" {
 
}

variable "GOOGLE_CLOUD_REGION" {
    default = "us-central1"
}

variable "GOOGLE_CLOUD_BUCKET_NAME" {

}

variable "GOOGLE_CLOUD_BUCKET_STORAGE_CLASS" {
  default = "STANDARD"
}

variable "BQ_DATASET_ID" {
  default = "solana_subreddit_posts"
}

variable "COMPUTE_VM_NAME" {

}

variable "COMPUTE_VM_MACHINE_TYPE" {
  default = "e2-standard-4"
}

variable "COMPUTE_VM_IMG" {
  default = "ubuntu-2204-jammy-v20230302"
}

variable "COMPUTE_VM_REGION" {
  default = "us-central1-a"
}

variable "SERVICE_ACCOUNT_EMAIL" {
  
}

variable "SSH_USER" {

}

variable "SSH_PUBLIC_KEY_PATH" {

}

variable "SETUP_SCRIPT_PATH" {

}

variable "SERVICE_ACCOUNT_FILE_PATH" {

}

