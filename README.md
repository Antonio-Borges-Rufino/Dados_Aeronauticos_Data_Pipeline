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
![PipeLine](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PipeLine-Arq.png)
1. A arquitetura de funcionamento está representada na imagem acima.
2. Primeiro foi construida uma API que simula a API da ICAO sobre incidentes aeronauticos.
3. A api é composta apenas por incidentes dos EUA e os dados podem ser acessados [aqui](https://www.kaggle.com/datasets/prathamsharma123/aviation-accidents-and-incidents-ntsb-faa-waas?select=faa_incidents_data.csv).
4. A construção da API vai ser detalhada mais a frente.
5. Depois foram construidos 2 arquivos CSV para poder fazer a raspagem da API. Um deles contem as cidades que vão ter informações salvas no mysql em batch, e o outro contem as cidades que vão ser passadas como stream para o kafka.
6. Para fazer a raspagem da API, utilizei o APache NiFi. Ele quem é responsavel por fazer o insert no mysql e produzir para o kafka.
7. Com os dados no kafka, utilizei o apache druid para fazer a coleta dos dados do Kafka, fazer algumas limpezas e mandar para uma tabela hive no Hdfs.
8. Com a tabela no Hive pronta, fiz algumas consultas e apresentei no tableu.

# API 
1. O objetivo nessa etapa foi construir uma API que simulava a API da ICAO para incidentes aeronauticos.
2. Para cumprir esse obejtivo, utilizei a biblioteca flask do python para construir uma API sem autenticação que tinha como função retornar registros de incidentes aeronauticos nos EUA.
3. Para construir a API utilizei o Flask, Pandas e o conjunto de dados disposto na secção de arquitetura.
4. Por definição, a API possui 4 parâmetros: event_city/aircraft_damage/flight_phase/aircraft_make; a os parâmetros podem ser subistituidos por '*' como coringa.
5. A primeira coisa que eu faço na chamada do método GET é buscar o arquivo de incidentes e carregar ele com o pandas. Também foram renomeadas as colunas para serem posteriormente processadas pelo NiFi.
```
df = pd.read_csv("/home/hadoop/projetos/Scripts_Data/faa_incidents_data.csv")
df = df.rename(columns={'AIDS Report Number':'AIDSReportNumber','Local Event Date':'LocalEventDate','Event City':'EventCity','Event State':'EventState','Event Airport':'EventAirport','Aircraft Damage':'AircraftDamage','Flight Phase':'FlightPhase','Aircraft Make':'AircraftMake','Aircraft Model':'AircraftModel'})
```
6. Esse procedimento vai facilitar muito a pesquisa e aquisição dos dados para retorno, o pandas é uma biblioteca muito eficiente para manipulação dos dados e simplifica o processo.
7. Depois, verifico se o caracter coringa foi passado, se isso acontecer, eu retorno todos os registros, caso não, faço a pesquisa relacionada ao primeiro parâmetro event_city.
```
if event_city != "*":
            df = df.loc[df["EventCity"]==event_city,['AIDSReportNumber','LocalEventDate','EventCity','EventState','EventAirport','AircraftDamage','FlightPhase','AircraftMake','AircraftModel']]
        else:
            df = df[['AIDSReportNumber','LocalEventDate','EventCity','EventState','EventAirport','AircraftDamage','FlightPhase','AircraftMake','AircraftModel']]
```
8. O próximo passo é verificar se existe registros na pesquisa realizada, caso não exista registros retorna NULL em forma de dict python.
```
if len(df)>0:
  CODE...
else:
  return {"Result":"Null"}
```
9. Caso exista registros, vai ser feita verificações para todos os parâmetros, entre elas: A existencia de registros para aquele parâmetro e se o parâmetro é coringa.
10. Todos os aninhamentos vão ser demonstrados aqui, leve em consideração que CODE... representa o próximo aninhamento, que vou quebrar aqui para ficar mais fácil a visualização.
11. Aninhamento de aircraft_damage.
```
if aircraft_damage != '*':
  df = df.loc[df["AircraftDamage"]==aircraft_damage]
else:
  df = df
if len(df)> 0:
  CODE...
else:
  return {"Result":"|Null"} 
```
12. Aninhamento de flight_phase.
```
if flight_phase != "*":
  df = df.loc[df["FlightPhase"]==flight_phase]
else:
  df = df
if len(df)>0:
  CODE...
else:
  return {"Result":"||Null"}
```
13. No próximo aninhamento, já encontramos o retorno da API, mas vou demontrar apenas o aninhamento de aircraft_make.
```
if aircraft_make != "*":
  df = df.loc[df["AircraftMake"]==aircraft_make]
else:
  df = df
if len(df)>0:
  <RETORNO DA API>
else:
  return {"Result":"|||Null"}
```
14. O código de <RETORNO API> começa com uma subistituição dos valores nulos pela string "None", isso vai ser importante para que depois o NaN não atrapalhe na conversão para o Json no NiFi. Depois, uso a função do pandas to_dict para retornar um dicionario de dados, o parâmetro orient='records' indica que o dicionário deve ser separado por linha, ou seja, dentro da grande estrutura [] deverá haver N pequenas estruturas {} que deverão conter as colunas:valor de cada linha do Df Pandas. Vai ser demonstrado o retorno da API a seguir.
```
df.fillna("None",inplace=True)
df = df.to_dict(orient='records')
return df
```
15. Retorno da API
```
[
    {
        "AIDS Report Number": "19780103001059I",
        "Local Event Date": "03-JAN-78",
        "Event City": "MIAMI",
        "Event State": "FL",
        "Event Airport": "MIAMI INTL",
        "Aircraft Damage": "None",
        "Flight Phase": "NORMAL CRUISE",
        "Aircraft Make": "DOUGLAS",
        "Aircraft Model": "DC8"
    },...
 ]
```
16. Todo o código da API pode ser encontrado [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/Api_Data_Incidents.py).

# SQL Create Database
1. Acesse o cluster por ssh e desvie o tráfego para a porta 80 da sua máquina local.
```
ssh -L 80:localhost:80 hadoop@<IP_VM>
```
2. Acesse o phpmyadmin atraves da URL.
```
http://localhost/phpmyadmin
```
3. Abra o terminal de comandos SQL e digite.
```
CREATE DATABASE incidents;
```
4. Acesse a nova base de dados através do menu lateral clicando sobre ela.
5. Após estar na base de dados, clique novamente no menu SQL e crie a tabela que vai receber as informações. Essa tabela deve respeitar o schema definido [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/avro_schema.txt).
```
CREATE TABLE incidents_aer (AIDSReportNumber VARCHAR(255),LocalEventDate VARCHAR(255),EventCity VARCHAR(255),EventState VARCHAR(255),EventAirport VARCHAR(255),AircraftDamage VARCHAR(255),FlightPhase VARCHAR(255),AircraftMake VARCHAR(255),AircraftModel VARCHAR(255),PRIMARY KEY (AIDSReportNumber));
```
6. O mysql agora está configurado para receber os dados da API.

# NiFi Flow
1. Para execurtamos a tarefa do pipeline, vamos dividir em 2 grupos de processo diferentes, ambos vão ser explicados posteriormente.
2. Os 2 grupos de processo estão demonstrados na imagem abaixo
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/NIFI_FLOW.PNG)
3. O grupo de processos GET_API_INSERT_SQL deve executar a parte do pipeline que lê um arquivo CSV com informações que devem ser buscadas pelo NiFi da API, e então gravar essas informações no MySQL.
4. O grupo de processos GET_API_KAFKA deve executar o pipeline que vai ler um arquivo CSV igual ao grupo GET_API_INSERT_SQL, mas ele em vez de gravar no banco, vai enviar as informações para o kafka em forma de mensagem.

