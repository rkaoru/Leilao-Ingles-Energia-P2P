// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MercadoEnergia {
    struct Oferta {
        address produtor;
        uint quantidadeDisponivel;
        uint precoMinimoPorKwhEmReais;
        bool ativa;
    }

    mapping(uint => Oferta) public ofertas;
    uint public numeroOfertas;
    address public comprador;
    uint public quantidadeComprada;
    uint public precoTotal;
    uint public etherToReais = 500; // Fator de conversão de ETH para Reais (por exemplo, 1 ETH = 500 Reais)

    event NovaOferta(address produtor, uint quantidade, uint precoMinimoPorKwh);
    event NovaProposta(address comprador, uint ofertaIndex, uint quantidade, uint preco);
    event CompraEfetuada(address comprador, uint quantidade, uint preco);
    event OfertaEsgotada(uint ofertaIndex);

    // Função para cadastrar oferta de energia
    function cadastrarOferta(uint _quantidadeDisponivel, uint _precoMinimoPorKwhEmReais) public {
        require(_quantidadeDisponivel > 0, "Quantidade deve ser maior que zero");
        require(_precoMinimoPorKwhEmReais > 0, "Preco deve ser maior que zero");

        ofertas[numeroOfertas] = Oferta(msg.sender, _quantidadeDisponivel, _precoMinimoPorKwhEmReais, true);
        emit NovaOferta(msg.sender, _quantidadeDisponivel, _precoMinimoPorKwhEmReais);
        numeroOfertas++;
    }

    // Função para visualizar todas as ofertas disponíveis
    function visualizarOfertas() public view returns (Oferta[] memory) {
        uint count = 0;
        for (uint i = 0; i < numeroOfertas; i++) {
            if (ofertas[i].quantidadeDisponivel > 0) {
                count++;
            }
        }
        Oferta[] memory todasAsOfertas = new Oferta[](count);
        count = 0;
        for (uint i = 0; i < numeroOfertas; i++) {
            if (ofertas[i].quantidadeDisponivel > 0) {
                todasAsOfertas[count] = ofertas[i];
                count++;
            }
        }
        return todasAsOfertas;
    }

    // Função para fazer proposta de compra
    function fazerProposta(uint _ofertaIndex, uint _quantidadeDesejada, uint _precoOferecidoEmReais) public {
        require(_ofertaIndex < numeroOfertas, "Oferta nao existe");
        Oferta storage oferta = ofertas[_ofertaIndex];

        require(oferta.ativa, "Oferta nao esta ativa");
        require(_quantidadeDesejada <= oferta.quantidadeDisponivel, "Quantidade desejada excede oferta disponivel");
        require(_precoOferecidoEmReais >= oferta.precoMinimoPorKwhEmReais, "Preco oferecido abaixo do minimo");

        quantidadeComprada = _quantidadeDesejada;
        // Converte o valor oferecido em reais para wei
        precoTotal = (_precoOferecidoEmReais * etherToReais) / 1 ether; // Convertendo para wei
        comprador = msg.sender;

        emit NovaProposta(msg.sender, _ofertaIndex, quantidadeComprada, precoTotal);
    }

    // Função para finalizar a compra
    function finalizarCompra() public payable {
        require(msg.sender == comprador, "Apenas o comprador pode finalizar a compra");
        require(msg.value >= precoTotal, "Valor insuficiente");

        uint melhorOfertaIndex = _encontrarMelhorOferta(quantidadeComprada);
        Oferta storage melhorOferta = ofertas[melhorOfertaIndex];

        require(melhorOferta.quantidadeDisponivel >= quantidadeComprada, "Quantidade desejada excede oferta disponivel");

        payable(melhorOferta.produtor).transfer(precoTotal);
        melhorOferta.quantidadeDisponivel -= quantidadeComprada;

        if (melhorOferta.quantidadeDisponivel == 0) {
            melhorOferta.ativa = false;
            emit OfertaEsgotada(melhorOfertaIndex);
            _removerOfertaEsgotada(melhorOfertaIndex);
        }

        comprador = address(0);
        quantidadeComprada = 0;
        precoTotal = 0;

        emit CompraEfetuada(msg.sender, quantidadeComprada, precoTotal);
    }

    // Função interna para encontrar a melhor oferta
    function _encontrarMelhorOferta(uint _quantidadeDesejada) private view returns (uint) {
        uint melhorIndex = 0;
        uint melhorPreco = type(uint).max; // Inicializado com o maior valor possível de uint

        for (uint i = 0; i < numeroOfertas; i++) {
            if (ofertas[i].ativa && ofertas[i].quantidadeDisponivel >= _quantidadeDesejada && ofertas[i].precoMinimoPorKwhEmReais < melhorPreco) {
                melhorIndex = i;
                melhorPreco = ofertas[i].precoMinimoPorKwhEmReais;
            }
        }

        return melhorIndex;
    }

    // Função interna para remover oferta esgotada
    function _removerOfertaEsgotada(uint _index) private {
        for (uint i = _index; i < numeroOfertas - 1; i++) {
            ofertas[i] = ofertas[i + 1];
        }
        delete ofertas[numeroOfertas - 1];
        numeroOfertas--;
    }
}
