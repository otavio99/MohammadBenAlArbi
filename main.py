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
@app.route('/<lang>/')
def landing(lang='pt-br'):
    """ Página inicial da landing page """
    if lang not in ['pt-br', 'en']:
        return redirect(url_for('landing', lang='pt-br'))
    return render_template(f'landing_{lang}.html', metainfos=get_posts(lang), lang=lang)

@app.route("/<lang>/blog")
def blog(lang='pt-br'):
    """ Página principal do blog com filtro por tag """
    if lang not in ['pt-br', 'en']:
        return redirect(url_for('blog', lang='pt-br'))

    tag_filter = request.args.get('tag')
    posts = get_posts(lang, tag_filter)
    
    return render_template("blog_home.html", metainfos=posts, lang=lang, selected_tag=tag_filter)

@app.route("/<lang>/post/<path>")
def post(lang, path):
    """ Página individual de um post """
    if lang not in ['pt-br', 'en']:
        return redirect(url_for('landing', lang='pt-br'))
    
    post_path = f"./mdposts/{lang}/{path}"
    content = ""

    for file in glob.glob(post_path):
        content = codecs.open(file, mode='r', encoding="UTF-8").read()
        content = content.replace("$base", request.url_root)
    
    md = Markdown(extensions=['meta'])
    html = md.convert(content)

    # Garantir que as tags sejam tratadas corretamente
    tags = md.Meta.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    # Garante que as tags sejam uma lista separada corretamente
    if 'tags' in md.Meta:
        md.Meta['tags'] = [tag.strip() for tag in md.Meta['tags'][0].split(',')]
    else:
        md.Meta['tags'] = []
    
    return render_template("post.html", content=html, metainfos=md.Meta, lang=lang)

if __name__ == "__main__":
    app.run(debug=True)
