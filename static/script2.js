document.addEventListener('DOMContentLoaded', () => {

    // LÓGICA DO ACORDEÃO (ABRIR/FECHAR TREINOS)
    document.querySelectorAll('.workout-item').forEach(item => {
        const header = item.querySelector('.workout-header');
        if (header) {
            header.addEventListener('click', (e) => {
                // Impede que o clique nos botões feche o acordeão
                if (!e.target.closest('.workout-controls') && !e.target.closest('.inline-edit-form')) {
                    item.classList.toggle('active');
                }
            });
        }
    });

    // LÓGICA DO MODAL DE NOTIFICAÇÃO (PARA TREINO CONCLUÍDO)
    const notificationModal = document.getElementById('notificationModal');
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('treino_concluido')) {
        const notificationMessage = document.getElementById('notificationMessage');
        if (notificationModal && notificationMessage) {
            notificationMessage.innerHTML = "Parabéns, treino concluído e repetições atualizadas!<br><br>Exercícios que precisam de mais carga estão marcados em vermelho.";
            notificationModal.style.display = 'block';
        }
        // Limpa a URL para o pop-up não aparecer novamente ao recarregar
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // LÓGICA GERAL DOS MODAIS (ADICIONAR, DELETAR, NOTIFICAÇÃO)
    const addWorkoutModal = document.getElementById('addWorkoutModal');
    const deleteModal = document.getElementById('deleteWorkoutModal');
    
    // Botões de fechar e OK
    const okNotificationBtn = document.getElementById('okNotificationBtn');
    const closeNotificationBtn = notificationModal ? notificationModal.querySelector('.close-btn') : null;
    const addWorkoutBtn = document.getElementById('addWorkoutBtn');
    const closeAddBtn = addWorkoutModal ? addWorkoutModal.querySelector('.close-btn') : null;
    const confirmDeleteForm = document.getElementById('confirmDeleteForm');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    if (okNotificationBtn) okNotificationBtn.onclick = () => { notificationModal.style.display = 'none'; };
    if (closeNotificationBtn) closeNotificationBtn.onclick = () => { notificationModal.style.display = 'none'; };
    if (addWorkoutBtn) addWorkoutBtn.onclick = () => { addWorkoutModal.style.display = 'block'; };
    if (closeAddBtn) closeAddBtn.onclick = () => { addWorkoutModal.style.display = 'none'; };
    if (cancelDeleteBtn) cancelDeleteBtn.onclick = () => { deleteModal.style.display = 'none'; };

    // Lógica para abrir o modal de deleção
    document.querySelectorAll('.delete-workout-btn, .delete-exercise-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            const isWorkout = btn.classList.contains('delete-workout-btn');
            if (confirmDeleteForm) {
                confirmDeleteForm.action = isWorkout ? `/treinos/deletar/${id}` : `/exercicios/deletar/${id}`;
            }
            if (deleteModal) deleteModal.style.display = 'block';
        });
    });

    // LÓGICA PARA ATIVAR EDIÇÃO INLINE
    document.querySelectorAll('.edit-workout-btn, .edit-exercise-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isWorkout = btn.classList.contains('edit-workout-btn');
            const item = btn.closest(isWorkout ? '.workout-header' : '.exercise-item');
            const display = item.querySelector(isWorkout ? '.workout-title' : '.exercise-display');
            const form = item.querySelector(isWorkout ? '.inline-edit-form' : '.inline-exercise-edit-form');
            if (display) display.style.display = 'none';
            if (form) form.style.display = isWorkout ? 'flex' : 'grid';
        });
    });
    
    // LÓGICA PARA FECHAR MODAIS CLICANDO FORA
    window.onclick = function(event) {
        if (event.target == addWorkoutModal) addWorkoutModal.style.display = "none";
        if (event.target == deleteModal) deleteModal.style.display = "none";
        if (event.target == notificationModal) notificationModal.style.display = "none";
    }

    // --- LÓGICA DO WEBSOCKET PARA O CHAT DE TESTE ---
    const socket = new WebSocket('ws://' + window.location.host + '/websocket');
    const messagesDiv = document.getElementById('websocket-messages');
    const wsForm = document.getElementById('websocket-form');
    const wsInput = document.getElementById('websocket-input');

    // Apenas executa se os elementos do chat existirem na página
    if (messagesDiv && wsForm && wsInput) {
        socket.onopen = function(event) {
            console.log("Conexão WebSocket para chat estabelecida!");
            messagesDiv.innerHTML += '<p><em>Conectado ao servidor de chat!</em></p>';
        };

        socket.onmessage = function(event) {
            console.log("Mensagem do servidor de chat:", event.data);
            messagesDiv.innerHTML += `<p><strong>Servidor:</strong> ${event.data}</p>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };

        socket.onclose = function(event) {
            console.log("Conexão WebSocket do chat fechada.");
            messagesDiv.innerHTML += '<p><em>Desconectado do servidor de chat.</em></p>';
        };

        wsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = wsInput.value;
            if (message) {
                socket.send(message);
                messagesDiv.innerHTML += `<p><strong>Você:</strong> ${message}</p>`;
                wsInput.value = '';
            }
        });
    }
});