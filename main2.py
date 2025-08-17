from dotenv import load_dotenv
import os
import pandas as pd
import google.generativeai as genai

def carregar_dados(caminho_arquivo):
    """Lê um arquivo Excel e retorna os dados como um DataFrame pandas."""
    try:
        df = pd.read_excel(caminho_arquivo)
        print("✔ Planilha carregada com sucesso!")
        return df
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None
    except Exception as e:
        print(f"ERRO: Ocorreu um problema ao ler a planilha: {e}")
        return None

def main():
    # --- 1. CONFIGURAÇÃO INICIAL (só precisa ser feita uma vez) ---
    load_dotenv()
    API_KEY = os.environ.get('CHAVE_API')
    if not API_KEY:
        print("ERRO: A variável de ambiente CHAVE_API não foi encontrada.")
        print("Verifique seu arquivo .env")
        return

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # --- 2. CARREGAR A PLANILHA ---
    caminho_planilha = r"C:\Users\Acer\Desktop\Espectros\planilha_tritoes.xlsx"
    dataframe = carregar_dados(caminho_planilha)

    if dataframe is None:
        return # Encerra o programa se a planilha não puder ser carregada

    # Converte todo o DataFrame para uma string para enviar à IA
    # Para planilhas muito grandes, você pode querer enviar apenas as primeiras linhas:
    # dados_string = dataframe.head(50).to_string()
    dados_string = dataframe.to_string()

    print("\n--- Analista de Dados pronto! Faça suas perguntas. Digite 'sair' para terminar. ---\n")

    # --- 3. LOOP INTERATIVO DE PERGUNTAS ---
    while True:
        pergunta_usuario = input("> Sua pergunta: ")

        if pergunta_usuario.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando o programa. Até mais!")
            break

        # --- 4. ENGENHARIA DE PROMPT: A parte mais importante! ---
        # Criamos um prompt bem estruturado para a IA entender o contexto.
        prompt_completo = f"""
        Você é um assistente especialista em análise de dados de futebol americano.
        Sua tarefa é analisar os dados da planilha fornecida e responder à pergunta do usuário de forma clara e objetiva. Por exemplo: "Qual a porcentagem de passes e corridas?" Você deve usar os dados da planilha para embasar sua resposta, achar as ocorrencia, gerar as estatisticas e retornar o resultado de forma concisa.
        **INSTRUÇÕES:**
        - Utilize os dados da planilha para embasar suas respostas.
        - Seja conciso e direto ao ponto.
        - Não inclua informações irrelevantes ou supérfluas.

        **NOMENCLATURA DAS COLUNAS**
        jogo = o jogo em questão da equipe. Se foi o 1, refere-se ao primeiro jogo da equipe no campeonato, 2 refere-se ao segundo jogo, e assim por diante.
        down = corresponde a descidas (1st down, 2nd down, etc.)
        dist = distancia que falta para o first down
        formacao =  corresponde à formação da jogada (ex: "I-formation", "Shotgun", strong i etc.)
        tipo_de_jogada = corresponde ao tipo de jogada (ex: "passe", "corrida", etc.)
        hash = corresponde ao hash da jogada (dir = direita, esq = esquerda e meio)
        rotas_direita = corresponde às rotas dos recebedores à direita da formação, em relação a defesa. As rotas foram cadastras do recebedor mais externo para o mais interno. Ex. curl/out/go, corresponde a rota do recebedor mais externo para o mais interno.
        rotas_esquerda = corresponde às rotas dos recebedores à esquerda da formação, em relação a defesa. As rotas foram cadastras do recebedor mais externo para o mais interno. Ex. curl/out/go, corresponde a rota do recebedor mais externo para o mais interno.
        resultado =  corresponde ao resultado da jogada (ex: "fd" = first down, "td" = touchdown, "1 jardas" = houve um avanço de 1 jarda positiva, "1 jardas negativa" = perda de 1 jarda na jogada, etc.)
        posicao_de_campo =  corresponde ao posicionamento de campo. A orientação se deu da seguinte forma: "10 D" =  corresponde à linha de 10 jardas do campo defensivo do ataque. Essa ordem vai ate "50 D". Após isso passa a ser um avanço de forma regressiva. Ex. 49 O, 48 O, 40 O, até 1 O. "O" corresponde a campo ofensivo.
        motion = corresponde a informação sobre o movimento dos jogadores antes da jogada. (ex: sim ou não)
        obs =  corresponde as observações relevantes sobre a jogada em questão.

        Analise a planilha com extremo cuidado e detalhes, para que as respostas sejam retornadas da melhor forma possível.
        ```
        {dados_string}
        ```

        **PERGUNTA DO USUÁRIO:**
        "{pergunta_usuario}"

        **SUA ANÁLISE:**
        """

        try:
            print("\nAnalisando os dados e gerando uma resposta...")
            
            response = model.generate_content(prompt_completo)
            
            resposta = response.text.strip()
            print("\n--- Resposta do Analista de IA ---\n")
            print(resposta)
            print("\n" + "-"*60 + "\n")

        except Exception as e:
            print(f"Ocorreu um erro ao chamar a API do Gemini: {e}")
            print("\n" + "-"*60 + "\n")


# Garante que o programa principal só rode quando o script for executado diretamente
if __name__ == "__main__":
    main()