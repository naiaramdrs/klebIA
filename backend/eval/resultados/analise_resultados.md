# Análise dos resultados: Ragas na KlebIA

**Configuração:** 20 perguntas (7 fáceis, 7 médias, 6 difíceis), k = 5 chunks recuperados, LLM da KlebIA `gpt-6-luna`, embeddings `text-embedding-3-small`, juiz `gpt-6-luna`.
**Fonte dos dados:** `backend/eval/resultados/resultado_k5.csv` (notas) e `respostas_k5.json` (respostas e chunks).

Legenda das notas: **F** = Faithfulness, **AR** = Answer Relevancy, **CP** = Context Precision, **CR** = Context Recall.

---

## 1. Visão geral

| Grupo | F | AR | CP | CR |
|---|---|---|---|---|
| **Geral (20)** | **0,90** | **0,79** | **0,49** | **0,70** |
| Fácil (7) | 0,86 | 0,92 | 0,53 | 0,86 |
| Médio (7) | 1,00 | 0,80 | 0,65 | 0,79 |
| Difícil (6) | 0,82 | 0,64 | 0,27 | 0,42 |

**Corretude das respostas** (avaliada por nós, comparando com a referência):

| Situação | Qtd. | Perguntas |
|---|---|---|
| Correta | 15 | 1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 20 |
| Parcial | 1 | 9 |
| Errada | 3 | 2, 15, 18 |
| Não respondeu (fallback) | 1 | 19 |

**Principais conclusões**
- **O gargalo é a busca, não a geração.** Faithfulness alto (0,90) mostra que o modelo quase sempre se apoia no que recebe. Já Precision (0,49) e Recall (0,70) são as notas mais baixas.
- **Todas as 4 respostas erradas ou sem resposta tiveram Context Recall = 0.** Ou seja, a busca não trouxe a informação e a geração não teve como acertar. O Recall foi a métrica que melhor previu erro.
- **A dificuldade pesa principalmente na busca:** o Recall cai de 0,86 (fácil) para 0,42 (difícil).
- **Faithfulness alto não é sinônimo de resposta certa** (perguntas 15 e 18), e **Answer Relevancy não mede corretude** (pergunta 2 tem 0,81 e está errada).
- **Context Precision baixa nem sempre é problema:** em várias respostas corretas ela ficou baixa só porque o chunk certo veio em 4º ou 5º lugar (1, 13), ou porque a resposta depende de juntar vários chunks (16).

---

## 2. Análise pergunta por pergunta

### Fáceis

#### 1. Em que ano foi criado o curso de Ciência da Computação da UFCG?
**F 1,00 · AR 0,94 · CP 0,20 · CR 1,00 · ✅ Correta**
- **Resposta:** “...foi criado em 1976.”
- O chunk com a informação veio em **5º (último) lugar**, depois de calendários e histórico. Por isso a Precision foi 0,20. O Recall é 1,0 porque a informação estava lá, e a resposta saiu certa.
- **Lição:** Precision baixa com Recall alto indica que a busca acha, mas ordena mal.

#### 2. Quantos períodos dura o curso de Ciência da Computação?
**F 0,00 · AR 0,81 · CP 0,00 · CR 0,00 · ❌ Errada (alucinação)**
- **Resposta:** “8 períodos” (o correto é 9).
- Os 5 chunks eram os detalhes dos Períodos I, II, V, VII e VIII. Nenhum dizia a duração total, e o modelo **inferiu “8”** a partir do maior período que viu.
- O chunk com “A duração do curso é de 9 períodos” **existe na base** (ele apareceu na pergunta 8), mas perdeu na similaridade para os chunks de cada período.
- Faithfulness e Recall zeram juntos, o sinal clássico de alucinação por falta de contexto. O AR de 0,81 mostra que a métrica só mede se a resposta é **sobre** o assunto, não se está certa.

#### 3. Quem é a secretária da coordenação de graduação?
**F 1,00 · AR 0,98 · CP 0,58 · CR 1,00 · ✅ Correta**
- **Resposta:** “...Klébia Larubia Soares dos Santos.”
- Resposta exata. A Precision intermediária vem de chunks da pós-graduação misturados no topo da lista.

