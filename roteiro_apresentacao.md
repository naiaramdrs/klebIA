# Roteiro: Seminário V&V, Ragas

**Tempo-alvo: ~18 min** (sobram ~2 min de folga dentro dos 20).
Sugestão de divisão em 4 blocos, um por pessoa. Os tempos são aproximados e as falas são guias, não precisa decorar.

| Bloco | Slides | Tema | Tempo |
|---|---|---|---|
| 1 | 1–5 | O que é, por que usar, como avalia | ~4:50 |
| 2 | 6–8 | Métricas e como usar | ~3:35 |
| 3 | 9–12 | Experimento na KlebIA (parte 1) | ~4:10 |
| 4 | 13–15 | Experimento (parte 2), análise e V&V | ~4:05 |

---

## Bloco 1

### Slide 1: Capa (0:20)
> Boa tarde! Nós somos [nomes] e vamos apresentar o Ragas, uma ferramenta para avaliar aplicações que usam LLMs.

### Slide 2: O que é o Ragas? (1:00)
> O Ragas, de *Retrieval-Augmented Generation Assessment*, é um framework open source para testar e avaliar aplicações com LLMs, principalmente sistemas RAG. RAG é quando o modelo primeiro busca documentos numa base e depois gera a resposta com base neles.
>
> As principais funcionalidades são três: **métricas automáticas** para dar nota às respostas, **geração de dados de teste sintéticos** a partir dos documentos e **monitoramento em produção**. No nosso experimento usamos as métricas.

### Slide 3: Por que utilizar? (1:00)
> O problema que motiva a ferramenta é que um sistema RAG pode errar sem dar nenhum sinal. Mesmo quando a busca falha ou o modelo inventa informação, a resposta sai bem escrita e convincente.
>
> Então os objetivos são: **medir a alucinação**, **avaliar se a busca trouxe os documentos certos** e **comparar versões** do sistema, por exemplo, quando trocamos o modelo ou o número de documentos recuperados.

### Slide 4: O que é avaliado? (1:15)
> Para cada pergunta, o Ragas olha separadamente as duas etapas do RAG. Na **recuperação**, a pergunta é: os documentos recuperados são relevantes, ou seja, ele recuperou o contexto certo? Na **geração**, a pergunta é: a resposta foi fiel a esse contexto?
>
> Cada métrica devolve uma nota de 0 a 1. Separar as etapas é o que permite saber *onde* está o defeito.

### Slide 5: Quem avalia? (1:15)
> Quem dá as notas é outro LLM, uma técnica chamada **LLM-as-a-judge**. Esse modelo juiz recebe a pergunta, o contexto recuperado e a resposta, e devolve a nota.
>
> Um ponto importante é que isso é **não determinístico**: o juiz é um LLM, então ele pode errar e as notas podem variar um pouco de uma execução para outra. Vamos voltar a isso nas limitações.

---

## Bloco 2

### Slide 6: Métricas (1:45)
> O Ragas tem várias métricas. **Escolhemos estas quatro para o nosso experimento**, duas para cada etapa.
>
> Na recuperação:
> - **Context Precision**: os trechos relevantes estão no topo da lista recuperada?
> - **Context Recall**: o contexto recuperado tem tudo o que é preciso para responder?
>
> Na geração:
> - **Faithfulness**: a resposta está baseada no contexto, ou o modelo inventou?
> - **Answer Relevancy**: a resposta fala do que foi perguntado?
>
> Precision e Recall usam a resposta de referência do dataset. Faithfulness e Relevancy não precisam dela.

### Slide 7: Métricas: Faithfulness (1:00)
> Cada métrica tem sua lógica. No Faithfulness, o juiz quebra a resposta em afirmações e verifica quantas aparecem no contexto. Se a resposta faz 3 afirmações e só 2 estão nos documentos, a nota é 2 ÷ 3, ou 0,67.

### Slide 8: Como usar? (0:50)
> Usar é simples, são quatro passos:
> 1. instalar com `pip install ragas`;
> 2. montar o dataset de perguntas com as respostas de referência;
> 3. no script, escolher as métricas e o LLM juiz;
> 4. chamar o `evaluate()` e receber uma nota de 0 a 1 por métrica.

---

## Bloco 3

### Slide 9: Experimento (1:30)
> Para testar na prática, aplicamos o Ragas na **KlebIA**, um chatbot RAG sobre o curso de Ciência da Computação da UFCG, **que desenvolvemos na disciplina de PLN**. Ele usa o **gpt-6-luna** para gerar as respostas e o **text-embedding-3-small** para buscar os documentos.
>
> Montamos um dataset com **20 perguntas**. Estas três são exemplos. Para cada pergunta, colocamos o **nível de dificuldade** e uma **resposta de referência**, que é comparada com a resposta do modelo.

