from flask import Flask, render_template, request, redirect, url_for
import os
import codecs
from dotenv import dotenv_values
from markdown import Markdown
import glob
from datetime import datetime

app = Flask(__name__)

# Carregar configuração do ambiente
config = dotenv_values(".env.dev") if os.getenv('FLASK_ENV') == 'development' else dotenv_values(".env")

app.secret_key = '!BzsArrd#'  # Altere para um segredo seguro em produção

# Converte NO_GA para um booleano
NO_GA = config.get('NO_GA', "False").lower() in ["true", "1", "yes"]

@app.context_processor
def inject_env():
    return dict(no_ga=NO_GA)

def get_posts(language, tag_filter=None):
    path = f"./mdposts/{language}/*.md"
    meta_list = []

    for file in glob.glob(path):
        html = codecs.open(file, mode='r', encoding="UTF-8").read()
        md = Markdown(extensions=['meta'])
        md.convert(html)

        # Garante que tags existam e divide corretamente
        if 'tags' in md.Meta:
            md.Meta['tags'] = [tag.strip() for tag in md.Meta['tags'][0].split(',')]
        else:
            md.Meta['tags'] = []

        # Filtra por tag, se necessário
        if tag_filter and tag_filter not in md.Meta['tags']:
            continue

        md.Meta['file'] = os.path.basename(file)
        meta_list.append(md.Meta)

    return sorted(meta_list, key=lambda meta: datetime.strptime(meta['date'][0], '%d.%m.%Y'), reverse=True)

@app.route('/')
def landing(lang='pt-br'):
    """ Página inicial da landing page """
    if lang not in ['pt-br', 'en']:
        return redirect(url_for('landing', lang='pt-br'))
    return render_template(f'landing_{lang}.html', metainfos=get_posts(lang), lang=lang)


if __name__ == "__main__":
    app.run(debug=True)