#### 4. Qual o valor da bolsa de monitoria?
**F 1,00 · AR 0,99 · CP 0,70 · CR 1,00 · ✅ Correta**
- **Resposta:** “R$ 300,00.”
- O chunk certo veio em **1º lugar**. Ficou de fora o detalhe “desde 2013.1”, que não altera a corretude.

#### 5. Qual foi o primeiro computador instalado na UFCG?
**F 1,00 · AR 0,94 · CP 0,83 · CR 1,00 · ✅ Correta**
- **Resposta:** “IBM 1130, em 1968... primeiro em universidades do Norte e Nordeste.”
- Um dos melhores casos: a busca trouxe os chunks de história no topo e a resposta cobre toda a referência.

#### 6. Quem é o tutor atual do PET Computação?
**F 1,00 · AR 0,90 · CP 0,50 · CR 1,00 · ✅ Correta**
- **Resposta:** “...professor Marcelo Barros.”
- Todos os chunks falavam do PET, mas só alguns citavam o tutor, por isso a Precision ficou em 0,50.

#### 7. Quem leciona a disciplina Programação para Web?
**F 1,00 · AR 0,90 · CP 0,87 · CR 1,00 · ✅ Correta**
- **Resposta:** “...Turma 01, é lecionada por Demetrio Gomes Mestre.”
- O chunk exato (`TECC (PROGRAMAÇÃO PARA WEB) Turma 01`) veio em 1º lugar. Perguntas com nome próprio de disciplina funcionam bem na busca semântica.

### Médias

#### 8. Qual o e-mail e o telefone da secretaria do curso de graduação?
**F 1,00 · AR 1,00 · CP 1,00 · CR 1,00 · ✅ Correta**
- **Resposta:** “secgrad@computacao.ufcg.edu.br ... +55 (83) 2101-1027.”
- **Único caso com nota máxima em todas as métricas.** É um bom exemplo de “caminho feliz” para mostrar.

#### 9. Quantos créditos de atividades complementares eu preciso para me formar?
**F 1,00 · AR 0,73 · CP 0,33 · CR 0,50 · ⚠️ Parcial**
- **Resposta:** currículo 2017 = 22 créditos (330 h); currículo 2023 = 30 créditos (450 h).
- Os números estão certos, mas faltou dizer que, no currículo 2023, **22 desses créditos precisam ser de extensão**. Os chunks não traziam essa regra, por isso o Recall foi 0,50: metade da referência estava coberta.
- A resposta acrescentou como pedir aproveitamento (processo no SEI), o que é fiel ao contexto mas desvia um pouco da pergunta, e o AR caiu para 0,73.

#### 10. Posso receber bolsa de um projeto e da monitoria ao mesmo tempo?
**F 1,00 · AR 0,80 · CP 0,75 · CR 1,00 · ✅ Correta**
- **Resposta:** “Não... Porém, quem recebe bolsa de projeto pode atuar na monitoria como voluntário.”
- A resposta é completa e bate com a referência. O AR fica abaixo de 1 porque perguntas de sim/não geram perguntas reformuladas um pouco diferentes da original.

#### 11. Como funciona o TCC do curso?
**F 1,00 · AR 0,67 · CP 1,00 · CR 1,00 · ✅ Correta**
- **Resposta:** obrigatório, individual, com orientador, regido pela Resolução 01/2019, publicado na Biblioteca Digital, mais 60 h, 4 créditos e pré-requisitos.
- Busca perfeita (CP e CR = 1). O AR de 0,67 é **penalidade por informação extra**: carga horária e pré-requisitos vieram do chunk do Período IX. São corretos e fiéis, mas fazem o juiz gerar perguntas mais distantes da original.

