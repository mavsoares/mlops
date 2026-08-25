# Exemplo 4 — Um container Docker de verdade, via Terraform
# Testa: provider docker (kreuzwerker), docker_image, docker_container
# Pré-requisito: Docker instalado e rodando na sua máquina.
# Depois do apply, abra http://localhost:8080

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_container" "site" {
  name  = "meu-site-local"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }
}

output "acesse_em" {
  value = "http://localhost:8080"
}
