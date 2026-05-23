output "bronze_bucket" {
  value = aws_s3_bucket.bronze.bucket
}

output "silver_bucket" {
  value = aws_s3_bucket.silver.bucket
}

output "gold_bucket" {
  value = aws_s3_bucket.gold.bucket
}

output "eks_cluster_name" {
  value = aws_eks_cluster.data_platform.name
}

output "metadata_db_endpoint" {
  value = aws_db_instance.metadata.endpoint
}