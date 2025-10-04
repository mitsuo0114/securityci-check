provider "aws" {
  region                  = "us-east-1"
  access_key              = "hardcoded-access-key"
  secret_key              = "hardcoded-secret-key"
  skip_credentials_validation = true
}

resource "aws_s3_bucket" "public_bucket" {
  bucket = "insecure-public-bucket-example"
  acl    = "public-read"

  versioning {
    enabled = false
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_security_group" "open_sg" {
  name        = "insecure-security-group"
  description = "Allow all inbound traffic"
  vpc_id      = "vpc-123456"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "insecure_db" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.6"
  instance_class       = "db.t2.micro"
  name                 = "vulnerabledb"
  username             = "root"
  password             = "password"
  skip_final_snapshot  = true
  publicly_accessible  = true
  storage_encrypted    = false
}
