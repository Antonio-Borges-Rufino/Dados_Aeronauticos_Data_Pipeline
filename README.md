# Big Data Cluster
1. A estrutura de big data usada nesse trabalho está totalmente descrita [aqui](https://github.com/Antonio-Borges-Rufino/Hadoop_Ecosystem).
2. Assume-se que para repodução das tarefas, usa-se um cluster igual ou similar a esse apresentado.

# Detalhes do projeto
1. O ramo aeronautico usa os dados de forma massiva para poder melhorar sua estrutura, seus serviços e a segurança. Esse projeto propõe a criação de um pipeline completo de dados de incidentes aeronauticos desde a obtenção através de API, até a sua mostragem a partir de gráficos.  
2. Para realizar esse trabalho, pensou-se na sequinte estrutura.     
  -> 1. Criar uma API própria para disponibilizar os dados baseada na API de incidadentes da ICAO.     
  -> 2. Obter os dados em 2 pipelines diferentes. Através de batch e de streaming.  
  -> 3. Guardar os dados em um SGBD e no HDFS para o Hive.  
  -> 4. Acessar esses dados utilizando um serviço de BI.  


# Arquitetura do projeto
![PipeLine](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/PipeLine-Arq.png)
1. A arquitetura de funcionamento está representada na imagem acima.