### Slide 10: Script (0:50)
> No script, a chamada principal é o `evaluate`: passamos o dataset, as quatro métricas, o LLM juiz e o modelo de embeddings. Ele devolve uma nota por métrica e por pergunta.
>
> Na média das 20 perguntas, ficamos com:
> - Faithfulness 0,90;
> - Answer Relevancy 0,79;
> - Context Precision 0,49;
> - Context Recall 0,70.
>
> O ponto mais fraco foi a busca. Agora vamos ver três casos.

### Slide 11: Resultado 1, “Quantos períodos dura o curso?” (1:20)
> A resposta certa é 9 períodos, mas a KlebIA disse **8**.
>
> O que aconteceu foi uma **alucinação**: nenhum trecho recuperado dizia quantos períodos o curso tem, e o modelo inferiu o 8. Por isso **Faithfulness e Context Recall zeram juntos**. A busca falhou e o modelo inventou.
>
> Curiosidade: o Answer Relevancy deu 0,81 mesmo com a resposta errada. Essa métrica só mede se a resposta *fala do assunto* da pergunta, não se está correta.

### Slide 12: Resultado 2, “Quantos alunos entram por ano?” (1:20)
> A resposta certa é 180 vagas por ano, mas a KlebIA respondeu “120 novos profissionais por ano”.
>
> Aqui o **Faithfulness deu 1,00**, porque a frase estava, de fato, no documento recuperado. O problema é que o documento era sobre **formandos, não sobre vagas**. Ou seja, **Faithfulness 1 não garante resposta certa**. Quem denuncia a falha é o **Context Recall, que zerou**: a busca não trouxe a informação necessária.

---

## Bloco 4

### Slide 13: Resultado 3, “Horas-aula do 1º + 4º período” (1:40)
> Neste caso a resposta está **correta**: 300 + 360 = 660 horas-aula. A busca trouxe os dois períodos, então o **Recall deu 1,0**. Mesmo assim, a **Context Precision deu 0**.
>
> Isso acontece porque a Context Precision **julga cada trecho isoladamente**, e nenhum trecho sozinho leva a “660 horas”: a resposta depende de juntar dois. É uma **limitação conhecida** da métrica em perguntas que dependem de vários trechos. Por isso não dá para olhar uma nota sozinha.

### Slide 14: Análise da ferramenta (2:30)
> **Pontos fortes:**
> - avalia texto livre com notas de 0 a 1, sem exigir resposta exata;
> - separa busca e geração, mostrando onde está o defeito, como vimos nos três casos;
> - vira um teste de regressão: o mesmo dataset roda a cada mudança;
> - é fácil de montar, com um dataset em JSON e poucas linhas de Python.
>
> **Limitações:**
> - cada nota custa chamadas de LLM;
> - o juiz também pode errar e as notas variam entre execuções;
> - as métricas têm pontos cegos, como a Precision 0 no caso das 660 horas;
> - a qualidade depende de referências bem escritas.
>
> **Onde o Ragas entra em V&V:** ele cobre os dois lados.
> - **Verificação** (“construímos o produto corretamente?”): o Faithfulness verifica se a resposta obedece aos documentos, e a Context Precision e o Context Recall verificam se o componente de busca faz o que deveria.
> - **Validação** (“construímos o produto certo?”): o Answer Relevancy e a comparação com a referência dizem se a resposta atende ao que o estudante precisa.
>
> *(Opcional, se sobrar tempo, ~20 s)* Uma ferramenta parecida é o **DeepEval**, que tem métricas de RAG semelhantes, mas trata cada pergunta como um teste que passa ou falha, no estilo pytest. Escolhemos o Ragas pelo foco em RAG e por gerar uma tabela de notas por pergunta, que facilita a análise.

### Slide 15: Obrigada! (0:15)
> É isso, obrigada! Ficamos à disposição para perguntas.

---

## Possíveis perguntas da turma
- **“Por que o Answer Relevancy não pega resposta errada?”** O juiz gera perguntas a partir da resposta e compara, por embeddings, com a pergunta original. Ele mede o assunto, não a correção.
- **“Dá para confiar no juiz?”** Não cegamente. As notas variam entre execuções, então vale rodar mais de uma vez e olhar os casos individuais, não só a média.
- **“Quanto custou?”** Cada pergunta gera várias chamadas ao juiz, porque são quatro métricas e o Relevancy faz 3 gerações. Para 20 perguntas o custo é baixo, mas cresce com o dataset.