# Processo GET_API_INSERT_SQL
1. Esse processo tem como objetivo coletar dados da API e salvá-los no MySQL.
2. Aqui está o pipeline de funcionamento do process group.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/GET_API_INSERT_SQL.PNG)
3. As caixinhas vão ser sequencialmente explicadas, para que tudo funcione perfeitamente bem.
4. A primeira caixinha é a PegarCSV, ela é responsável por ler o CSV que delimita quais são os dados que vão ser buscados na API, esse csv está disponível [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/sql_get.csv). A caixinha utiliza o processo GetFile 1.18.0 que busca um arquivo CSV dentro do sistemas de arquivos do servidor.
5. A imagem abaixo mostra a configuração da caixa.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PegarCSV.PNG)
6. Essa é a única aba que terá modificações nessa caixinha, é bom ressaltar que o arquivo depois de lido é deletado do servidor.
7. O atributo "Input Directory" recebe o caminho da pasta onde vai ser coletado o arquivo CSV, nesse caso, "/home/hadoop/projetos/Scripts_Data".
8. O atributo "File Filter" recebe o nome do arquivo ou uma expressão regular reconhecida pelo JAVA caso seja mais de 1 arquivo, nesse caso ele recebe "sql_get.csv".
9. Os atributos de relationships são determinados na ligação entre essa caixa com a próxima, nesse caso, o atributo marcado é "success".
10. A próxima caixa adicionada é a SplitCsvSQL do tipo SplitRecord 1.18.0, ela vai fazer o split das linhas do csv, ou seja, ele pega o arquivo csv e o separa em vários flows, cada um com uma linha do csv, cada linha vai ser processada individualmente nas próximas etapas. Aqui também é feita a conversão de csv para JSON, cada linha vai ser separada e convertida para JSON para depois ser processada. A imagem abaixo mostra as caixas que sofreram alterações.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/SplitCsvSQL.PNG)
11. A aba relationships mostra o que o NiFi deve fazer caso aconteça alguns deses cenários, só foram marcados os cenários de falha e original porque o cenário de split vai ser marcado na conexão dessa caixa com a próxima.
12. O primeiro atributo modificado da aba de propiedades é o "Record Reader", nele vamos passar um processor que vai ler o CSV do tipo CSVReader 1.18.0 com as propiedades setadas como na figura abaixo.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/csvTransform1.png)
13. O segundo atributo é o "Record Writer", ele é o responsavel por fazer o output da leitura no formato Json. O processor é do tipo JsonRecordSetWriter 1.18.0 e vai transformar cada linha csv "splitada" é uma string JSON com os dados organizados. As configurações do arquivo está presente na imagem abaixo.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/jsonTransform1.png)
14. O ultimo atributo modificado é o "Records Per Split", que diz quantas linhas do csv vão ser "splitadas" por arquivo de saída, nesse caso, apenas 1, ou seja, uma linha do csv vai se transformar em um arquivo Json próprio.
15. A próxima caixa a ser adicionada é a PegarAtributosPesquisa do tipo EvaluateJsonPath 1.18.0, essa caixa é responsável por pegar os atributos de cada Json separadamente e os transformar em variáveis que serão posteriormente usadas. A imagem abaixo mostra os atributos modificaveis.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PegarAtributosPesquisa.png)
16. Em relationships está marcado apenas "failure" e "unmatched" porque o matched será marcado na conexão dessa caixa com a próxima.
17. Nas propiedades, o atributo "Destination" recebe flowfile-attribute. Depois, cria-se 4 novos atributos que vão ser repassados adiante, eles devem ser condizentes com os especificados no json, ou seja, não podem ter atributos diferentes.
18. Os atributos são "AircraftDamage" que recebe "$.AircraftDamage", "AircraftMake" que recebe "$.AircraftMake", "EventCity" que recebe "$.EventCity" e "FlightPhase" que recebe "$.FlightPhase."
19. A próxima caixa adicionada é a get_incidents do tipo InvokeHTTP 1.18.0, ela é responsável por pegar cada um dos arquivos "splitados" que se transformaram em variáveis e fazer uma requisição GET na API que construimos anteriormente. A imagem abaixo mostra sua configuração.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/get_incidents.jpg)
20. Na aba de relationships está marcado todos, menos response, que será marcado quando for feita a conexão com a próxima caixa do pipeline.
21. Nas propiedades, a única modificada foi a URL, que recebeu "http://127.0.0.1:5000/${EventCity}/${AircraftDamage}/${FlightPhase}/${AircraftMake}", essa construção pega todas as variaveis passadas da caixa anterior e as coloca dentro da URL para fazer o GET e obter os dados.  
  OBS: Na aba "Scheduling" existe uma opção chamada "Run Schedule", nela você pode colocar um tempo de espera de uma execução a outra do card, no meu caso, coloquei "1 min" o que siginfica que essa caixa vai rodar de 1 e 1 minutos fazendo o GET na minha API.  
