import dns.resolver
import time
import json
import socket
import concurrent.futures
from datetime import datetime
import sys


def verificar_suporte_ipv6():
    """Verifica se o sistema tem suporte a IPv6"""
    try:
        socket.socket(socket.AF_INET6, socket.SOCK_DGRAM).close()
        return True
    except:
        return False


def testar_servidor_dns(servidor, dominio_teste="google.com", tipo_registro="A", tempo_limite=5, tentativas=2):
    """Testa um servidor DNS com suporte a retentativas e fallback"""
    resolvedor = dns.resolver.Resolver(configure=False)
    resolvedor.nameservers = [servidor["ip"]]
    resolvedor.timeout = tempo_limite
    resolvedor.lifetime = tempo_limite

    resultado = {
        "servidor": servidor,
        "status": "❌ Erro",
        "tempo_resposta": None,
        "resposta": None,
        "erro": None,
        "sucesso": False,
        "tentativas": tentativas + 1
    }

    # Pular servidores IPv6 se o sistema não suportar
    if ":" in servidor["ip"] and not verificar_suporte_ipv6():
        resultado["erro"] = "IPv6 não suportado pelo sistema"
        return resultado

    # Teste de conectividade básica com fallback para UDP
    try:
        familia = socket.AF_INET6 if ":" in servidor["ip"] else socket.AF_INET

        # Tentativa com UDP (mais comum para DNS)
        try:
            with socket.socket(familia, socket.SOCK_DGRAM) as sock_udp:
                sock_udp.settimeout(tempo_limite)
                sock_udp.connect((servidor["ip"], 53))
        except:
            # Fallback para TCP se UDP falhar
            with socket.socket(familia, socket.SOCK_STREAM) as sock_tcp:
                sock_tcp.settimeout(tempo_limite)
                sock_tcp.connect((servidor["ip"], 53))

    except Exception as e:
        resultado["erro"] = f"Falha de conexão: {str(e)}"
        return resultado

    # Teste de consulta DNS com retentativas
    for tentativa_atual in range(tentativas + 1):
        try:
            inicio = time.perf_counter()
            resposta = resolvedor.resolve(dominio_teste, tipo_registro)
            tempo_resposta = (time.perf_counter() - inicio) * 1000

            resultado["status"] = "✅ Ativo"
            resultado["tempo_resposta"] = tempo_resposta
            resultado["resposta"] = [str(r) for r in resposta]
            resultado["sucesso"] = True
            resultado["tentativas"] = tentativa_atual + 1
            break

        except dns.exception.DNSException as e:
            tipo_erro = type(e).__name__
            if tentativa_atual == tentativas:
                resultado["erro"] = f"Falha DNS: {tipo_erro}"
        except Exception as e:
            if tentativa_atual == tentativas:
                resultado["erro"] = f"Erro geral: {str(e)}"

    return resultado


