# Hash Legendador

Ferramenta Streamlit para gerar legendas (formato SRT) a partir de vídeos ou áudios em português usando o modelo Whisper da OpenAI.

## Requisitos
- Python 3.11+ (testado com 3.13)
- `ffmpeg` disponível no PATH (necessário para o pydub)
- Conta na OpenAI com chave de API válida

## Instalação
1. Crie e ative um ambiente virtual (opcional, mas recomendado).
2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
3. Garanta que o `ffmpeg` está instalado. Em Windows, você pode instalar via [ffmpeg.org](https://ffmpeg.org/download.html). Depois de baixar, adicione a pasta `bin` do ffmpeg ao PATH do sistema.

## Configuração
Crie um arquivo `.env` na pasta `aula_fazer_teste` com a chave da OpenAI:
```
OPENAI_API_KEY=sk-minha-chave
```

### Correções automáticas de palavras
No arquivo `legendador.py`, a constante `DEFAULT_CORRECOES` guarda substituições padrão. Exemplo:
```python
DEFAULT_CORRECOES = {
    "seticismo": "ceticismo",
}
```
Você pode adicionar novas entradas nesse dicionário. Também é possível enviar correções adicionais ao chamar `legendar(..., correcoes={"palavra": "substituto"})`.

### Arquivo padrão
Quando nenhum arquivo é enviado, `legendar()` usa `oswaldo_porchat.mp4` (presente na pasta) como entrada e gera `oswaldo_porchat_legenda.srt`.

## Usando via linha de comando
Execute diretamente o script:
```bash
python legendador.py
```
Isso cria o arquivo `*_legenda.srt` correspondente ao vídeo padrão.

## Executando a interface Streamlit
Dentro da pasta `aula_fazer_teste` rode:
```bash
streamlit run main.py
```
A interface permite:
- Informar um contexto opcional para melhorar a transcrição.
- Fazer upload de arquivos `.mp4` ou `.mp3`.
- Visualizar a legenda gerada em SRT na tela.

## Implantação 24/7
Opções recomendadas:
- **Streamlit Community Cloud**: conecte este repositório, defina `main.py` como entry point e configure `OPENAI_API_KEY` em *Secrets*.
- **Render / Railway / Fly.io** (buildpack ou Docker): use o comando `streamlit run aula_fazer_teste/main.py --server.port $PORT --server.address 0.0.0.0` e exporte as variáveis de ambiente.
- **VPS/VM (AWS, Azure, GCP, DigitalOcean)**: instale Python, ffmpeg e configure o app para rodar em background (systemd, pm2 ou Docker). Mantenha a máquina ativa para atendimento 24 horas.

Garanta que arquivos necessários (`oswaldo_porchat.mp4`, etc.) estejam versionados ou disponíveis no ambiente de produção.

## Estrutura
```
.
├── legendador.py          # Lógica principal de conversão e transcrição
├── main.py                # Interface Streamlit
├── oswaldo_porchat.mp4    # Vídeo de exemplo
├── oswaldo_porchat_legenda.srt  # Exemplo gerado
├── pyaudioop.py           # Shim para compatibilizar pydub com Python 3.13
└── requirements.txt       # Dependências do projeto
```

## Próximos passos sugeridos
- Adicionar testes automatizados (por exemplo, mocks do Whisper) para validar ajustes sem consumir API.
- Criar um fluxo de logs para monitorar consumo da API em produção.
- Investigar cache/localização dos arquivos de saída quando vários uploads são processados simultaneamente.
