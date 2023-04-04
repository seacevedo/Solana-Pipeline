terraform {
  required_version = ">= 1.0"
  backend "local" {}  # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.GOOGLE_CLOUD_PROJECT_ID
  region = var.GOOGLE_CLOUD_REGION
  credentials = file(var.SERVICE_ACCOUNT_FILE_PATH)
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "google-cloud-bucket" {
  name          = var.GOOGLE_CLOUD_BUCKET_NAME  # Concatenating DL bucket & Project name for unique naming
  location      = var.GOOGLE_CLOUD_REGION

  # Optional, but recommended settings:
  storage_class = var.GOOGLE_CLOUD_BUCKET_STORAGE_CLASS
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 60  // days
    }
  }

  force_destroy = true
}

# DWH
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET_ID
  project    = var.GOOGLE_CLOUD_PROJECT_ID
  location   = var.GOOGLE_CLOUD_REGION
}

resource "google_compute_instance" "project-vm" {
    name = var.COMPUTE_VM_NAME
    machine_type = var.COMPUTE_VM_MACHINE_TYPE
    zone = var.COMPUTE_VM_REGION

    metadata = {
      ssh-keys = "${var.SSH_USER}:${file(var.SSH_PUBLIC_KEY_PATH)}"
      # "PREFECT_API_KEY" = var.PREFECT_API_KEY
      # "PREFECT_API_URL" = var.PREFECT_API_URL
      # "PREFECT_AGENT_QUEUE_NAME" = var.PREFECT_AGENT_QUEUE_NAME
    }

    boot_disk {
        initialize_params {
            image = var.COMPUTE_VM_IMG
        }
    }

    service_account {
        email  = var.SERVICE_ACCOUNT_EMAIL
        scopes = ["cloud-platform"]
    }

    network_interface {
        network = "default"
        access_config {

        }
  }


}