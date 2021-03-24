# Blog social desenvolvido com Flask

Aplicação de blog social desenvolvida em flasky, possuindo features como, seguidores, criar publicações, fazer comentarios em publicações entre outras.

## Como rodar o projeto

Para rodar o projeto é preciso criar um ambiente virtual python e então instalar as dependencias de bibliotecas para fazer isso você pode seguir a sequência de passos a seguir

### Criando e ativando o ambiente virtual

    python -m venv venv
    venv\Scripts\activate

### Instalando dependências
    
    pip install -r requirements.txt

### Configurando as variaveis e rodando o projeto

##### Windows
    set FLASK_APP=flasky
    flask run

##### Linux
    export FLASK_APP=flasky
    flask run

