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
5. A primeira coisa que eu faço na chamada do método GET é buscar o arquivo de incidentes e carregar ele com o pandas.
```
df = pd.read_csv("/home/hadoop/projetos/Scripts_Data/faa_incidents_data.csv")
```
6. Esse procedimento vai facilitar muito a pesquisa e aquisição dos dados para retorno, o pandas é uma biblioteca muito eficiente para manipulação dos dados e simplifica o processo.
7. Depois, verifico se o caracter coringa foi passado, se isso acontecer, eu retorno todos os registros, caso não, faço a pesquisa relacionada ao primeiro parâmetro event_city.
```
if event_city != "*":
            df = df.loc[df["Event City"]==event_city,['AIDS Report Number','Local Event Date','Event City','Event State','Event Airport','Aircraft Damage','Flight Phase','Aircraft Make','Aircraft Model']]
        else:
            df = df[['AIDS Report Number','Local Event Date','Event City','Event State','Event Airport','Aircraft Damage','Flight Phase','Aircraft Make','Aircraft Model']]
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
  df = df.loc[df["Aircraft Damage"]==aircraft_damage]
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
  df = df.loc[df["Flight Phase"]==flight_phase]
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
  df = df.loc[df["Aircraft Make"]==aircraft_make]
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
16. Todo o código da API pode ser encontrado [aqui](https://github.com/Antonio-Borges-Rufino/Dados_Aeronauticos_Data_Pipeline/blob/main/Api_Data_Incidents.py)

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
