from flask import Flask, request, jsonify
import json
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['POST'])  # Rota e método
def tasks():
    try:
        event = request.get_json()
        print("JSON recebido:", event)

        user_data = event['users']
        
        # Inicializar listas para cada coluna da matriz
        ids = []
        disp = []
        ct = []
        php = []
        office = []
        java = []
        javascript = []
        python = []
        ruby = []
        assembly = []
        sql = []
        git = []
        linux = []

        # Preencher listas com os dados do JSON
        for user_id, user_info in user_data.items():
            ids.append(user_info["id"])
            disp.append(int(user_info["disp"]))
            ct.append(int(user_info["ct"]))
            skills = user_info["skill"][0]  # Acessar a lista de habilidades diretamente
            php.append(int(skills["php"]))
            office.append(int(skills["office"]))
            java.append(int(skills["java"]))
            javascript.append(int(skills["javascript"]))
            python.append(int(skills["python"]))
            ruby.append(int(skills["ruby"]))
            assembly.append(int(skills["assembly"]))
            sql.append(int(skills["sql"]))
            git.append(int(skills["git"]))
            linux.append(int(skills["linux"]))

        # Criar a matriz usando NumPy
        matrix = np.array([range(0, len(ids)), disp, ct, php, office, java, javascript, python, ruby, assembly, sql, git, linux]).T
        
        # Dicionário mapeando habilidades para índices
        index = {
            'php': 3,
            'office': 4,
            'java': 5,
            'javascript': 6,
            'python': 7,
            'ruby': 8,
            'assembly': 9,
            'sql': 10,
            'git': 11,
            'linux': 12
        }
        
        # Acessar as habilidades requeridas dentro do arquivo JSON
        task_json = list(event['tarefa'])
        
        # Resgatar os índices correspondentes às habilidades requeridas
        skills_index = [index[skill] for skill in task_json]
        
        # Nova matriz apenas com as habilidades requeridas
        users_skills = matrix[:, skills_index]
        
        # Adicionar as três primeiras colunas de volta à nova matriz
        users_skills = np.concatenate((matrix[:, :3], users_skills), axis=1)
        
        # Contar quantas linhas têm pelo menos um valor 0 (com exceção três primeiras, que representam o index, a disp e a carga de trabalho)
        lines_with_zeros = np.sum(np.any(users_skills[:, 3:] == 0, axis=1))
        
        # Verificar se a quantidade de linhas com zero é igual ou muito próxima ao total de linhas
        limite_proximidade = 0.2  # 20% de tolerância para proximidade
        if lines_with_zeros == 0:
            verif_dom = users_skills.shape[0]
        else:
            if lines_with_zeros < len(users_skills) * (1 - limite_proximidade):
                # Remover as linhas com pelo menos um valor 0
                users_skills = users_skills[~np.any(users_skills[:, 3:] == 0, axis=1)]
                verif_dom = users_skills.shape[0]
            else:
                verif_dom = users_skills.shape[0]
                
        # Criando matriz vazia para salvar resultados
        distances_results = np.zeros((verif_dom, 1))
        
        #Criar vetor com a quantidade de posições igual a quantidades de habilidades requeridas
        skills_quant = len(skills_index)
        skills_max = np.full(skills_quant, 10)
        
        # Nova matriz apenas com as habilidades requeridas
        skills_dist = users_skills[:, 3:]
        
        # Verificando distancia das habilidades
        for i in range(verif_dom):
          user_current = skills_dist[i, :]
          user_current_reshaped = user_current.reshape(1, -1)
          skills_max_reshaped = skills_max.reshape(1, -1)
          variation = user_current_reshaped - skills_max_reshaped
          distance = np.linalg.norm(variation)
          distances_results[i, 0] = distance
          
        # Juntando os resultados de distancia com a disponibilidade e a carga de trabalho
        disp_cargat = users_skills[:, :3]
        verif_dom = np.hstack((disp_cargat, distances_results))
        
        # Função para encontrar os usuários não dominados e atualizar a matriz
        def find_and_update_non_dominated(df):
            non_dominated_users = []
            
            for idx, row in df.iterrows():
                filtered = df[(df['Disponibilidade'] >= row['Disponibilidade']) &
                              (df['Carga_de_Trabalho'] <= row['Carga_de_Trabalho']) &
                              (df['Habilidade'] <= row['Habilidade'])]
        
                if len(filtered) == 1:
                    non_dominated_users.append(int(row['ID']))
        
            # Atualizar o ranking com os IDs dos usuários não dominados
            ranking.extend(non_dominated_users)
            
            # Remover usuários não dominados do DataFrame
            df_filtered = df[~df['ID'].isin(non_dominated_users)]
            
            return df_filtered
        
        # Criando um DataFrame com os dados
        columns = ['ID', 'Disponibilidade', 'Carga_de_Trabalho', 'Habilidade']
        df = pd.DataFrame(verif_dom, columns=columns)
        
        # Lista para armazenar o ranking
        ranking = []
        
        # Repetir até que a matriz esteja vazia
        while not df.empty:
            df = find_and_update_non_dominated(df)
            
        # Seus arrays
        ranking = np.array(ranking)
        ids = np.array(ids)
        
        # Criar o array reorganizado
        ranking_organized = ids[ranking]
        
        # Convertendo para lista
        lst_ranking = ranking_organized.tolist()
        return jsonify({'ranking': lst_ranking})
        
    except Exception as e:
        error_message = f"Erro durante o processamento: {str(e)}"
        print(error_message)  # Imprimir o erro no console para depuração
        return jsonify({'error': error_message}), 400

if __name__ == '__main__':
    app.run(debug=True)
