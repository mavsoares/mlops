# Exemplo 3 — Empacotar um "app" em .zip e reagir ao resultado
# Testa: data.archive_file, terraform_data (built-in, sem provider),
#        provisioner local-exec
# Pré-requisito: a pasta ./app já vem incluída neste exemplo.
# Se quiser testar com seu próprio código, só trocar o conteúdo dela.

terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

data "archive_file" "pacote" {
  type        = "zip"
  source_dir  = "${path.module}/app"
  output_path = "${path.module}/app.zip"
}

# terraform_data é um resource nativo do Terraform (desde a v1.4),
# por isso não precisa de "required_providers" — não vem de plugin nenhum
resource "terraform_data" "info" {
  input = data.archive_file.pacote.output_sha

  provisioner "local-exec" {
    command = "echo 'Pacote gerado em ${data.archive_file.pacote.output_path} — ${data.archive_file.pacote.output_size} bytes'"
  }
}

output "sha256_do_pacote" {
  value = data.archive_file.pacote.output_sha
}
