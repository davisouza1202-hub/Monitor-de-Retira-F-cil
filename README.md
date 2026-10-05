#  Monitor de Retira Fácil

Contagem regressiva para remessas de **retira fácil**: quando o cliente está
esperando no balcão e a separação precisa ser concluída em até **20 minutos**
(para remessas de até **400 kg**).

## O problema

No coletor usado na separação, o tempo restante de cada remessa não aparece.
O operador não sabe qual remessa está perto de estourar o prazo e acaba
priorizando sem ter essa informação.

## A solução

Um monitor de terminal que lê um CSV exportado do sistema e mostra, em tempo
real, as remessas pendentes ordenadas da mais urgente para a menos urgente:

| Situação | Quando |
|----------|--------|
| 🟢 NO PRAZO | mais de 10 min restantes |
| 🟡 ATENÇÃO  | entre 5 e 10 min |
| 🔴 CRÍTICA  | menos de 5 min |
| 🔴 ATRASADA | prazo estourado (tempo negativo) |

O monitor é executado diretamente no terminal do computador.

## Como usar

Requer Python 3.8+ e nenhuma biblioteca extra.

```bash
git clone https://github.com/SEU-USUARIO/monitor-retira-facil.git
cd monitor-retira-facil

python gerar_exemplo.py                 # cria dados fictícios para testar
python monitor.py dados/exemplo.csv     # abre o monitor (Ctrl+C para sair)
```

Opções:

```bash
python monitor.py arquivo.csv --limite-kg 400 --sla-min 20 --intervalo 1
python monitor.py arquivo.csv --uma-vez   # mostra uma vez e sai
```


O servidor mostra um endereço como `http://192.168.0.15:8000`. Com o coletor na
mesma rede Wi-Fi, abra esse endereço no navegador dele. A página exibe um card por
remessa, com tempo grande e colorido, e se atualiza sozinha (a contagem corre
a cada segundo e os dados são recarregados a cada 15 s).

- Se o Windows perguntar sobre o firewall, permita o acesso em rede privada.
- A página usa JavaScript simples para funcionar em navegadores antigos de coletor.
- Se a conexão cair, aparece um aviso vermelho e a contagem continua com o último dado.

## Formato do CSV

O arquivo precisa ter estas colunas (separador `;` ou `,`):

| Coluna | Exemplo | Observação |
|--------|---------|------------|
| remessa | 80000001 | número da remessa |
| tipo | RETIRA_FACIL | só esse tipo é monitorado (mude com `--tipo`) |
| peso_kg | 123,5 | aceita vírgula ou ponto |
| criada_em | 05/10/2026 14:30:00 | também aceita `2026-10-05 14:30:00` |
| status | pendente | `separado`, `concluido` e `cancelado` saem da lista |

O monitor relê o arquivo a cada atualização. Se o arquivo for substituído por
uma exportação nova, a tela já reflete os dados novos.

##  Privacidade

Nunca suba dados reais da empresa para o GitHub. A pasta `dados/` está no
`.gitignore` justamente para isso. Todos os exemplos deste repositório são fictícios.

## Limitações

- Não se conecta ao SAP: depende de um arquivo exportado e atualizado.
- Não aparece dentro da tela do Fiori; abre no navegador do coletor, em outra aba ou janela.
- Remessas acima do limite de peso ficam fora do monitor.
- A solução definitiva seria exibir o prazo no próprio coletor, o que exige
  uma customização feita pela equipe de TI/SAP. Este projeto serve como protótipo.

## Próximos passos

- [ ] Alerta sonoro quando uma remessa ficar crítica
- [ ] Versão web para o navegador do coletor
- [ ] Relatório diário: % de remessas atendidas dentro do prazo
- [ ] Testes automatizados com `pytest`