22. A próxima caixa a ser adicionada é a atibute_schema do tipo UpdateAttribute 1.18.0, a sua função e criar um schema de transformação dos dados, isso é necessário porque a API devolve os dados no formato dict do python, apesar das similaridades, esse formato pode possuir algumas inconsistencias com o Json, para evitar esse tipo de coisa usa-se a transformação de atributo, e criar um schema válido é parte disso. As propiedades da caixa está demonstrada na imagem abaixo.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/atibute_schema.JPG)
23. Aqui, apenas 1 atributo foi adicionado, o schema.name que recebe "inform_incid". O "inform_incid" é um processo avro do tipo AvroSchemaRegistry 1.18.0 que retém um schema pré-definido para um conjunto de dados Json.
24. Para poder adicionar o "inform_incid" você precisa ir até o painel de process group, clicar em cima de GET_API_INSERT_SQL e no painel esquerdo criar em cima da engrenagem. Após isso, adicione um processo novo em "+" do tipo AvroSchemaRegistry 1.18.0 e configure como na imagem abaixo.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/avro_schema_reg.jpg)
25. O schema colocado no atributo inform_incid está [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/avro_schema.txt).
26. A penultima caixa é a tranformação dos dados de dict para Json propiamente dito. Fazemos isso através da caixa Write_Json do tipo ConvertRecord 1.18.0. O tipo ConvertRecord 1.18.0 também requer atributos "Record Reader" e "Record Writer", entretanto, dessa vez, todos os atributos são do tipo JSON, sendo o atributo "Record Reader" do tipo JsonTreeReader 1.18.0 e o atributo "Record Writer" do tipo JsonRecordSetWriter 1.18.0. Todas as configurações estão sendo mostradas na imagem abaixo.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/atribute_json_convert.jpg)  
27. A caixa Write_Json é conectada por fim a caixa PutDatabaseRecord do tipo PutDatabaseRecord 1.18.0, é essa caixa que faz a inserção dos dados convertidos em JSON no banco de dados MySql. As caixas são ligadas através do atributo Relationships "success". A configuração dessa caixa é mostrada na imagem a seguir.  
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/putsql.JPG) 
28. O atributo Database Type indica qual é o tipo de base de dados que será usada, por isso ele recebe MySql.
29. O atributo Statement Type indica qual é o tipo de ação usada, ele recebe INSERT porque o que queremos é a inserção dos dados.
30. O atributo Schema Name recebe o nome da base de dados que queremos fazer a incersão.
31. O atributo Table Name receb o nome da tabela que vamos inserir os dados.
31. Os 2 atributos anteriores são relacionados a criação da base de dados discutido anteriormente.
32. O atributo Record Reader recebe um controller também, esse controler pode ser criado indo até o painel de grupos de processo, clicando em cima do grupo 
GET_API_INSERT_SQL e no painel esquerdo clicando em cima da engrenagem. Entrando na pasta clica-se em "+" e adiciona o controle DBCPConnectionPool 1.18.0 como na imagem a seguir.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/conect_sql_pull.JPG)
33. Na imagem, os atributos modificados foram: Database Connection URL que recebe a url de conexão padrão jdbc:mysql://localhost:3306/incidents. O atributo Database Driver Class Name que recebe com.mysql.jdbc.Driver que é a classe do pacote jar que faz a conexão. O atributo Database Driver Location(s) que aponta onde ta o mysql_conector /home/hadoop/hadoop_ecosystem/nifi/mysql-connector-java-8.0.30.jar, o [mysql_conector pode ser obtido aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/mysql-connector-java-8.0.30.jar). E por fim os atributos Database User que é root e o atributo Password que é a senha que voce configurou seu mysql.
34. E por fim o ultimo atributo modificado em PutDatabaseRecord que é o Record Reader. Ele também é um controle da classe JsonTreeReader 1.18.0 mas com todos os parâmetros default. Ou seja, você apenas instancia um novo como os anteriores e não mexe em mais nada, apenas roda.
35. Com isso, terminamos o primeiro fluxo de dados. API->NiFi->Mysql

