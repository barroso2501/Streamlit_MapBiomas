# 🌿 MapBiomas Observer

Dashboard interativo para análise temporal de cultivos e dinâmica de uso do solo nos biomas **Cerrado**, **Amazônia** e **Mata Atlântica** — MapBiomas Coleção 10.

---

## O que o dashboard oferece

| Aba | Conteúdo |
|-----|----------|
| 📈 Cobertura Temporal | Séries temporais (1985–2024) de soja, cana, arroz, algodão e outros cultivos temporários por bioma, estado ou classe |
| 🔀 Transições (Sankey) | Diagrama de fluxo mostrando de onde vem e para onde vai cada classe nos períodos pré-calculados |
| 📋 Dados Brutos | Tabela consultável com exportação CSV para cobertura e transições |

---

## Como publicar (passo a passo)

### 1. Criar o repositório no GitHub

1. Acesse [github.com](https://github.com) e crie uma conta gratuita (se ainda não tiver)
2. Clique em **New repository**
3. Dê um nome (ex: `mapbiomas-observer`), marque **Private** se quiser restringir acesso
4. Clique em **Create repository**

### 2. Fazer upload dos arquivos

No repositório criado, clique em **Add file → Upload files** e suba:

```
mapbiomas-observer/
├── app.py
├── requirements.txt
└── MapBiomas_101_Cerrado_AmAzonia_MAtlantica.xlsx
```

> **Atenção:** O arquivo `.xlsx` deve estar na **mesma pasta** que o `app.py`.

### 3. Publicar no Streamlit Community Cloud (gratuito)

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta GitHub
3. Clique em **New app**
4. Selecione:
   - **Repository:** seu repositório (`seu-usuario/mapbiomas-observer`)
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clique em **Deploy**

O Streamlit vai instalar as dependências automaticamente e em ~2 minutos o app estará disponível em uma URL pública como:

```
https://seu-usuario-mapbiomas-observer-app-xxxx.streamlit.app
```

### 4. Compartilhar com os especialistas

Copie a URL gerada e envie para o grupo. Qualquer pessoa com o link pode acessar — sem precisar instalar nada.

> Para restringir o acesso a pessoas específicas, use o recurso **Sharing** do Streamlit Cloud (disponível no painel do app).

---

## Como atualizar os dados

Quando houver uma nova versão do arquivo `.xlsx`:

1. No GitHub, vá até o arquivo `.xlsx` no repositório
2. Clique em **...** → **Replace file**
3. Faça upload do novo arquivo com o **mesmo nome**
4. O Streamlit detecta a mudança e reinicia o app automaticamente

---

## Dependências

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
openpyxl>=3.1.0
```

---

## Dados

**MapBiomas Brasil — Coleção 10**  
Biomas: Cerrado, Amazônia, Mata Atlântica  
Período: 1985–2024  
Fonte: [mapbiomas.org](https://mapbiomas.org)
