terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
  type    = string
}

variable "environment" {
  default = "dev"
  type    = string
}

# S3 buckets for data lake
resource "aws_s3_bucket" "bronze" {
  bucket = "${var.environment}-data-bronze"
  
  tags = {
    Environment = var.environment
    Layer        = "bronze"
  }
}

resource "aws_s3_bucket" "silver" {
  bucket = "${var.environment}-data-silver"
  
  tags = {
    Environment = var.environment
    Layer       = "silver"
  }
}

resource "aws_s3_bucket" "gold" {
  bucket = "${var.environment}-data-gold"
  
  tags = {
    Environment = var.environment
    Layer       = "gold"
  }
}

# S3 bucket versioning and encryption
resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# RDS for metadata (dbt, Airflow)
resource "aws_db_instance" "metadata" {
  identifier           = "${var.environment}-metadata-db"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.medium"
  allocated_storage     = 50
  max_allocated_storage = 200
  
  db_name  = "metadata"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.metadata.id]
  db_subnet_group_name   = aws_db_subnet_group.metadata.name
  
  backup_retention_period = 7
  skip_final_snapshot     = true
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "metadata" {
  name       = "${var.environment}-metadata-subnet"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "metadata" {
  name        = "${var.environment}-metadata-sg"
  description = "Security group for metadata database"
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  tags = {
    Environment = var.environment
  }
}

# EKS cluster for Airflow, MLflow, etc.
resource "aws_eks_cluster" "data_platform" {
  name     = "${var.environment}-data-platform"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.27"
  
  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false
  }
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role" "eks_cluster" {
  name = "${var.environment}-eks-cluster-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}

# EKS node group
resource "aws_eks_node_group" "data_platform" {
  cluster_name    = aws_eks_cluster.data_platform.name
  node_group_name = "${var.environment}-data-workers"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = var.subnet_ids
  
  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 1
  }
  
  ami_type = "AL2023_1_0"
  capacity_type = "ON_DEMAND"
}

resource "aws_iam_role" "eks_nodes" {
  name = "${var.environment}-eks-nodes-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

# Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "${var.environment}/db-credentials"
  
  tags = {
    Environment = var.environment
  }
}

variable "db_username" {
  type      = string
  sensitive = true
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "subnet_ids" {
  type    = list(string)
}