#### 12. Quais são as disciplinas do primeiro período?
**F 1,00 · AR 0,56 · CP 0,50 · CR 1,00 · ✅ Correta**
- **Resposta:** lista as 5 disciplinas, 300 h e 20 créditos, mais a observação de que P1 e LP1 são co-requisitos.
- A resposta está perfeita, mas tem o **AR mais baixo entre as respostas corretas**. O motivo é o mesmo da 11: a observação extra sobre co-requisitos e as siglas desviam as perguntas geradas pelo juiz. Também mostra a **variabilidade do juiz**: uma lista bem formatada recebeu nota de “meio relevante”.

#### 13. Quais os pré-requisitos de Estruturas de Dados e Algoritmos?
**F 1,00 · AR 0,87 · CP 0,20 · CR 1,00 · ✅ Correta**
- **Resposta:** pré-requisitos Programação II e LP2; co-requisito LEDA.
- O chunk certo (Período III) veio em **5º lugar**, atrás de chunks sobre arquitetura e algoritmos avançados que só compartilham palavras-chave. Por isso a CP foi 0,20, o mesmo padrão da pergunta 1.

#### 14. Quais são as linhas de pesquisa do Programa de Pós-Graduação em Ciência da Computação?
**F 1,00 · AR 0,94 · CP 0,75 · CR 0,00 · ✅ Correta**
- **Resposta:** Metodologia e Técnicas da Computação; Sistemas de Computação.
- **Caso curioso: resposta correta com Recall 0.** Os chunks traziam as linhas de pesquisa e a área de concentração, mas não o detalhe “iniciado em 1973”. A referência foi escrita como **uma única frase**, e o Recall avalia frase por frase. Com um detalhe faltando, a frase inteira foi marcada como não coberta.
- **Lição:** o jeito de escrever a referência afeta a nota. Referências com uma ideia por frase dão um Recall mais justo.

### Difíceis

#### 15. Trabalhei 450 horas numa empresa. Quantos créditos complementares consigo aproveitar?
**F 0,57 · AR 0,68 · CP 0,00 · CR 0,00 · ❌ Errada**
- **Resposta:** “até 7 créditos”, usando a regra de **estágio não obrigatório** (1 crédito a cada 60 h).
- O correto é **6 créditos**, pela regra de **atividade profissional** (1 crédito a cada 75 h). O chunk dessa regra não foi recuperado. Veio o do estágio, que é parecido, e o modelo aplicou a regra errada.
- O Faithfulness de 0,57 reflete que a regra dos 60 h estava no contexto, mas o arredondamento “7,5 → 7” e a suposição de que “trabalho = estágio” foram inferência do modelo.
- É uma pergunta que exige **raciocínio + regra específica**, o pior cenário para RAG.

#### 16. Quantas horas-aula somam o primeiro e o quarto período juntos?
**F 1,00 · AR 0,95 · CP 0,00 · CR 1,00 · ✅ Correta**
- **Resposta:** 300 + 360 = 660 horas-aula.
- Os chunks do Período IV (1º lugar) e do Período I (4º) foram recuperados, o Recall foi 1,0 e a resposta está certa. Mesmo assim, a **Precision foi 0**.
- Isso acontece porque a Context Precision julga **cada chunk isoladamente**, e nenhum chunk sozinho leva a “660 horas”. É um **ponto cego da métrica** em perguntas que dependem de juntar informações.

#### 17. Qual laboratório de ensino tem mais computadores, e quantos a mais que o LCC1?
**F 1,00 · AR 0,78 · CP 1,00 · CR 1,00 · ✅ Correta**
- **Resposta:** “O LCC3... são 120, ou seja, 65 a mais que o LCC1, que possui 55.”
- É o **contraponto da 16**. Também é uma conta (120 − 55), mas os dois números estavam **no mesmo chunk**, e aí a Precision é 1,0. A diferença entre os dois casos é só como a informação está dividida na base.