def gerar_relatorio(resultados, dominio_teste, tipo_registro):
    """Gera relatório com análise de falhas e estatísticas avançadas"""
    sucedidos = [r for r in resultados if r['sucesso']]
    falhas = [r for r in resultados if not r['sucesso']]

    # Estatísticas básicas
    total_servidores = len(resultados)
    taxa_sucesso = (len(sucedidos) / total_servidores *
                    100) if total_servidores > 0 else 0

    # Tempos de resposta
    tempos_resposta = [r["tempo_resposta"]
                       for r in sucedidos if r["tempo_resposta"] is not None]
    media_tempo = sum(tempos_resposta) / \
        len(tempos_resposta) if tempos_resposta else 0
    min_tempo = min(tempos_resposta) if tempos_resposta else 0
    max_tempo = max(tempos_resposta) if tempos_resposta else 0

    # Relatório por categoria
    categorias = {}
    for resultado in resultados:
        categoria = resultado['servidor']['categoria']
        if categoria not in categorias:
            categorias[categoria] = {'total': 0, 'sucesso': 0}
        categorias[categoria]['total'] += 1
        if resultado['sucesso']:
            categorias[categoria]['sucesso'] += 1

    # Top 5 mais rápidos
    mais_rapidos = sorted(sucedidos, key=lambda x: x["tempo_resposta"])[
        :5] if sucedidos else []

    # Falhas mais comuns
    contagem_erros = {}
    for resultado in falhas:
        erro = resultado.get('erro', 'Erro desconhecido')
        contagem_erros[erro] = contagem_erros.get(erro, 0) + 1
    erros_comuns = sorted(contagem_erros.items(),
                          key=lambda x: x[1], reverse=True)[:3]

    # Adicionar análise de falhas por categoria
    analise_falhas = {}
    for categoria in categorias.keys():
        servidores_categoria = [r for r in resultados if r['servidor']
                                ['categoria'] == categoria and not r['sucesso']]
        if servidores_categoria:
            analise_falhas[categoria] = {
                "falhas_totais": len(servidores_categoria),
                "erros_comuns": {},
                "servidores": []
            }
            for servidor in servidores_categoria:
                analise_falhas[categoria]["servidores"].append({
                    "nome": servidor["servidor"]["nome"],
                    "ip": servidor["servidor"]["ip"],
                    "erro": servidor.get("erro", "Erro desconhecido")
                })
                erro = servidor.get("erro", "Erro desconhecido")
                analise_falhas[categoria]["erros_comuns"][erro] = \
                    analise_falhas[categoria]["erros_comuns"].get(
                        erro, 0) + 1

    return {
        "timestamp": datetime.now().isoformat(),
        "dominio_teste": dominio_teste,
        "tipo_registro": tipo_registro,
        "total_servidores": total_servidores,
        "taxa_sucesso": f"{taxa_sucesso:.2f}%",
        "tempos_resposta": {
            "minimo": f"{min_tempo:.2f} ms",
            "maximo": f"{max_tempo:.2f} ms",
            "media": f"{media_tempo:.2f} ms"
        },
        "categorias": categorias,
        "servidores_mais_rapidos": [
            {"nome": r["servidor"]["nome"], "ip": r["servidor"]["ip"],
             "tempo": f"{r['tempo_resposta']:.2f} ms"} for r in mais_rapidos
        ],
        "erros_comuns": erros_comuns,
        "analise_falhas": analise_falhas,
        "servidores_falha": [
            {"nome": r["servidor"]["nome"], "ip": r["servidor"]["ip"],
             "erro": r.get('erro', 'Erro desconhecido')} for r in falhas
        ]
    }


