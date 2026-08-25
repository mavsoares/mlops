terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

data "azurerm_resource_group" "rg" {
  name = "rg-pcdf-grupo-7"
}

resource "azurerm_storage_account" "st" {
  name                     = "rgpcdfgrupo7storage"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = data.azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "raw" {
  name                  = "bos-raw"
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = "private"
}
