// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MercadoEnergiaLeilao {
    struct Oferta {
        address produtor;
        uint quantidadeDisponivel;
        uint precoAtualPorKwhEmReais;
        bool ativa;
    }

    struct Proposta {
        address comprador;
        uint quantidade;
        uint precoOferecidoPorKwhEmReais;
    }

    mapping(uint => Oferta) public ofertas;
    mapping(uint => Proposta) public melhoresPropostas;
    uint public numeroOfertas;

    event NovaOferta(address produtor, uint quantidade, uint precoAtualPorKwh);
    event NovaProposta(address comprador, uint ofertaIndex, uint quantidade, uint precoOferecidoPorKwhEmReais);
    event LeilaoFinalizado(address vencedor, uint ofertaIndex, uint quantidade, uint precoTotalEmReais);

    constructor() payable {} // Construtor tornando-se payable para receber ether durante a criação do contrato

    // Função para cadastrar oferta de energia para leilão
    function cadastrarOferta(uint _quantidadeDisponivel, uint _precoInicialPorKwhEmReais) public {
        require(_quantidadeDisponivel > 0, "Quantidade deve ser maior que zero");
        require(_precoInicialPorKwhEmReais > 0, "Preco deve ser maior que zero");

        ofertas[numeroOfertas] = Oferta(
            msg.sender,
            _quantidadeDisponivel,
            _precoInicialPorKwhEmReais,
            true
        );
        emit NovaOferta(msg.sender, _quantidadeDisponivel, _precoInicialPorKwhEmReais);
        numeroOfertas++;
    }

    // Função para fazer proposta de compra em uma oferta de leilão
    function fazerProposta(uint _ofertaIndex, uint _quantidadeDesejada, uint _precoOferecidoPorKwhEmReais) public {
        require(_ofertaIndex < numeroOfertas, "Oferta nao existe");
        Oferta storage oferta = ofertas[_ofertaIndex];

        require(oferta.ativa, "Oferta nao esta ativa");
        require(_quantidadeDesejada <= oferta.quantidadeDisponivel, "Quantidade desejada excede oferta disponivel");
        require(_precoOferecidoPorKwhEmReais > oferta.precoAtualPorKwhEmReais, "Preco oferecido abaixo do atual");

        oferta.precoAtualPorKwhEmReais = _precoOferecidoPorKwhEmReais;
        melhoresPropostas[_ofertaIndex] = Proposta(msg.sender, _quantidadeDesejada, _precoOferecidoPorKwhEmReais);

        emit NovaProposta(msg.sender, _ofertaIndex, _quantidadeDesejada, _precoOferecidoPorKwhEmReais);
    }

    // Função para finalizar o leilão automaticamente para a melhor oferta
    function finalizarLeilao(uint _ofertaIndex) public {
        require(_ofertaIndex < numeroOfertas, "Oferta nao existe");

        Proposta storage melhorProposta = melhoresPropostas[_ofertaIndex];
        require(melhorProposta.comprador != address(0), "Nao ha propostas validas");

        Oferta storage oferta = ofertas[_ofertaIndex];
        require(oferta.ativa, "Oferta nao esta ativa");
        require(oferta.quantidadeDisponivel >= melhorProposta.quantidade, "Quantidade desejada excede oferta disponivel");

        uint precoTotalEmReais = melhorProposta.precoOferecidoPorKwhEmReais * melhorProposta.quantidade;

        oferta.quantidadeDisponivel -= melhorProposta.quantidade;

        payable(oferta.produtor).transfer(precoTotalEmReais); // Pagamento em Ether equivalente ao preço total em reais

        emit LeilaoFinalizado(melhorProposta.comprador, _ofertaIndex, melhorProposta.quantidade, precoTotalEmReais);

        // Reset melhor proposta se a quantidade disponível da oferta chegar a zero
        if (oferta.quantidadeDisponivel == 0) {
            oferta.ativa = false;
            melhoresPropostas[_ofertaIndex] = Proposta(address(0), 0, 0);
        }
    }

    // Função para remover todas as ofertas (por exemplo, em caso de manutenção)
    function removerTodasOfertas() public {
        for (uint i = 0; i < numeroOfertas; i++) {
            if (ofertas[i].ativa) {
                ofertas[i].ativa = false;
                emit LeilaoFinalizado(address(0), i, 0, 0);
            }
        }
        numeroOfertas = 0; // Defina o número de ofertas como zero para limpar o mapa de ofertas
    }
}
