"""
Avaliação da KlebIA com o Ragas.

Etapas (rodar de dentro da pasta backend/):
    python -m eval.run_ragas gerar --k 5     # roda a KlebIA no dataset e salva respostas + chunks
    python -m eval.run_ragas avaliar --k 5   # roda as métricas do Ragas sobre as respostas salvas

Opções úteis:
    --k 3            quantidade de chunks recuperados (padrão 5)
    --limite 2       usa só as N primeiras perguntas (para testar sem gastar)
    --juiz MODELO    modelo da OpenAI que dá as notas (padrão gpt-6-luna)
"""
import os
import sys
import json
import argparse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.chat import generate_answer
from core.models import get_embeddings_model
from core.vector_store import get_vector_store

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(EVAL_DIR, "dataset.json")

def get_paths(k):
    results_dir = os.path.join(EVAL_DIR, "resultados")
    os.makedirs(results_dir, exist_ok=True)
    return (
        os.path.join(results_dir, f"respostas_k{k}.json"),
        os.path.join(results_dir, f"resultado_k{k}.csv"),
    )

def load_dataset(limite):
    with open(DATASET_PATH, encoding="utf-8") as f:
        dataset = json.load(f)
    return dataset[:limite] if limite else dataset

def gerar(args):
    answers_path, _ = get_paths(args.k)
    dataset = load_dataset(args.limite)

    # Retomável: perguntas que já têm resposta salva não são geradas de novo
    saved = {}
    if os.path.exists(answers_path):
        with open(answers_path, encoding="utf-8") as f:
            saved = {s["user_input"]: s for s in json.load(f)}

    vector_store = get_vector_store(get_embeddings_model())
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": args.k})

    samples = []
    for i, item in enumerate(dataset, 1):
        if item["user_input"] in saved:
            print(f"[{i}/{len(dataset)}] já gerada, pulando")
            samples.append(saved[item["user_input"]])
            continue

        print(f"[{i}/{len(dataset)}] {item['user_input']}")
        response, contexts = generate_answer(item["user_input"], retriever)
        samples.append({**item, "retrieved_contexts": contexts, "response": response})

        # Salva a cada pergunta para não perder progresso se algo falhar
        with open(answers_path, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)

    print(f"\nRespostas salvas em {answers_path}")

def avaliar(args):
    from langchain_openai import ChatOpenAI
    from ragas import EvaluationDataset, RunConfig, evaluate
    from ragas.cost import get_token_usage_for_openai
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms.base import LangchainLLMWrapper
    from ragas.metrics import (
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
        ResponseRelevancy,
    )

    answers_path, result_path = get_paths(args.k)
    if not os.path.exists(answers_path):
        sys.exit(f"Não encontrei {answers_path}. Rode a etapa 'gerar' antes.")

    with open(answers_path, encoding="utf-8") as f:
        samples = json.load(f)
    if args.limite:
        samples = samples[:args.limite]

    # O Ragas descarta campos que não conhece, então a dificuldade é guardada à parte
    difficulties = [s.get("dificuldade") for s in samples]
    dataset = EvaluationDataset.from_list(samples)

    # bypass_temperature: modelos de raciocínio recusam o parâmetro temperature que o Ragas envia
    # bypass_n: o modelo ignora o pedido de n respostas numa requisição, então o Ragas faz n requisições
    judge = LangchainLLMWrapper(
        ChatOpenAI(model=args.juiz, reasoning_effort="low"),
        bypass_temperature=True,
        bypass_n=True,
    )
    embeddings = LangchainEmbeddingsWrapper(get_embeddings_model())

    result = evaluate(
        dataset=dataset,
        metrics=[
            Faithfulness(),
            ResponseRelevancy(),
            LLMContextPrecisionWithReference(),
            LLMContextRecall(),
        ],
        llm=judge,
        embeddings=embeddings,
        run_config=RunConfig(max_workers=4, max_retries=5, timeout=180),
        token_usage_parser=get_token_usage_for_openai,
    )

    df = result.to_pandas()
    df.insert(0, "dificuldade", difficulties)
    df.to_csv(result_path, index=False)

    metrics = ["faithfulness", "answer_relevancy", "llm_context_precision_with_reference", "context_recall"]
    metrics = [m for m in metrics if m in df.columns]

    print("\n=== Média geral ===")
    print(df[metrics].mean().round(3).to_string())
    print("\n=== Média por dificuldade ===")
    print(df.groupby("dificuldade")[metrics].mean().round(3).reindex(["facil", "medio", "dificil"]).dropna(how="all").to_string())

    nan_count = int(df[metrics].isna().sum().sum())
    if nan_count:
        print(f"\nAtenção: {nan_count} nota(s) ficaram NaN (o juiz não devolveu um formato válido).")

    usage = result.total_tokens()
    print(f"\nTokens do juiz: {usage.input_tokens} de entrada, {usage.output_tokens} de saída")
    print(f"Resultado por pergunta salvo em {result_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avaliação da KlebIA com o Ragas")
    parser.add_argument("etapa", choices=["gerar", "avaliar"])
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--limite", type=int, default=None)
    parser.add_argument("--juiz", default="gpt-6-luna")
    args = parser.parse_args()

    gerar(args) if args.etapa == "gerar" else avaliar(args)
