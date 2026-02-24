output "ec2_security_group_id" {
  description = "ID of the EC2 security group"
  value       = aws_security_group.ec2.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group (empty if not created)"
  value       = var.create_rds_sg ? aws_security_group.rds[0].id : ""
}