#### 18. Quantos alunos entram no curso por ano?
**F 1,00 · AR 0,65 · CP 0,00 · CR 0,00 · ❌ Errada**
- **Resposta:** “...forma aproximadamente 120 novos profissionais por ano.” O correto são 180 vagas por ano.
- A busca trouxe vagas do **mestrado** (44), um chunk histórico com “forma 120 profissionais por ano” e chunks de disciplinas. Nenhum falava das vagas da graduação.
- A KlebIA respondeu algo **fiel ao chunk** (F = 1,00), mas sobre **outra coisa**: formandos em vez de ingressantes. **Faithfulness 1 não garante resposta certa.** Quem denuncia a falha é o Recall 0.

#### 19. Com quem eu falo sobre assuntos da graduação no curso?
**F 0,33 · AR 0,00 · CP 0,00 · CR 0,00 · 🚫 Não respondeu**
- **Resposta:** “Desculpe, não tenho informações suficientes... Consulte o site oficial...”
- Todos os 5 chunks eram de **procedimentos da pós-graduação**. A palavra “graduação” casou com “pós-graduação” na busca, e o chunk da Coordenação de Graduação (que existe, como mostram as perguntas 3 e 8) não veio.
- A KlebIA aplicou o **fallback** previsto no prompt: não inventou nada, mas também não ajudou.
- O Ragas dá **AR = 0 para respostas evasivas** (noncommittal). Essa é a pior nota de relevância do dataset.
- O F de 0,33 aparece porque a frase “não tenho informações” não é verificável no contexto.
- **Lição:** perguntas vagas, sem palavras-chave fortes, são as mais difíceis para a busca.

#### 20. Se eu quisesse entrar no mestrado em 2025.1, ainda daria para me inscrever no dia 10 de novembro de 2024?
**F 1,00 · AR 0,76 · CP 0,64 · CR 0,50 · ✅ Correta**
- **Resposta:** “Não. ...inscrições de 16 de outubro a 8 de novembro de 2024. Portanto, em 10 de novembro o prazo já teria encerrado.”
- O raciocínio sobre datas está certo e fiel ao contexto. O Recall de 0,50 vem do detalhe “às 23h59”, que estava na referência mas não nos chunks, o mesmo efeito da pergunta 14 em menor grau.

---

## 3. Padrões encontrados

| Padrão | Perguntas | O que as métricas mostram |
|---|---|---|
| **Alucinação por falta de contexto** | 2 | F = 0 e CR = 0 juntos |
| **Fiel ao chunk errado** | 15, 18 | F alto, CR = 0, resposta errada |
| **Fallback (não respondeu)** | 19 | AR = 0, CR = 0 |
| **Chunk certo mal posicionado** | 1, 13 | CP = 0,20 com CR = 1 e resposta certa |
| **Resposta depende de vários chunks** | 16 | CP = 0 com CR = 1 e resposta certa |
| **Excesso de informação na resposta** | 9, 11, 12 | AR cai (0,56–0,73) mesmo com resposta certa |
| **Referência escrita numa frase só** | 14, 20 | CR cai mesmo com resposta certa |
| **Caminho feliz** | 5, 7, 8, 17 | Todas as notas altas |

## 4. O que melhorar na KlebIA (sugestões a partir dos dados)
1. **Busca primeiro:** os 4 casos de erro vêm de Recall 0. Opções:
   - aumentar o k;
   - usar busca híbrida (palavra-chave + semântica) para casos como “graduação” × “pós-graduação”;
   - fazer reranking dos chunks.
2. **Chunks de resumo:** criar um chunk com dados gerais do curso (duração, vagas, coordenação) ajudaria as perguntas 2, 18 e 19.
3. **Prompt:** pedir respostas mais diretas, sem informação extra, subiria o AR nas perguntas 11 e 12. Pedir para não inferir números ausentes evitaria o “8 períodos”.

## 5. O que melhorar na avaliação
1. **Referências com uma ideia por frase**, para o Recall não zerar por um detalhe (pergunta 14).
2. **Rodar mais de uma vez** e comparar, porque o juiz é não determinístico (o AR de 0,56 na pergunta 12 é suspeito).
3. **Não olhar uma métrica sozinha:** Faithfulness 1 com Recall 0 é um alerta (pergunta 18), e Precision 0 com Recall 1 pode ser falso alarme (pergunta 16).
