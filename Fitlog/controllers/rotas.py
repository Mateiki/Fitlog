import json
from bottle import route, template, static_file, redirect, request, TEMPLATE_PATH
TEMPLATE_PATH.insert(0, './views/')
from models.treino import Treino, Exercicio
from models.usuario import Usuario

# --- ROTAS GERAIS ---
@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static/')

@route('/')
def index():
    return template('apresentacao.html')

@route('/acesso_negado')
def acesso_negado_page():
    return template('acesso_negado.html')

# --- ROTAS DE AUTENTICAÇÃO E CONTA ---
@route('/cadastro', method=['GET', 'POST'])
def cadastro_page():
    if request.method == 'POST':
        Usuario.create(
            nome=request.forms.get('nome'),
            email=request.forms.get('email'),
            senha=request.forms.get('senha')
        )
        return redirect('/login')
    return template('cadastro.html', error=None)

@route('/login', method=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.forms.get('email')
        senha = request.forms.get('senha')
        usuario = Usuario.find_by_email(email)
        if usuario and usuario.check_password(senha):
            s = request.environ.get('beaker.session')
            s['user_id'] = usuario.id
            s.save()
            return redirect('/home')
        return template('login.html', error="E-mail ou senha inválidos.")
    return template('login.html', error=None)

@route('/logout')
def logout():
    s = request.environ.get('beaker.session')
    s.delete()
    return redirect('/login')

@route('/informacoes')
def informacoes_page():
    s = request.environ.get('beaker.session')
    if 'user_id' not in s: return redirect('/login')
    usuario = Usuario.find_by_id(s['user_id'])
    if not usuario:
        s.delete()
        return redirect('/login')
    success_msg = request.query.get('success')
    error_msg = request.query.get('error')
    return template('informacoes.html', usuario=usuario, success=success_msg, error=error_msg)

# ROTA PARA ATUALIZAR NOME
@route('/usuario/atualizar/nome', method='POST')
def atualizar_nome():
    s = request.environ.get('beaker.session')
    if 'user_id' not in s: return redirect('/login')
    novo_nome = request.forms.get('novo_nome')
    if novo_nome:
        Usuario.update_nome(s['user_id'], novo_nome)
        return redirect('/informacoes?success=Nome alterado com sucesso!')
    return redirect('/informacoes?error=Ocorreu um erro ao alterar o nome.')

# ROTA PARA ATUALIZAR SENHA 
@route('/usuario/atualizar/senha', method='POST')
def atualizar_senha():
    s = request.environ.get('beaker.session')
    if 'user_id' not in s: return redirect('/login')
    senha_antiga = request.forms.get('senha_antiga')
    nova_senha = request.forms.get('nova_senha')
    usuario = Usuario.find_by_id(s['user_id'])
    if not usuario or not usuario.check_password(senha_antiga):
        return redirect('/informacoes?error=A senha atual está incorreta.')
    usuario.update_senha(nova_senha)
    return redirect('/informacoes?success=Senha alterada com sucesso!')

# ROTA PARA DELETAR CONTA 
@route('/usuario/deletar', method='POST')
def deletar_conta():
    s = request.environ.get('beaker.session')
    user_id = s.get('user_id')
    if not user_id: return redirect('/login')
    Usuario.delete(user_id)
    s.delete()
    return redirect('/')

# --- ROTAS PRINCIPAIS DA APLICAÇÃO (TREINOS E EXERCÍCIOS) ---
@route('/home')
def home_page():
    s = request.environ.get('beaker.session')
    user_id = s.get('user_id')
    if not user_id:
        return redirect('/login')
    
    usuario = Usuario.find_by_id(user_id)
    if not usuario:
        s.delete()
        return redirect('/login')

    treinos_do_usuario = usuario.get_treinos()
    return template('home.html', nome=usuario.nome, treinos=treinos_do_usuario)

@route('/treinos/criar', method='POST')
def criar_treino():
    s = request.environ.get('beaker.session')
    user_id = s.get('user_id')
    if not user_id: return redirect('/login')
    
    nome_treino = request.forms.get('nome_treino')
    if nome_treino:
        Treino.create(nome=nome_treino, usuario_id=user_id)
    return redirect('/home')

# ROTA DE EDITAR TREINO
@route('/treinos/editar/<treino_id:int>', method='POST')
def editar_treino(treino_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s:
        return redirect('/login')
    
    novo_nome = request.forms.get('novo_nome_treino')
    if novo_nome:
        Treino.update_nome(treino_id, novo_nome)
    return redirect('/home')

# ROTA DE DELETAR TREINO
@route('/treinos/deletar/<treino_id:int>', method='POST')
def deletar_treino(treino_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s:
        return redirect('/login')
    
    Treino.delete(treino_id)
    return redirect('/home')

@route('/exercicios/criar/<treino_id:int>', method='POST')
def criar_exercicio(treino_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s: return redirect('/login')
    
    Exercicio.create(
        nome=request.forms.get('nome_exercicio'),
        carga=request.forms.get('carga_exercicio'),
        repeticoes=int(request.forms.get('repeticoes_exercicio')),
        treino_id=treino_id
    )
    return redirect('/home')

@route('/exercicios/editar/<exercicio_id:int>', method='POST')
def editar_exercicio(exercicio_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s: return redirect('/login')
    
    Exercicio.update(
        exercicio_id=exercicio_id,
        novo_nome=request.forms.get('novo_nome_exercicio'),
        nova_carga=request.forms.get('nova_carga_exercicio'),
        novas_repeticoes=request.forms.get('novas_repeticoes_exercicio')
    )
    return redirect('/home')

@route('/exercicios/deletar/<exercicio_id:int>', method='POST')
def deletar_exercicio(exercicio_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s:
        return redirect('/login')
    
    Exercicio.delete(exercicio_id)
    return redirect('/home')

# ROTA DE PROGRESSÃO DE TREINO
@route('/treinos/progredir/<treino_id:int>', method='POST')
def progredir_treino_rota(treino_id):
    s = request.environ.get('beaker.session')
    if 'user_id' not in s:
        return redirect('/login')

    Treino.progredir_treino(treino_id)
    return redirect('/home?treino_concluido=true')

# --- ROTA WEBSOCKET ---
@route('/websocket')
def handle_websocket():
    wsock = request.environ.get('wsgi.websocket')
    if not wsock:
        from bottle import abort
        abort(400, 'Expected WebSocket request.')

    print("Conexão WebSocket aberta.")
    while not wsock.closed:
        try:
            message = wsock.receive()
            if message:
                print(f"Mensagem recebida do chat: {message}")
                # Apenas devolve a mensagem recebida (servidor de eco)
                wsock.send(f"{message}")

        except Exception as e:
            print(f"Erro no WebSocket: {e}")
            break
    print("Conexão WebSocket fechada.")