# Processo GET_API_KAFKA
1. Com o servidor kafka rodando, execute o comando para criar o tópico "api-get-data", que será respnsável por receber os dados.
```
kafka-topics.sh --create --topic api-get-data --bootstrap-server localhost:9092
```
2. O processo do NiFi tem como objetivo pegar os dados da API e envialos para o Kafka, para que posteriormente seja lido pelo Druid.
3. O pipeline de funcionamento do processo GET_API_KAFKA está representado pela imagem abaixo.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/kafka_pipeline_nifi.JPG)
4. A primeira caixa é a PegarCsvKafka do tipo GetFile 1.18.0, ela tem como objetivo pegar o arquivo .csv que vai mostrar quais informações coletar da API. O arquivo .csv pode ser encontrado [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/kafka_get.csv). A imagem abaixo mostra as propiedades da caixinha.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PegarCsvKafka.JPG)
5. Os atributos modificados foram: "Input Directory" que recebe o caminho do csv (/home/hadoop/projetos/Scripts_Data) e "File Filter" que recebe um filtro para os arquivos que vão ser pegos, no caso, aqui foi posto apenas o nome do arquivo (kafka_get.csv).
6. O atributo Relationships será inserido na conexão com a próxima caixa.
7. A próxima caixa do processo é a SplitCsvToJson do tipo SplitRecord 1.18.0, ela te como objetivo pegar cada linha do arquivo .csv e tranformar em uma linha de JSON separada, que vai servir para montar a URL posteriormente. A imagem abaixo mostra os atributos configuraveis da caixa.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/SplitCsvToJson.jpg)
8. A caixa recebe 3 parâmetros, o parâmetro "Record Reader" recebe um serviço de controle do tipo CSVReader 1.18.0 com o nome de LerCsvKafka, ele é reponsável por ler o arquivo .csv e transformar em um flowfile, a segunda imagem do card mostra os atributos desse serviço de controle. O próximo parâmetro é o "Record Writer" que também recebe um serviço de controle do tipo JsonRecordSetWriter 1.18.0 com o nome de SplitJsonGetApi, ele é responsável por transformar cada linha do arquivo .csv em uma linha de JSON válida e as suas configurações estão na terceira imagem do card. Por ultimo, o parâmetro "Records Per Split" que separa a quantidade de linhas .csv que serão transformadas em um arquivo JSON, nesse caso, 1 linha se transforma em um arquivo JSON próprio.
9. A aba Relationships tem marcada apenas as opções "failure" e "original" como terminate. A opção "splits" é marcada na conexão com a próxima caixa.
10. A próxima caixa é a PegarAtributosPesquisa do tipo EvaluateJsonPath 1.18.0, ela é responsável por pegar cada JSON do passo anterior e os transformar em variaveis dentro do pipeline, e essas variaveis podem ser acessadas por qualquer caixa que esteja ligada a essa. A imagem abaixo mostra os atributos configuraveis da caixa.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PegarAtributosPesquisa.JPG)
11. Os atributos configurados aqui são: "Destination" que recebe flowfile-attribute como valor, esse valor indica a transformação em atributos das variaveis lidas no JSON. Os próximos atributos são as variaveis do arquivo JSON que são: "AircraftDamage","AircraftMake","EventCity","FlightPhase", elas recebem os valores dos atributos JSON "$.AircraftDamage","$.AircraftMake","$.EventCity","$.FlightPhase", essas variaveis podem ser acessadas através do nome dos atributos.
12. Na aba Relationships são marcados apenas "failure" e "unmatched" como "terminate", o atributo matched vai ser marcado na ligação com a próxima caixa.
13. A próxima caixa é a InvokeHTTP do tipo InvokeHTTP 1.18.0, ela é responsável por fazer a requisição da api e por recuperar os dados retorndados. A imagem abaixo mostra os atributos configuraveis
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/invokehttpkafka.JPG)
14. Nesse caso, o único atributo setado foi o "HTTP URL" que recebeu a URL da API (http://127.0.0.1:5000/${EventCity}/${AircraftDamage}/${FlightPhase}/${AircraftMake}) junto com as variaveis criadas anteriormente.
15. Na aba Relationships todas as opções foi marcada como "terminate" exceto a opção "response" que é marcada quando conecta essa caixa a próxima.
16. Na aba scheduling você pode configurar um tempo de espera entre uma execução e outra no campo "Run Schedule", no meu caso, coloquei 1 min.
17. A próxima caixa é a UpdateAtributosJsonGet do tio UpdateAttribute 1.18.0, ele é responsável por montar um schema apropiado para a resposta do http. A imagem abaixo mostra os atributos configuraveis da caixa.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/UpdateAtributosJsonGetkafka.jpg)
18. O atributo configurado aqui foi o "schema.name" que recebe o [schema](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/avro_schema.txt) básico avro e valida, nesse caso, ele aponta para o controle de serviço AvroSchemaRegistry do tipo AvroSchemaRegistry 1.18.0 que está representado na segunda imagem do card.
19. A próxima caixa é a ConvertToJsonGetResponse do tipo ConvertRecord 1.18.0, ela é responsável por pegar as informações da API que são retornadas no tipo dict e transformalas para o tipo JSON através de serviços de controle. A imagem abaixo mostra os atributos configuraveis da caixa.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/ConvertToJsonGetResponsekafka.jpg)  
20. Aqui configuramos 2 atributos, o primeiro é o "Record Reader" que recebe um serviço de controle do tipo JsonTreeReader 1.18.0 chamado LerJsonSchemaAvro, esse serviço de controle possui 3 atributos configuraveis presente na segunda imagem do card, os atributos "Schema Access Strategy" que recebe "Use 'Schema Name' Property" porque existe um schema já configurado, o atributo "Schema Registry" que recebe de fato o serviço de controle AvroSchemaRegistry 1.18.0 que vai ser posteriormente discutido e o atributo "Schema Name" que faz referencia ao schema do serviço de controle. O segundo atributo da caixa é o "Record Writer" que recebe também um serviço de controle do tipo JsonRecordSetWriter 1.18.0 com nome JsonRecordSetWriter que possui atributos semelhantes aos do "Record Reader", as configurações do atributo está sendo mostrada na imagem 3 do card.
21. O controle de serviço AvroSchemaRegistry 1.18.0 é o mesmo demostrado na imagem 2 do card da seção 17.
22. Na aba Relationships o único marcado foi "failure" como "terminate", o "success" será marcado na ligação com a próxima caixa.
23. A próxima caixa é a SplitJsonGet do tipo SplitJson 1.18.0, ela é responsável por transformar um grande arquivo que veio da requisição da API e foi tranformado para JSON em vários arquivos JSON contendo um único registro que vai ser enviado individualmente ao Kafa. A imagem abaixo mostra os atributos modificaveis.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/SplitJsonGetkafka.JPG)
24. Aqui apenas o atributo "JsonPath Expression" recebeu modificações, a string "$.*" indica uma separação de todos os registros.
25. Na aba Relationships todos foram marcados como "terminate" exceto "splits" que vai ser marcado como "terminate" quando fizer a ligação com a próxima caixa.
26. A ultima caixa do grupo de processos é a PublishKafka_2_6 do tipo PublishKafka_2_6 1.18.0, ela é responsável por publicar no tópico kafka os registros que chegam da caixa anterior. A imagem abaixo mostra os atributos configuraveis.
![](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/imgs/PublishKafkaset.JPG)
27. O atributo "Kafka Brokers" recebe o endereço do host kafka, no nosso caso, é localhost:9092, que é o endereço padrão. O atributo "Topic Name" recebe o nome do tópico que você quer fazer a inserção, no nosso caso, o tópico api-get-data.
28. Na aba Relationships todos foram marcados como "terminate".
29. Com isso, terminamos a parte de inserção dos dados, agora vem as partes de análise com tableu + hive e apache druid, e movimentação dos dados com spark e hdfs.

