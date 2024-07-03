let ofertas = [];
let ofertaSelecionada = null;

document.addEventListener('DOMContentLoaded', function() {
    carregarOfertas();

    function carregarOfertas() {
        fetch('http://localhost:8000/ofertas/')
            .then(response => response.json())
            .then(data => {
                ofertas = data;
                const ofertasTableBody = document.getElementById('ofertasTableBody');
                ofertasTableBody.innerHTML = ''; // Limpar tabela antes de recarregar
                data.forEach(oferta => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${oferta.nome}</td>
                        <td>${oferta.endereco_publico}</td>
                        <td>${oferta.energia_disponivel}</td>
                        <td>${oferta.preco_minimo}</td>
                        <td>${oferta.time_limit}</td>
                        <td><button class="btn btn-primary btn-proposta" data-id="${oferta.id}" data-toggle="modal" data-target="#propostaModal">Fazer Proposta</button></td>
                    `;
                    ofertasTableBody.appendChild(row);
                });

                document.querySelectorAll('.btn-proposta').forEach(button => {
                    button.addEventListener('click', function() {
                        const ofertaId = this.getAttribute('data-id');
                        ofertaSelecionada = ofertas.find(o => o.id === ofertaId);
                        document.getElementById('quantidadeDesejada').value = '';
                        document.getElementById('lance').value = '';
                        document.getElementById('accountAddress').value = '';
                        document.getElementById('privateKey').value = '';
                        document.getElementById('lanceMinimo').textContent = '';
                        document.getElementById('quantidadeAlerta').classList.add('d-none');
                        document.getElementById('erro').classList.add('d-none');

                        // Buscar e exibir o maior lance da oferta selecionada
                        fetch(`http://localhost:8000/maior_lance/${ofertaId}`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.maior_lance !== undefined && data.maior_lance !== null) {
                                    document.getElementById('infoMaiorLance').innerHTML = `<span class="info-label">Maior Lance:</span> R$ ${data.maior_lance.toFixed(2)}`;
                                    document.getElementById('infoComprador').innerHTML = `<span class="info-label">Comprador:</span> ${data.comprador}`;
                                    document.getElementById('infoQuantidadeProposta').innerHTML = `<span class="info-label">Quantidade Proposta:</span> ${data.quantidade_proposta} kWh`;
                                } else {
                                    document.getElementById('infoMaiorLance').innerHTML = '<span class="info-label">Maior Lance:</span> Sem lances até o momento';
                                    document.getElementById('infoComprador').innerHTML = '';
                                    document.getElementById('infoQuantidadeProposta').innerHTML = '';
                                }
                            })
                            .catch((error) => {
                                document.getElementById('infoMaiorLance').innerHTML = '<span class="info-label">Maior Lance:</span> Erro ao carregar o maior lance';
                                document.getElementById('infoComprador').innerHTML = '';
                                document.getElementById('infoQuantidadeProposta').innerHTML = '';
                                console.error('Error:', error);
                            });
                    });
                });
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    document.getElementById('quantidadeDesejada').addEventListener('input', function() {
        const quantidadeDesejada = parseFloat(this.value);
        if (ofertaSelecionada) {
            const precoMinimo = ofertaSelecionada.preco_minimo;
            const energiaDisponivel = ofertaSelecionada.energia_disponivel;
            if (quantidadeDesejada > energiaDisponivel) {
                document.getElementById('quantidadeAlerta').classList.remove('d-none');
            } else {
                document.getElementById('quantidadeAlerta').classList.add('d-none');
            }
            const lanceMinimo = quantidadeDesejada * precoMinimo;
            document.getElementById('lance').setAttribute('min', lanceMinimo);
            document.getElementById('lanceMinimo').textContent = `Lance mínimo: R$ ${lanceMinimo.toFixed(2)}`;
        }
    });

    document.getElementById('propostaForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const quantidadeDesejada = parseFloat(document.getElementById('quantidadeDesejada').value);
        const lance = parseFloat(document.getElementById('lance').value);
        const accountAddress = document.getElementById('accountAddress').value;
        const privateKey = document.getElementById('privateKey').value;

        if (ofertaSelecionada) {
            const precoMinimo = ofertaSelecionada.preco_minimo;
            const energiaDisponivel = ofertaSelecionada.energia_disponivel;
            const lanceMinimo = quantidadeDesejada * precoMinimo;

            if (quantidadeDesejada > energiaDisponivel) {
                document.getElementById('erro').textContent = `A quantidade desejada não pode ser maior que ${energiaDisponivel} kWh.`;
                document.getElementById('erro').classList.remove('d-none');
                return;
            }

            if (lance < lanceMinimo) {
                document.getElementById('erro').textContent = `O lance deve ser no mínimo R$ ${lanceMinimo.toFixed(2)}.`;
                document.getElementById('erro').classList.remove('d-none');
                return;
            }

            fetch('http://localhost:8000/fazer_lance/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    oferta_id: ofertaSelecionada.id, // Adicionado o ID da oferta selecionada
                    account_address: accountAddress,
                    private_key: privateKey,
                    lance_reais: lance,
                    quantidade_desejada: quantidadeDesejada // Adicionado a quantidade desejada
                }),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => { throw new Error(data.detail); });
                }
                return response.json();
            })
            .then(data => {
                alert('Proposta enviada com sucesso!');
                $('#propostaModal').modal('hide');
                carregarOfertas(); // Recarregar ofertas após fazer uma proposta
            })
            .catch((error) => {
                document.getElementById('erro').textContent = error.message;
                document.getElementById('erro').classList.remove('d-none');
            });
        }
    });
});