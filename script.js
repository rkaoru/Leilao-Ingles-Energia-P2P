document.getElementById('myForm1').addEventListener('submit', async function(event) {
    event.preventDefault();

    const quantity = parseInt(document.getElementById('quantity').value);
    const price = parseInt(document.getElementById('price').value);
    const address = document.getElementById('address').value;

    const response = await fetch('http://localhost:8000/cadastrar_oferta', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        quantidade_disponivel: quantity, 
        preco_minimo_por_kwh_em_reais: price, 
        sender_address: address 
      })
    });

    const result = await response.json();

    if (response.ok) {
      alert('Proposta enviada com sucesso! Transaction Hash: ' + result.transaction_hash);
    } else {
      alert('Erro ao enviar a proposta: ' + result.detail);
    }
});

document.getElementById('proposalForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const offerIndex = parseInt(document.getElementById('offerIndex').value);
    const desiredQuantity = parseInt(document.getElementById('desiredQuantity').value);
    const offeredPrice = parseInt(document.getElementById('offeredPrice').value);
    const address = document.getElementById('proposalAddress').value;

    try {
        const response = await fetch(`http://localhost:8000/fazer_proposta`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                oferta_index: offerIndex,
                quantidade_desejada: desiredQuantity,
                preco_oferecido_em_reais: offeredPrice,
                sender_address: address
            })
        });

        const result = await response.json();

        if (response.ok) {
            alert('Proposta enviada com sucesso! Transaction Hash: ' + result.transaction_hash);
            fetchOffers();  // Atualize a lista de ofertas após enviar a proposta
        } else {
            alert('Erro ao enviar a proposta: ' + result.detail);
        }
    } catch (error) {
        alert('Erro ao enviar a proposta: ' + error.message);
    }
});

document.getElementById('finalizeForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const finalizeIndex = document.getElementById('finalizeIndex').value;
    const address = document.getElementById('finalizeAddress').value;

    try {
        const response = await fetch(`http://localhost:8000/finalizar_compra/${finalizeIndex}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender_address: address })
        });

        const result = await response.json();

        if (response.ok) {
            alert('Compra finalizada com sucesso! Transaction Hash: ' + result.transaction_hash);
            fetchOffers();  // Atualize a lista de ofertas após finalizar a compra
        } else {
            alert('Erro ao finalizar a compra: ' + result.detail);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao finalizar a compra: ' + error.message);
    }
});

async function fetchOffers() {
    try {
        const response = await fetch('http://localhost:8000/offers');
        const result = await response.json();

        const offersList = document.getElementById('offersList');
        offersList.innerHTML = '';

        result.offers.forEach((offer, index) => {
            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item');
            listItem.innerHTML = `
                <strong>Índice da Oferta:</strong> ${index} <br>
                <strong>Produtor:</strong> ${offer.produtor} <br>
                <strong>Quantidade Disponível:</strong> ${offer.quantidadeDisponivel} <br>
                <strong>Preço Mínimo por kWh:</strong> ${offer.precoMinimoPorKwhEmReais} <br>
                <strong>Ativa:</strong> ${offer.ativa ? 'Sim' : 'Não'} <br>
                <strong>Transaction Hash:</strong> ${offer.transaction_hash}
            `;
            offersList.appendChild(listItem);
        });
    } catch (error) {
        console.error('Erro ao buscar ofertas:', error);
        alert('Erro ao buscar ofertas: ' + error.message);
    }
}

// Fetch offers when the page loads
document.addEventListener('DOMContentLoaded', fetchOffers);
