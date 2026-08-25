# Exemplo 1 — Gerador de credenciais
# Testa: random_pet, random_password, local_sensitive_file
# Pré-requisito: nenhum. Só rodar terraform init && terraform apply.

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

resource "random_pet" "usuario" {
  length    = 2
  separator = "_"
}

resource "random_password" "senha" {
  length  = 16
  special = true
}

# local_sensitive_file é igual ao local_file, mas o Terraform
# esconde o conteúdo no plan/apply (mesma ideia do sensitive = true)
resource "local_sensitive_file" "credenciais" {
  filename = "${path.module}/credenciais.txt"
  content  = "usuario: ${random_pet.usuario.id}\nsenha: ${random_password.senha.result}"
}

output "usuario_gerado" {
  value = random_pet.usuario.id
}

# repare: não existe output da senha aqui de propósito —
# pra ver a senha, é preciso abrir credenciais.txt ou usar
# `terraform output -json` explicitamente. Bom gancho de aula
# sobre por que sensitive não é "criptografia", é só "não mostrar à toa"