# Movimentando tabela SQL com Spark para o HDFS e Hive
1. Execute o código da API que criamos.
```
source projetos/bin/activate
python3 projetos/Scripts_Data/Api_Data_Incidents.py
```
2. Execute o pipeline GET_API_INSERT_SQL no NiFi.
```
nifi.sh run
```
3. Execute o hiveserver2
```
hiveserver2
```
4. Optei por fazer os comando utilizando o jupyter noteook, mas, se você não quiser, pode gerar um arquivo python com os códigos fontes aqui demonstrados e usar o seguinte comando.
```
spark-submit --jars /home/hadoop/hadoop_ecosystem/spark/Conectores/mysql-connector-java-8.0.30.jar /home/hadoop/projetos/Scripts_Data/Spark_Mysql_Hive.py
```
5. Inicie o jupyter notebook em qualquer porta e crie o arquivo Spark_Mysql_Hive dentro do nosso ambiente virtual.
6. Primeiro, crie um sparkSession para poder se conectar ao spark.
```
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("salvarHive") \
        .config("spark.jars","/home/hadoop/hadoop_ecosystem/spark/Conectores/mysql-connector-java-8.0.30.jar") \
        .enableHiveSupport().getOrCreate()
```
7. No código acima podemos ver alguns pontos. O primeiro é o .config() que traz o jar de conexão com o mysql, essa linha é crucial para que o código funcione no jupyter, já que a conexão com jdbc:mysql não é nativa do spark. 
8. Outro elemento perceptivel é o .enableHiveSupport(), esse atributo permite que o spark se conecte ao metastore do hive, transformando o backend do spark sql em uma extensão da metastore do hive. Você pode otimizar esse processo atribuindo ao hive uma engine spark com configurações Hive-On-Spark, mas aqui foi apenas para passar o conteudo para o hdfs.
9. Para se certificar da conexão com o hive, o próximo bloco de código verifica as databases e cria a database que vamos passar as informações, chamada de teste_h.
```
spark.sql("show databases").show()
spark.sql("create database teste_h")
spark.sql("use teste_h")
```
10. Com isso, temos a database criada e podemos fazer a transferencia dos arquivos para o hive. Para ver se a database foi realmente criada, execute esse o comando abaixo no hdfs, precisa aparecer uma pasta chamada teste_h.db
```
hdfs dfs -ls /user/hive/warehouse
```
11. Com a conexão feita e o database criado, vou conectar ao mysql através do driver indicado no primeiro bloco de código. Para isso, utilizo o método read.format("jdbc").
```
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:mysql://localhost:3306/incidents") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("dbtable", "incidents_aer") \
    .option("user", "root") \
    .option("password", "123456789") \
    .load()
```
12. A option("url", "jdbc:mysql://localhost:3306/incidents") indica a forma de acesso ao banco de dados mysql, enquanto option("driver", "com.mysql.cj.jdbc.Driver") indica qual driver vai ser usado para fazer a conexão, optei por esse porque o com.mysql.jdbc.Driver já está sem suporte, apenas para tirar o warn. As outras options são configurações normais, como os usuários de acesso, que são os mesmos do phpmyadmin e a tabela que queremos acessar.
13. Para confirmar a conexão com a tabela, dou um show() no df para ver os registros.
```
df.show()
```
14. Com a conexão feita tanto no hive quanto no mysql, agora é só salvar o df como tabela no banco teste_h do hive. O comando para fazer isso é mostrado no próximo bloco de código.
```
df.write.saveAsTable("incidents_aer")  
```
15. Para confirmar que a tabela foi salva no hive, vou primeiro buscar no hdfs. O resultado do comando abaixo deve ser um diretório chamado incidents_aer
```
hdfs dfs -ls /user/hive/warehouse/teste_h.db
```
16. Agora, vou salvar o arquivo no HDFS usando o formato csv, esse arquivo vai servir de input para o druid.
```
df.write.csv("hdfs://localhost:9000/get_mysql")
```
17. Comfirmando que o arquivo parquet foi salvo no hdfs
```
!hdfs dfs -ls /get_mysql
```
18. Depois, no último bloco de código, vou apenas dar um select na tabela utilizando o spark.
```
spark.sql("SELECT * FROM incidents_aer").show()  
```
19. Todo o código pode ser acessado [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/Spark_Mysql_Hive.ipynb)  

OBS: Para esse trabalho poderia ser usado o sqoop, mas como o ambiente que estou usando comporta os mais atualizados (até o momento) software, o sqoop teve incompatibilidade com o driver mysql de acesso, portanto, optei por não usar o sqoop e sim o spark, que é tão poderoso quanto. 
