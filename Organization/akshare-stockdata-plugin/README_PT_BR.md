# Plugin de Dados de Ações AKShare para Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

## 📞 Informações de Contato

- **Autor**: shaoxing-xie
- **Email**: sxxiefg@163.com
- **Repositório**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **Relatórios de Problemas**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 Visão Geral

**Plugin de Dados de Ações AKShare** é uma ferramenta abrangente de dados de ações desenvolvida especificamente para a plataforma Dify, construída na renomada biblioteca Python [AKShare](https://github.com/akfamily/akshare). Este plugin oferece aos usuários uma solução de acesso a dados do mercado de ações em um só lugar, cobrindo múltiplas dimensões de informações profissionais sobre ações, incluindo cotações em tempo real, dados históricos, análise financeira, fluxo de capital, análise técnica e Shanghai-Shenzhen-Hong Kong Stock Connect.

> **Aviso Importante**: Este plugin é uma ferramenta de integração da plataforma Dify baseada na biblioteca AKShare. AKShare é uma biblioteca de interface de dados financeiros de código aberto projetada para fins de pesquisa acadêmica. Expressamos nossa sincera gratidão à equipe do projeto AKShare por seu excelente trabalho.

## 🚀 Características Principais

### 💎 **Sem Necessidade de Chave API**
- ✅ **Uso Zero Configuração**: Não é necessário solicitar chaves API ou tokens
- ✅ **Plug and Play**: Pronto para uso imediatamente após a instalação, sem configuração complexa
- ✅ **Economia de Custos**: Completamente gratuito para usar, sem limites de uso

### 🌐 **Fontes de Dados Autoritativas**
- 📊 **Eastmoney**: Cotações em tempo real, dados financeiros, análise de mercado
- 📈 **Sina Finance**: Cotações históricas, notícias de ações
- 🏢 **Tonghuashun**: Indicadores técnicos, análise de fluxo de capital
- 💰 **Tencent Finance**: Dados de ações de Hong Kong e EUA
- 📱 **NetEase Finance**: Visão geral do mercado, informações de ações individuais
- 🔗 **APIs Públicas**: Interfaces de dados oficiais das bolsas de valores

### 🛠️ **Matriz de Funcionalidades Poderosas**
- 🎯 **8 Ferramentas Profissionais**: Cobrindo todos os aspectos da análise de dados de ações
- 🌍 **113 Interfaces de Dados**: Cobertura ampla dos principais mercados de ações globais
- 📊 **Suporte Multi-Mercado**: A-shares, B-shares, Hong Kong, EUA, STAR Market, BSE
- 🔄 **Tempo Real + Histórico**: Tanto cotações em tempo real quanto análise de dados históricos
- 📋 **Saída Dupla**: Tabelas Markdown + formato JSON, fácil de ler e processar

### 🔧 **Vantagens Técnicas**
- 🛡️ **Tratamento Inteligente de Erros**: Mecanismo de retry automático, recuperação elegante de erros
- 🌐 **Suporte Completo Unicode**: Processamento perfeito de caracteres chineses e símbolos especiais
- ⚡ **Otimização de Performance**: Isolamento de subprocesso, gerenciamento eficiente de memória
- 🔄 **Validação de Parâmetros**: Validação automática de parâmetros e conversão de formato

## 👥 Público-Alvo

### 🎓 **Pesquisadores Acadêmicos**
- Pesquisadores de finanças realizando análise de mercado e pesquisa acadêmica
- Acadêmicos de economia estudando padrões de volatilidade do mercado de ações
- Pesquisadores de ciência de dados realizando análise quantitativa

### 🤖 **Desenvolvedores de Aplicações de IA**
- Construindo assistentes de investimento inteligentes e chatbots financeiros
- Desenvolvendo sistemas de recomendação de ações baseados em IA
- Criando ferramentas de análise de dados financeiros automatizadas

### 💼 **Profissionais Financeiros**
- Analistas financeiros precisando de acesso rápido a dados de mercado
- Gestores de portfólio monitorando posições de ações
- Consultores de investimento fornecendo insights baseados em dados

## 📊 Ferramentas Disponíveis

### 1. 📈 **Resumo do Mercado de Ações** (`stock_market_summary`)
- **13 interfaces** cobrindo dados de mercado de A-shares
- Inclui: Resumo de dados de ações SSE, estatísticas de categorias de títulos SZSE, dados diários de negociação
- **Interfaces principais**: `stock_sse_summary`, `stock_szse_summary`, `stock_sse_deal_daily`

### 2. 🏢 **Resumo de Informações de Ações Individuais** (`stock_individual_info_summary`)
- **15 interfaces** para informações detalhadas de empresas
- Inclui: Informações básicas de empresas, dados de IPO, informações de dividendos
- **Interfaces principais**: `stock_individual_info_em`, `stock_ipo_info`, `stock_dividend_detail`

### 3. 📊 **Cotações em Tempo Real** (`stock_spot_quotations`)
- **20 interfaces** para dados de mercado em tempo real
- Inclui: Cotações A-shares, B-shares, Hong Kong, EUA, STAR Market
- **Interfaces principais**: `stock_zh_a_spot_em`, `stock_hk_spot_em`, `stock_us_spot_em`

### 4. 📈 **Cotações Históricas** (`stock_hist_quotations`)
- **15 interfaces** para dados históricos de preços
- Inclui: Dados diários, semanais, mensais, dados de minuto
- **Interfaces principais**: `stock_zh_a_hist`, `stock_hk_hist`, `stock_us_hist`

### 5. 🔗 **Participações Shanghai-Shenzhen-Hong Kong** (`stock_hsgt_holdings`)
- **12 interfaces** para dados de Stock Connect
- Inclui: Fluxo de capital, participações, dados de ranking
- **Interfaces principais**: `stock_hsgt_fund_flow_summary`, `stock_hsgt_hold_stock_em`

### 6. 💰 **Análise de Fluxo de Capital** (`stock_fund_flow_analysis`)
- **18 interfaces** para análise de fluxo de capital
- Inclui: Fluxo de capital por setor, fluxo de capital individual, dados de ranking
- **Interfaces principais**: `stock_sector_fund_flow_rank`, `stock_individual_fund_flow_rank`

### 7. 📊 **Análise Financeira** (`stock_financial_analysis`)
- **20 interfaces** para análise financeira
- Inclui: Demonstrações financeiras, indicadores financeiros, análise de dívida
- **Interfaces principais**: `stock_financial_abstract`, `stock_balance_sheet_by_report_em`

### 8. 📈 **Análise Técnica** (`stock_technical_analysis`)
- **12 interfaces** para indicadores técnicos
- Inclui: Médias móveis, RSI, MACD, Bollinger Bands
- **Interfaces principais**: `stock_zh_a_hist_min_em`, `stock_zh_a_hist_pre_min_em`

## 🚀 Instalação e Uso

### Pré-requisitos
- Dify Platform 1.0+
- Python 3.12+
- Conexão com internet

### Instalação

#### Método 1: Marketplace da Dify (Recomendado)
1. Abra seu workspace da Dify
2. Navegue para **Ferramentas** → **Navegar Marketplace**
3. Procure por **"AKShare Stock Data"** ou **"AKShare 股票数据"**
4. Clique no botão **Instalar**
5. Aguarde a instalação ser concluída e comece a usar

#### Método 2: Instalação via GitHub
1. Visite o repositório do plugin: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
2. Baixe o pacote do plugin da versão mais recente (arquivo .difypkg)
3. Em seu workspace da Dify:
   - Navegue para **Ferramentas** → **Plugins Locais**
   - Clique em **Carregar Plugin**
   - Selecione o arquivo .difypkg baixado
   - Confirme a instalação

#### Método 3: Instalação Manual
1. Clone este repositório localmente
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. Instale as dependências Python
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. Empacote o plugin usando Dify CLI
   ```bash
   dify plugin package
   ```
4. Carregue o arquivo .difypkg gerado na Dify

### Uso Básico
```python
# Exemplo de uso em workflow da Dify
{
  "interface": "stock_sse_summary",
  "retries": 5,
  "timeout": 300
}
```

## 📋 Parâmetros Comuns

### Parâmetros de Rede
- **retries**: Número de tentativas (1-10, padrão: 5)
- **timeout**: Tempo limite do subprocesso em segundos (5-3600, padrão: 240)

### Parâmetros de Data
- **date**: Data de negociação no formato YYYYMMDD (ex: 20240101)
- **symbol**: Código da ação (ex: 000001, 600000)

### Parâmetros de Mercado
- **market**: Mercado específico (A, B, Hong Kong, EUA)
- **period**: Período de dados (daily, weekly, monthly)

## 🔧 Configuração Avançada

### Timeout por Tipo de Interface
- **Interfaces de Mercado em Tempo Real**: 15 minutos
- **Interfaces de Dados Financeiros**: 10 minutos
- **Interfaces de Dados Históricos**: 5 minutos
- **Interfaces Básicas**: 2 minutos

### Tratamento de Erros
- Retry automático com backoff exponencial
- Validação de parâmetros automática
- Recuperação elegante de erros de rede
- Logs detalhados para debugging

## 📊 Exemplos de Saída

### Formato Markdown
```markdown
| 项目 | 股票 | 主板 | 科创板 |
|------|------|------|--------|
| 流通股本 | 47466.3 | 45587.82 | 1878.47 |
| 总市值 | 615583.81 | 519873.03 | 95710.77 |
```

### Formato JSON
```json
{
  "data": [
    {
      "项目": "流通股本",
      "股票": "47466.3",
      "主板": "45587.82",
      "科创板": "1878.47"
    }
  ],
  "columns": ["项目", "股票", "主板", "科创板"],
  "shape": [8, 4]
}
```

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia nosso guia de contribuição antes de enviar pull requests.

### Como Contribuir
1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [AKShare](https://github.com/akfamily/akshare) - Biblioteca Python para dados financeiros
- [Dify](https://dify.ai/) - Plataforma de desenvolvimento de aplicações de IA
- Todos os contribuidores e usuários do projeto

## 📞 Suporte

## 🎯 Demonstração e Exemplos

### 📋 **Demonstração de Workflow Dify**

Fornecemos dois arquivos de demonstração de workflow Dify completos que mostram como usar vários recursos do Plugin de Dados de Ações AKShare:

#### 🔧 **Arquivo de Demonstração 1: Demonstração de Funcionalidade do Plugin**
**Arquivo**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**Descrição**: Demonstra o uso de todas as ferramentas do plugin e suas interfaces, mostrando a funcionalidade completa de 8 ferramentas profissionais

**Conteúdo da Demonstração**:
- **Resumo do Mercado de Ações** - Aquisição de dados de visão geral do mercado
- **Resumo de Informações de Ações Individuais** - Consultas de informações detalhadas de ações individuais
- **Cotações de Ações em Tempo Real** - Aquisição de dados de preços em tempo real
- **Cotações Históricas de Ações** - Análise de dados de preços históricos
- **Participações Shanghai-Shenzhen-Hong Kong Stock Connect** - Participações de capital norte
- **Análise de Fluxo de Capital** - Análise de dados de fluxo de capital
- **Análise de Dados Financeiros de Ações** - Aquisição de dados de demonstrações financeiras
- **Análise Técnica de Ações** - Cálculos de indicadores técnicos

**Recursos da Demonstração**:
- **Ramificação Condicional Inteligente** - Seleciona automaticamente interfaces de dados apropriadas com base na entrada do usuário
- **Conversão de Formato de Dados** - Converte automaticamente tabelas Markdown para arquivos Excel
- **Exibição Multi-dimensional** - Cobre cenários de uso para todas as 8 ferramentas profissionais
- **Workflow Completo** - Processo completo da aquisição de dados à exibição de resultados

#### 🤖 **Arquivo de Demonstração 2: Aplicação de Análise Profunda de Ações Individuais**
**Arquivo**: `应用示例/个股行情分析-ChatFlow.yml`

**Descrição**: Aplicação ChatFlow de análise profunda de ações individuais baseada no Plugin de Dados de Ações AKShare, fornecendo análise multi-dimensional de ações

**Recursos Principais**:
- **Reconhecimento Inteligente de Ações** - Identifica automaticamente códigos de ações e tipos de mercado (A-shares de Xangai, A-shares de Shenzhen, Bolsa de Valores de Pequim)
- **Análise de Cotações Históricas** - Análise técnica baseada em dados históricos de um ano
- **Análise de Indicadores Financeiros** - Análise fundamental baseada em dados financeiros
- **Análise de Fluxo de Fundos** - Análise de fluxo de fundos baseada em dados de fluxo de capital
- **Relatórios de Pesquisa de Ações Individuais** - Acesso aos relatórios de pesquisa mais recentes de ações individuais
- **Recomendações de Investimento Abrangentes** - Recomendações de investimento baseadas em dados multi-dimensionais

**Recursos Técnicos**:
- **Cálculo Dinâmico de Datas** - Calcula automaticamente o intervalo de tempo mais recente dos dados históricos
- **Validação do Mercado A-shares** - Identifica e valida inteligentemente códigos de ações A-shares
- **Integração de Múltiplas Fontes de Dados** - Integra cotações históricas, dados financeiros, fluxo de fundos, relatórios de pesquisa e outros dados multi-dimensionais
- **Relatórios de Análise Profissional** - Gera relatórios de análise abrangentes incluindo aspectos técnicos, fundamentais e de fluxo de fundos

#### 🔧 **Como Usar a Demonstração**
1. Importe o arquivo de demonstração correspondente na plataforma Dify
2. Certifique-se de que o Plugin de Dados de Ações AKShare está instalado
3. Execute o workflow para experimentar vários recursos de dados de ações
4. Modifique e personalize o workflow conforme necessário

Para suporte e perguntas:
- Abra uma issue no GitHub
- Consulte a documentação oficial
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ para a comunidade de dados financeiros**
