import os
import json

def load_all_news(output_dir, date_filter=None):
    all_news = []
    for fname in os.listdir(output_dir):
        if fname.endswith('.json') and fname != f'relatorio_unico_deduplicado.json{datetime.now()}':
            if date_filter:
                # Espera-se que a data esteja no formato 'DD-MM-YYYY' no nome do arquivo
                if date_filter not in fname:
                    continue
            fpath = os.path.join(output_dir, fname)
            try:
                with open(fpath, encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_news.extend(data)
            except Exception:
                continue
    return all_news

def deduplicate_news(news_list):
    unique = {}
    for n in news_list:
        key = (
            str(n.get('titulo', '') or '').strip().lower(),
            str(n.get('municipio', '') or '').strip().lower(),
            str(n.get('tipo_investimento', '') or '').strip().lower()
        )
        if key not in unique:
            unique[key] = n
        else:
            # Opcional: juntar links/fontes se quiser consolidar
            if 'link' in n and 'link' in unique[key]:
                if isinstance(unique[key]['link'], list):
                    if n['link'] not in unique[key]['link']:
                        unique[key]['link'].append(n['link'])
                else:
                    if n['link'] != unique[key]['link']:
                        unique[key]['link'] = [unique[key]['link'], n['link']]
    return list(unique.values())

if __name__ == "__main__":
    from datetime import datetime

    print("Você deseja analisar:")
    print("1 - Todas as notícias")
    print("2 - Apenas as notícias do dia")
    escolha = input("Digite 1 ou 2: ").strip()

    output_dir = os.path.dirname(os.path.abspath(__file__))
    date_filter = None

    if escolha == "2":
        date_filter = datetime.now().strftime('%d-%m-%Y')
        print(f"Analisando apenas notícias do dia {date_filter}...")
        all_news = load_all_news(output_dir, date_filter=date_filter)
        deduped = deduplicate_news(all_news)
        print(f"Total notícias únicas do dia: {len(deduped)}")
        gerar_json = input("Você deseja gerar um arquivo JSON único com todas as notícias do dia? (s/n): ").strip().lower()
        if gerar_json == "s":
            with open(os.path.join(output_dir, "noticias_unicas_do_dia.json"), "w", encoding="utf-8") as f:
                json.dump(deduped, f, ensure_ascii=False, indent=2)
            print("Arquivo 'noticias_unicas_do_dia.json' gerado com sucesso.")
    else:
        print("Analisando todas as notícias...")
        all_news = load_all_news(output_dir, date_filter=None)
        deduped = deduplicate_news(all_news)
        with open(os.path.join(output_dir, "relatorio_unico_deduplicado.json"), "w", encoding="utf-8") as f:
            json.dump(deduped, f, ensure_ascii=False, indent=2)
        print(f"Total notícias únicas: {len(deduped)}")
