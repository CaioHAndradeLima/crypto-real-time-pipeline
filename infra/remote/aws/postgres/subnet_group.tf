resource "aws_db_subnet_group" "postgres" {
  name       = "trading-postgres-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "trading-postgres-subnet-group"
  }
}
