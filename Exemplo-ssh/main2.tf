# Exemplo 2 — Par de chaves SSH de verdade
# Testa: tls_private_key, local_file, file_permission
# Pré-requisito: nenhum.
# Depois do apply, teste com: ssh-keygen -lf id_rsa.pub

terraform {
  required_providers {
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

resource "tls_private_key" "chave" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "chave_privada" {
  content         = tls_private_key.chave.private_key_pem
  filename        = "${path.module}/id_rsa"
  file_permission = "0600" # SSH exige permissão restrita, senão recusa a chave
}

resource "local_file" "chave_publica" {
  content  = tls_private_key.chave.public_key_openssh
  filename = "${path.module}/id_rsa.pub"
}

output "fingerprint" {
  value = tls_private_key.chave.public_key_fingerprint_sha256
}
