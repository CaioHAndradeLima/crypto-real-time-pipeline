resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "trading-prod-vpc"
  }
}

resource "aws_security_group" "postgres" {
  name        = "trading-postgres-sg"
  description = "Security group for Postgres RDS"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "Postgres access from local machine"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["179.110.97.183/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "trading-postgres-sg"
  }
}

resource "aws_db_instance" "postgres" {
  identifier = "trading-prod-postgres"

  engine         = "postgres"
  engine_version = "17.7"

  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.postgres.id]
  db_subnet_group_name  = aws_db_subnet_group.postgres.name

  publicly_accessible = true
  skip_final_snapshot = true
  multi_az            = false

  tags = {
    Name = "trading-prod-postgres"
  }
}
