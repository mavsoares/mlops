#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aula 06 -- Kubeflow Pipelines (KFP SDK) -- pipeline de exemplo com 2
componentes, no MESMO espirito do DAG do Airflow (extract -> clean),
so que aqui cada etapa vira um COMPONENTE.

Testado com: kfp==2.17.0 (SDK oficial, pip install kfp)

Uso (dentro da pasta Kubeflow-Demo/, ver Passo A1-1 do Manual):
    pip install kfp pandas
    python3 pipeline_kfp_exemplo.py

O script faz DUAS coisas, em sequencia:
    1) RODA o pipeline de verdade, localmente, via kfp.local
       (SubprocessRunner, sem Docker e sem cluster Kubernetes) -- os
       componentes executam de verdade, com o MESMO codigo Python que
       rodaria dentro de um Pod num cluster real, e o resultado de cada
       etapa e impresso no console.

       IMPORTANTE: usamos SubprocessRunner(use_venv=False) -- o kfp
       instala os packages_to_install (ex.: pandas) direto no Python
       atual, sem criar venv por componente. Em Python gerenciado pelo
       sistema (Debian/Ubuntu/WSL2), isso bateria no erro
       "externally-managed-environment" (PEP 668) -- por isso o script
       ja seta PIP_BREAK_SYSTEM_PACKAGES=1 automaticamente logo abaixo,
       antes de importar o kfp. Essa e a mesma flag que usamos em todo
       "pip install ... --break-system-packages" da aula, so que via
       variavel de ambiente (e o pip respeita as duas formas
       igualmente). Vantagem sobre criar um venv por componente:
       nao depende do pacote python3-venv/ensurepip do sistema (que
       pode nao existir para builds mais novos/customizados de Python,
       como aconteceu em Python 3.14 instalado fora do apt padrao), e
       roda em ~5s em vez de ~20-30s.
    2) COMPILA o pipeline em pipeline_bos_pcdf.yaml -- o "IR YAML"
       (Intermediate Representation): a especificacao completa dos
       componentes e das dependencias entre eles, pronta para ser
       submetida a um cluster Kubeflow de verdade (Argo Workflow). E o
       BACKEND do Kubeflow (quando o YAML e submetido a um cluster) que
       traduz esse IR YAML para Argo Workflow e sobe um Pod por
       componente -- rodar localmente com kfp.local pula essa etapa de
       infraestrutura, mas executa exatamente a mesma logica.
"""
import io
import os

# precisa vir ANTES de importar kfp: garante que qualquer "pip install"
# disparado internamente pelo kfp.local (SubprocessRunner use_venv=False)
# funcione mesmo em Python gerenciado pelo sistema (Debian/Ubuntu/WSL2,
# erro "externally-managed-environment" / PEP 668) -- equivalente a
# sempre rodar "pip install ... --break-system-packages".
os.environ.setdefault("PIP_BREAK_SYSTEM_PACKAGES", "1")

from kfp import dsl
from kfp import compiler
from kfp import local


@dsl.component(base_image="python:3.11", packages_to_install=["pandas"])
def extrair_relatos(quantidade: int) -> str:
    """Componente 1 -- gera um mini-dataset ficticio de relatos (E de
    ETL) e devolve como uma string JSON -- a "saida tipada" que o
    proximo componente vai receber como entrada."""
    import pandas as pd

    dados = [
        {"id": i, "texto_relato": f"  RELATO {i}  "}
        for i in range(1, quantidade + 1)
    ]
    df = pd.DataFrame(dados)
    return df.to_json()


@dsl.component(base_image="python:3.11", packages_to_install=["pandas"])
def limpar_relatos(relatos_json: str) -> str:
    """Componente 2 -- recebe a saida do componente 1 como entrada
    tipada (mesma ideia do XCom no Airflow, mas aqui e uma conexao
    explicita entre componentes, definida no pipeline abaixo)."""
    import io
    import pandas as pd

    df = pd.read_json(io.StringIO(relatos_json))
    df["texto_relato"] = df["texto_relato"].str.lower().str.strip()
    print(df.head().to_string())
    return df.to_json()


@dsl.pipeline(
    name="pipeline-bos-pcdf",
    description="Exemplo didatico: extract -> clean, 2 componentes KFP (Aula 06, projeto-guia PCDF).",
)
def pipeline_bos_pcdf(quantidade: int = 5) -> str:
    tarefa_extrair = extrair_relatos(quantidade=quantidade)
    tarefa_limpar = limpar_relatos(relatos_json=tarefa_extrair.output)
    # a linha acima E a conexao entre os dois componentes -- o
    # compilador usa essa dependencia de dados para decidir a ordem de
    # execucao dos Pods, sem precisarmos escrever um ">>" como no Airflow
    return tarefa_limpar.output


if __name__ == "__main__":
    print("=== 1) Rodando o pipeline de verdade, localmente (sem cluster) ===\n")
    local.init(runner=local.SubprocessRunner(use_venv=False))
    pipeline_task = pipeline_bos_pcdf(quantidade=5)
    print("\nSaida final do pipeline (componente limpar_relatos):")
    print(pipeline_task.output)

    print("\n=== 2) Compilando o pipeline em pipeline_bos_pcdf.yaml ===\n")
    compiler.Compiler().compile(
        pipeline_func=pipeline_bos_pcdf,
        package_path="pipeline_bos_pcdf.yaml",
    )
    print("ok: pipeline_bos_pcdf.yaml gerado -- abra o arquivo e procure por 'components:' e 'deploymentSpec:'")
