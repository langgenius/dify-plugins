# Política de Privacidade do Plugin de Dados de Ações AKShare

**Última Atualização:** 2025-09-17

## 1. Introdução
Esta política de privacidade descreve como o Plugin de Dados de Ações AKShare ("Plugin", "nós", "nosso") processa informações quando você usa nosso plugin através da plataforma Dify para acessar dados financeiros. Esta política se aplica apenas ao plugin, não à plataforma Dify em si ou a qualquer fonte de dados terceirizada.

**Aviso Importante**: Este plugin é um wrapper da biblioteca Python [AKShare](https://github.com/akfamily/akshare). O acesso e processamento de dados são realizados através do AKShare, que se conecta a várias fontes de dados financeiros.

## 2. Dados que Processamos
O plugin atua como intermediário para ajudá-lo a usar a biblioteca Python AKShare para recuperar dados financeiros. Quando você usa o plugin, os seguintes tipos de dados podem ser processados na memória:

- **Parâmetros de entrada do usuário**: Como códigos de ações, intervalos de datas, tipos de indicadores técnicos ou outros parâmetros de consulta que você fornece.
- **Respostas da API**: Dados financeiros retornados pelo AKShare em resposta às suas consultas, incluindo mas não limitado a:
  - Dados de cotações de ações em tempo real
  - Dados de preços históricos
  - Dados de indicadores financeiros
  - Dados de fluxo de capital
  - Dados de análise técnica
  - Dados de visão geral do mercado
- **Logs temporários**: Logs técnicos que podem conter parâmetros de solicitação e status de resposta (usados para depuração e tratamento de erros)

O plugin **não** armazena permanentemente qualquer uma dessas informações. Todos os dados são processados apenas na memória durante a duração da sua solicitação e são limpos imediatamente após a conclusão da solicitação.

## 3. Como Usamos os Dados
Seus dados são usados apenas para:
- Passar seus parâmetros de consulta para a biblioteca AKShare para obter dados financeiros.
- Recuperar e retornar os dados financeiros solicitados através da plataforma Dify.

Não usamos seus dados para análise, análise ou publicidade.

## 4. Compartilhamento de Dados
**Não compartilhamos seus dados com terceiros**, incluindo:
- Provedores de serviços terceirizados
- Parceiros comerciais
- Agências governamentais (exceto quando legalmente obrigatório)
- Outras entidades para fins comerciais

## 5. Retenção de Dados
- **Dados de usuário**: Não retemos dados de usuários
- **Logs técnicos**: Logs podem ser mantidos temporariamente para depuração, mas são limpos regularmente
- **Dados de API**: Dados retornados pelas APIs são processados em tempo real e não são armazenados

## 6. Segurança
Implementamos medidas de segurança apropriadas para proteger suas informações:
- **Processamento local**: Dados são processados localmente quando possível
- **Conexões seguras**: Usamos conexões HTTPS para todas as comunicações
- **Acesso limitado**: Apenas pessoal autorizado tem acesso aos sistemas
- **Monitoramento**: Monitoramos sistemas para detectar atividades suspeitas

## 7. Seus Direitos
Dependendo da sua jurisdição, você pode ter os seguintes direitos:
- **Acesso**: Solicitar informações sobre dados que processamos
- **Retificação**: Corrigir dados imprecisos
- **Eliminação**: Solicitar a exclusão de seus dados
- **Portabilidade**: Solicitar uma cópia dos seus dados
- **Oposição**: Opor-se ao processamento de seus dados

## 8. Cookies e Tecnologias Similares
Este plugin não usa cookies ou tecnologias de rastreamento similares.

## 9. Transferências Internacionais
Seus dados podem ser processados em servidores localizados em diferentes países. Garantimos que tais transferências sejam realizadas de acordo com as leis de proteção de dados aplicáveis.

## 10. Menores de Idade
Este plugin não é destinado a menores de 16 anos. Não coletamos intencionalmente informações de menores de 16 anos.

## 11. Alterações nesta Política
Podemos atualizar esta política de privacidade periodicamente. Notificaremos sobre mudanças significativas através de:
- Atualizações na documentação do plugin
- Notificações na plataforma Dify
- Email (se aplicável)

## 12. Conformidade com Regulamentações
Esta política foi elaborada para estar em conformidade com:
- **GDPR** (Regulamento Geral sobre a Proteção de Dados da UE)
- **CCPA** (Lei de Privacidade do Consumidor da Califórnia)
- **LGPD** (Lei Geral de Proteção de Dados do Brasil)
- Outras leis de proteção de dados aplicáveis

## 13. Contato
Se você tiver perguntas sobre esta política de privacidade ou sobre como processamos seus dados, entre em contato conosco:

- **Email**: [privacy@exemplo.com]
- **GitHub**: [Link para o repositório do GitHub]
- **Issues**: [Link para issues do GitHub]

## 14. Fonte de Dados
Este plugin obtém dados de fontes públicas através do AKShare. Para informações sobre como essas fontes tratam dados, consulte suas respectivas políticas de privacidade:
- [AKShare Privacy Policy](https://github.com/akfamily/akshare)
- [East Money](https://www.eastmoney.com/)
- [Sina Finance](https://finance.sina.com.cn/)
- [Tonghuashun](https://www.10jqka.com.cn/)

---

**Esta política de privacidade é efetiva a partir de 2025-09-17 e foi atualizada pela última vez em 2025-09-18.**
