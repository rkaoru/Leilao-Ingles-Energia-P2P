document.addEventListener('DOMContentLoaded', function() {
    const fetchOfertas = () => {
        fetch('http://localhost:8000/ofertas/')
            .then(response => response.json())
            .then(data => {
                const ofertasTableBody = document.getElementById('ofertasTableBody');
                ofertasTableBody.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(oferta => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${oferta.nome}</td>
                            <td>${oferta.energia_disponivel}</td>
                            <td>${oferta.preco_minimo}</td>
                            <td>${oferta.time_limit}</td> <!-- Mostra o time_limit -->
                            <td>
                                <button type="button" class="btn btn-primary btn-sm abrirModal" data-id="${oferta.id}" data-toggle="modal" data-target="#chaveModal">Finalizar</button>
                            </td>
                        `;
                        ofertasTableBody.appendChild(row);
                    });
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    };

    fetchOfertas(); 

    document.getElementById('ofertaForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const oferta = {
            nome: document.getElementById('nome').value,
            endereco_publico: document.getElementById('enderecoPublico').value,
            endereco_privado: document.getElementById('enderecoPrivado').value,
            energia_disponivel: parseFloat(document.getElementById('energiaDisponivel').value),
            preco_minimo: parseFloat(document.getElementById('precoMinimo').value),
        };

        fetch('http://localhost:8000/ofertas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(oferta)
        })
        .then(response => response.json())
        .then(data => {
            alert('Oferta cadastrada com sucesso!');
            document.getElementById('ofertaForm').reset();
            fetchOfertas();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('abrirModal')) {
            const ofertaId = event.target.getAttribute('data-id');
            
            document.getElementById('chaveForm').addEventListener('submit', function(event) {
                event.preventDefault();
                const chavePublica = document.getElementById('chavePublica').value;
                const chavePrivada = document.getElementById('chavePrivada').value;

                const dadosChaves = {
                    oferta_id: ofertaId,
                    beneficiario_address: chavePublica,
                    beneficiario_private_key: chavePrivada
                };

                fetch('http://localhost:8000/finalizar_leilao/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(dadosChaves)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao finalizar o leilão');
                    }
                    return response.json();
                })
                .then(data => {
                    alert('Leilão finalizado com sucesso!');
                    $('#chaveModal').modal('hide');

                    const rowToRemove = document.querySelector(`tr[data-id="${ofertaId}"]`);
                    if (rowToRemove) {
                        rowToRemove.remove();
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            });
        }
    });
});