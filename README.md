# Testar a performance do DNS

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://jp-linux.github.io)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

Um script Python avançado para testar o desempenho e confiabilidade de servidores DNS listados em um arquivo JSON. Realiza testes paralelos, gera relatórios detalhados e fornece análises estatísticas.

## Funcionalidades

- ✅ Teste de conectividade UDP/TCP em servidores DNS
- ⚡ Consultas paralelas com ThreadPoolExecutor
- 📊 Geração de relatórios em JSON com métricas detalhadas
- 🔍 Análise de falhas por categoria de servidores
- ⏱️ Medição de tempo de resposta com múltiplas tentativas
- 🌐 Suporte automático para IPv6 (com fallback quando não suportado)
- 🚀 Identificação dos servidores mais rápidos
- 🧩 Análise de erros com recomendações específicas

## Pré-requisitos

- Python 3.8+
- Biblioteca `dnspython`

```bash
pip install dnspython
```

## Como Usar

1. **Executar o teste**:
```bash
python teste_dns.py
```

2. **Resultados**:
   - Relatório completo: `relatorio_dns_avancado.json`
   - Saída detalhada no terminal

## Configurações (Editáveis no Código)

| Parâmetro          | Valor Padrão    | Descrição                              |
|--------------------|-----------------|----------------------------------------|
| `dominio_teste`    | `google.com`   | Domínio usado para testes              |
| `tipo_registro`    | `A`            | Tipo de registro DNS                  |
| `tempo_limite`     | `5` segundos   | Timeout por consulta                  |
| `tentativas`       | `2`            | Número de retentativas                |
| `max_workers`      | `50`           | Threads paralelas                     |
| `arquivo_saida`    | `relatorio...` | Nome do arquivo de saída              |

## Saída de Exemplo (Terminal)

```
⚙️ Configurações do Teste:
- Domínio: google.com
- Tipo de registro: A
- Timeout: 5s
- Retentativas: 2
- IPv6: Testando

⏳ Iniciando testes...
✅ Testado Google DNS (8.8.8.8) - Tentativas: 1 - ✅ Ativo
❌ Testado DNS Problemático (192.0.2.1) - Tentativas: 3 - ❌ Erro

📊 Relatório de Testes DNS - 2025-07-18T14:30:00.000000
Domínio testado: google.com (A)
Total de servidores: 15
Taxa de sucesso: 86.67%
Tempo médio de resposta: 42.35 ms

🔹 Públicos:
   Servidores: 5 | Sucesso: 5 (100.0%)

🚀 Top 5 mais rápidos:
1. Cloudflare (1.1.1.1): 12.45 ms
2. Google DNS (8.8.8.8): 18.72 ms

⚠️ Erros mais comuns:
- Falha de conexão: [Errno 61] Connection refused: 2 ocorrências

🔍 Análise Detalhada de Falhas por Categoria:
🔻 Privados: 2 falhas
   Erros mais comuns:
   - Falha de conexão: [Errno 61] Connection refused: 2 ocorrências

💡 Recomendações Específicas:
- Servidores com timeout: Considere aumentar o timeout ou verificar firewall
```

## Estrutura do Relatório JSON

```json
{
  "timestamp": "2025-07-18T14:30:00.000000",
  "dominio_teste": "google.com",
  "tipo_registro": "A",
  "total_servidores": 15,
  "taxa_sucesso": "86.67%",
  "tempos_resposta": {
    "minimo": "12.45 ms",
    "maximo": "120.80 ms",
    "media": "42.35 ms"
  },
  "categorias": {
    "Públicos": {"total": 5, "sucesso": 5}
  },
  "servidores_mais_rapidos": [...],
  "erros_comuns": [["Falha DNS: Timeout", 2]],
  "analise_falhas": {
    "Privados": {
      "falhas_totais": 2,
      "erros_comuns": {"Falha DNS: Timeout": 2},
      "servidores": [...]
    }
  },
  "servidores_falha": [...]
}
```

## Fluxo de Trabalho

1. Carrega servidores do arquivo JSON
2. Verifica suporte a IPv6 no sistema
3. Realiza testes de conectividade (UDP/TCP)
4. Executa consultas DNS com retentativas
5. Gera relatório com estatísticas
6. Salva resultados em JSON
7. Exibe análise detalhada no terminal

## Limitações Conhecidas
- Testes IPv6 dependem da configuração do sistema
- Tempo de teste proporcional ao número de servidores


## 👤 Autor

**Jorge Paulo Santos**  
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/JP-Linux)
[![Email](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:jorgepsan7@gmail.com)

## 💝 Suporte ao Projeto

Se este projeto foi útil para você, considere apoiar meu trabalho através do GitHub Sponsors:

[![Sponsor](https://img.shields.io/badge/Sponsor-JP_Linux-ea4aaa?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/JP-Linux)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
