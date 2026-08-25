resource "local_file" "Ola_Mundo" { 
  filename = "${path.module}/ola.txt"
  content  = "Olá, Mundo Terraform!"
}
