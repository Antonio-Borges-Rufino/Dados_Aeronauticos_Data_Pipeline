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
2. Primeiro foi construida uma API que simula a API da ICAO sobre incidentes aeronauticos.
3. A api é composta apenas por incidentes dos EUA e os dados podem ser acessados [aqui](https://www.kaggle.com/datasets/prathamsharma123/aviation-accidents-and-incidents-ntsb-faa-waas?select=faa_incidents_data.csv)
4. A construção da API vai ser detalhada mais a frente.
5. Depois foram construidos 2 arquivos CSV para poder fazer a raspagem da API. Um deles contem as cidades que vão ter informações salvas no mysql em batch, e o outro contem as cidades que vão ser passadas como stream para o kafka.
6. Para fazer a raspagem da API, utilizei o APache NiFi. Ele quem é responsavel por fazer o insert no mysql e produzir para o kafka.
7. Com os dados no kafka, utilizei o apache druid para fazer a coleta dos dados do Kafka, fazer algumas limpezas e mandar para uma tabela hive no Hdfs.
8. Com a tabela no Hive pronta, fiz algumas consultas e apresentei no tableu.

