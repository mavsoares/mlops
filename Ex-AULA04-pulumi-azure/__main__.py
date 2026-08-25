# Aula 04 -- Exemplo PCDF (Pulumi), retomando o que faltou na Aula 03.
#
# NOVIDADE em relacao a Aula 03: o Resource Group agora e OPCIONALMENTE
# CRIADO pelo proprio Pulumi (nao so lido com .get()). Isso resolve dois
# problemas reais que apareceram na ultima aula:
#
#   1) Cada aluno usa uma conta Azure for Students DIFERENTE -- nao faz
#      sentido exigir que "rg-pcdf-demo" ja exista na conta de cada um.
#   2) A conta de estudante restringe as REGIOES permitidas por politica
#      (Azure Policy "Allowed locations"), e essa lista muda de aluno para
#      aluno -- "brazilsouth" pode nao estar liberado. Por isso a regiao
#      agora e um parametro de config, nao um valor fixo no codigo.
#
# Como o Pulumi decide entre CRIAR ou LER o grupo:
#   pulumi.Config() le dois valores, com fallback seguro:
#     criar_grupo  (bool)   -- default: true  (cria um grupo novo)
#     localizacao  (string) -- default: "eastus"
#
# Pre-requisitos:
#   az login
#   pulumi new azure-python   (dentro de uma pasta vazia, ex.: pulumi/)
#   pip install -r requirements.txt
#
# Como rodar (ambos os casos -- WSL2 Ubuntu OU Linux nativo -- usam os
# MESMOS comandos, porque os dois sao um shell Linux com Python):
#   pulumi config set criar_grupo true
#   pulumi config set localizacao eastus     # troque pela regiao liberada
#                                             # na SUA conta de estudante
#   pulumi up
#   # confira em portal.azure.com -> Resource Groups

import pulumi
from pulumi_azure_native import resources, storage

config = pulumi.Config()
criar_grupo = config.get_bool("criar_grupo")
if criar_grupo is None:
    criar_grupo = True
localizacao = config.get("localizacao") or "eastus"

NOME_GRUPO = "rg-pcdf-aula4"
NOME_CONTA = "rgpcdfgrupo7storagetemp"
NOME_CONTAINER = "bos-pulumi-demo"

if criar_grupo:
    # equivalente a: resource "azurerm_resource_group" "rg"
    # Agora o Pulumi POSSUI o grupo -- um "pulumi destroy" vai apaga-lo
    # junto com tudo que estiver dentro. Use este modo no SEU projeto
    # individual, na SUA conta de estudante.
    rg = resources.ResourceGroup(
        "rg",
        resource_group_name=NOME_GRUPO,
        location=localizacao,
    )
    rg_name = rg.name
    rg_location = rg.location
else:
    # equivalente a: data "azurerm_resource_group" "rg"
    # Modo usado na demo do PROFESSOR (Aula 02/03), onde o grupo
    # "rg-pcdf-demo" ja existe e nunca deve ser apagado pelo Pulumi.
    rg = resources.ResourceGroup.get("rg", NOME_GRUPO)
    rg_name = rg.name
    rg_location = rg.location

# equivalente a: resource "azurerm_storage_account" "st"
# account_name explicito -- sem isso, o Pulumi "autonomeia" o recurso
# fisico com um sufixo aleatorio (visto na Aula 03).
account = storage.StorageAccount(
    "stpcdfbopulumi",
    account_name=NOME_CONTA,
    resource_group_name=rg_name,
    location=rg_location,
    sku=storage.SkuArgs(name="Standard_LRS"),
    kind="StorageV2",
)

# equivalente a: resource "azurerm_storage_container" "raw"
container = storage.BlobContainer(
    "bos-pulumi-demo",
    container_name=NOME_CONTAINER,
    account_name=account.name,
    resource_group_name=rg_name,
)

pulumi.export("grupo_de_recursos", rg_name)
pulumi.export("regiao_usada", rg_location)
pulumi.export("conta_criada", account.name)