def main():
    # Carrega os servidores do JSON
    try:
        with open('servidores_dns.json') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print("Erro: Arquivo 'servidores_dns.json' não encontrado!")
        sys.exit(1)

    # Coleta todos os servidores
    todos_servidores = []
    for categoria in dados['servidores_dns']:
        for servidor in categoria['servidores']:
            servidor['categoria'] = categoria['categoria']
            todos_servidores.append(servidor)

    # Configurações avançadas
    config = {
        "dominio_teste": "google.com",
        "tipo_registro": "A",
        "tempo_limite": 5,  # Aumentado para 5 segundos
        "tentativas": 2,   # 2 retentativas
        "max_workers": 50,
        "arquivo_saida": "relatorio_dns_avancado.json",
        "pular_ipv6": not verificar_suporte_ipv6()  # Pular IPv6 se não suportado
    }

    # Exibir configurações
    print("\n⚙️ Configurações do Teste:")
    print(f"- Domínio: {config['dominio_teste']}")
    print(f"- Tipo de registro: {config['tipo_registro']}")
    print(f"- Timeout: {config['tempo_limite']}s")
    print(f"- Retentativas: {config['tentativas']}")
    print(
        f"- IPv6: {'Testando' if not config['pular_ipv6'] else 'Pulando (sem suporte)'}")

    # Filtrar servidores IPv6 se necessário
    if config['pular_ipv6']:
        total_original = len(todos_servidores)
        todos_servidores = [s for s in todos_servidores if ":" not in s["ip"]]
        removidos = total_original - len(todos_servidores)
        print(
            f"- Servidores IPv6 removidos: {removidos}. Restantes: {len(todos_servidores)}")

    # Testa em paralelo
    resultados = []
    print("\n⏳ Iniciando testes...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        futures = {executor.submit(
            testar_servidor_dns,
            servidor,
            config['dominio_teste'],
            config['tipo_registro'],
            config['tempo_limite'],
            config['tentativas']
        ): servidor for servidor in todos_servidores}

        for future in concurrent.futures.as_completed(futures):
            resultado = future.result()
            resultados.append(resultado)
            # Exibir progresso
            status = "✅" if resultado['sucesso'] else "❌"
            print(f"{status} Testado {resultado['servidor']['nome']} ({resultado['servidor']['ip']}) - "
                  f"Tentativas: {resultado['tentativas']} - "
                  f"{resultado['status']}")

    # Gera relatório
    relatorio = gerar_relatorio(
        resultados, config['dominio_teste'], config['tipo_registro'])

    # Salva relatório completo
    with open(config['arquivo_saida'], 'w') as f:
        json.dump(relatorio, f, indent=2)

    # Exibe resumo
    print(f"\n📊 Relatório de Testes DNS - {relatorio['timestamp']}")
    print(
        f"Domínio testado: {relatorio['dominio_teste']} ({relatorio['tipo_registro']})")
    print(f"Total de servidores: {relatorio['total_servidores']}")
    print(f"Taxa de sucesso: {relatorio['taxa_sucesso']}")
    print(f"Tempo médio de resposta: {relatorio['tempos_resposta']['media']}")

    # Exibe resultados por categoria
    for categoria, estatisticas in relatorio['categorias'].items():
        taxa_sucesso = (estatisticas['sucesso'] / estatisticas['total']) * 100
        print(f"\n🔹 {categoria}:")
        print(
            f"   Servidores: {estatisticas['total']} | Sucesso: {estatisticas['sucesso']} ({taxa_sucesso:.1f}%)")

    # Top 5 mais rápidos
    if relatorio.get('servidores_mais_rapidos'):
        print("\n🚀 Top 5 mais rápidos:")
        for i, servidor in enumerate(relatorio['servidores_mais_rapidos'], 1):
            print(
                f"{i}. {servidor['nome']} ({servidor['ip']}): {servidor['tempo']}")
    else:
        print("\n⚠️ Nenhum servidor teve sucesso para calcular o top 5")

    # Erros mais comuns
    if relatorio.get('erros_comuns'):
        print("\n⚠️ Erros mais comuns:")
        for erro, quantidade in relatorio['erros_comuns']:
            print(f"- {erro}: {quantidade} ocorrências")

    # Análise de falhas detalhada
    if relatorio.get('analise_falhas'):
        print("\n🔍 Análise Detalhada de Falhas por Categoria:")
        for categoria, analise in relatorio['analise_falhas'].items():
            print(f"\n🔻 {categoria}: {analise['falhas_totais']} falhas")
            if analise.get('erros_comuns'):
                print("   Erros mais comuns:")
                for erro, quantidade in analise['erros_comuns'].items():
                    print(f"   - {erro}: {quantidade} ocorrências")

            if analise.get('servidores'):
                print("\n   Servidores com problemas:")
                for servidor in analise['servidores']:
                    print(
                        f"   - {servidor['nome']} ({servidor['ip']}): {servidor['erro']}")

    # Recomendações baseadas em falhas
    if relatorio.get('erros_comuns') or relatorio.get('analise_falhas'):
        print("\n💡 Recomendações Específicas:")
        if any("LifetimeTimeout" in e for e, _ in relatorio.get('erros_comuns', [])):
            print(
                "- Servidores com timeout: Considere aumentar o timeout ou verificar firewall")

        if any("NoNameservers" in e for e, _ in relatorio.get('erros_comuns', [])):
            print(
                "- Servidores com 'NoNameservers': Podem estar bloqueando consultas ou mal configurados")

        if any("IPv6" in e for e, _ in relatorio.get('erros_comuns', [])):
            print(
                "- Problemas IPv6: Configure suporte a IPv6 ou remova servidores IPv6 dos testes")

        if relatorio['taxa_sucesso'] != "100.00%":
            print("- Considere testar com diferentes domínios e tipos de registro")
            print("- Verifique se alguns servidores exigem configuração especial")
    else:
        print("\n🎉 Todos os servidores responderam com sucesso!")


if __name__ == "__main__":
    main()
