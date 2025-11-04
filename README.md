🚀 Passos para ativação do projeto

Baixe o projeto
Faça o download deste repositório e salve-o em seu computador.

Abra o projeto no VS Code
No Visual Studio Code, abra a pasta onde o projeto foi salvo.

Crie um ambiente virtual

    python -m venv venv

Ative o ambiente virtual

Windows:

    .\venv\Scripts\activate

Linux/Mac:

    source venv/bin/activate

Atualize o pip

    python -m pip install --upgrade pip

Instale as dependências do projeto

    pip install -r requirements.md

Configure as informações do banco de dados
Aplique as migrações do banco de dados

    python manage.py migrate

Execute o servidor de desenvolvimento

    python manage.py runserver

Acesse o projeto no navegador
