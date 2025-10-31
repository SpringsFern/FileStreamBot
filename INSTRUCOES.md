# Instruções de Uso - WebStreamer

Este arquivo explica como compilar e executar o bot WebStreamer em sua máquina local.

## Passos para Execução

1.  **Compile o executável:**
    *   Execute o script de compilação apropriado para o seu sistema operacional:
        *   **Windows:** Execute `build.bat`.
        *   **Linux/macOS:** Execute `build.sh` em seu terminal com `./build.sh`.
    *   Este comando instalará as dependências necessárias e criará um arquivo executável na pasta `dist`.

2.  **Coloque o executável em uma pasta:**
    *   Copie o arquivo `WebStreamer` (ou `WebStreamer.exe` no Windows) da pasta `dist` para uma nova pasta onde você deseja executar o bot.

3.  **Crie o arquivo de configuração `.env`:**
    *   Na mesma pasta onde você colocou o executável, crie um novo arquivo de texto chamado `.env`.

4.  **Adicione as variáveis de ambiente ao arquivo `.env`:**
    *   Abra o arquivo `.env` com um editor de texto e adicione as seguintes variáveis obrigatórias. Substitua os valores de exemplo pelos seus próprios valores.

    ```
    API_ID=1234567
    API_HASH=sua_api_hash_aqui
    BOT_TOKEN=seu_bot_token_aqui
    BIN_CHANNEL=-1001234567890
    ```

    *   **Como obter os valores:**
        *   `API_ID` e `API_HASH`: Obtenha em [my.telegram.org](https://my.telegram.org).
        *   `BOT_TOKEN`: Obtenha com o [@BotFather](https://telegram.dog/BotFather) no Telegram.
        *   `BIN_CHANNEL`: Crie um canal no Telegram (público ou privado), poste algo nele. Encaminhe essa postagem para [@missrose_bot](https://telegram.dog/MissRose_bot) e responda com `/id`. O ID do canal será retornado.

5.  **Execute o bot:**
    *   Abra um terminal ou prompt de comando na pasta onde estão o executável e o arquivo `.env`.
    *   Execute o seguinte comando:

    ```bash
    ./WebStreamer
    ```
    *   Se você estiver no Windows, pode ser necessário apenas dar um duplo clique no arquivo `WebStreamer.exe` ou executar no prompt de comando:
    ```cmd
    WebStreamer.exe
    ```

O bot agora deve estar em execução e pronto para ser usado.
