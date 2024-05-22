// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Mercado {
    struct Oferta {
        address produtor;
        uint256 quantidade;
        uint256 precoPorKWh;
        bool vendido;
        mapping(address => uint256) ofertasCompradores;
    }

    mapping(address => Oferta) public ofertas;
    address[] public produtores;
    
    event NovaOferta(address indexed produtor, uint256 quantidade, uint256 precoPorKWh);
    event OfertaAceita(address indexed produtor, address indexed comprador, uint256 quantidade, uint256 precoPorKWh);
    event OfertaRecusada(address indexed produtor, address indexed comprador, uint256 quantidade, uint256 precoPorKWh);
    event OfertaRealizada(address indexed comprador, address indexed produtor, uint256 quantidade, uint256 precoPorKWh);

    function cadastrarOferta(uint256 _quantidade, uint256 _precoPorKWh) public {
        require(ofertas[msg.sender].quantidade == 0, "Voce ja possui uma oferta cadastrada.");
        
        Oferta storage novaOferta = ofertas[msg.sender];
        novaOferta.produtor = msg.sender;
        novaOferta.quantidade = _quantidade;
        novaOferta.precoPorKWh = _precoPorKWh;
        novaOferta.vendido = false;

        produtores.push(msg.sender);

        emit NovaOferta(msg.sender, _quantidade, _precoPorKWh);
    }

    function visualizarOfertas() public view returns (address[] memory) {
        return produtores;
    }

    function fazerOferta(address _produtor) public payable {
        require(ofertas[_produtor].quantidade > 0, "O produtor nao possui uma oferta cadastrada.");
        require(msg.value >= ofertas[_produtor].precoPorKWh * ofertas[_produtor].quantidade, "Valor insuficiente.");

        // Marcar a oferta como vendida
        ofertas[_produtor].vendido = true;

        // Transferir pagamento para o produtor
        payable(_produtor).transfer(msg.value);

        emit OfertaAceita(_produtor, msg.sender, ofertas[_produtor].quantidade, ofertas[_produtor].precoPorKWh);
    }

    function fazerOfertaComprador(address _produtor, uint256 _quantidade, uint256 _precoOfertado) public payable {
        require(ofertas[_produtor].quantidade > 0, "O produtor nao possui uma oferta cadastrada.");
        require(_quantidade <= ofertas[_produtor].quantidade, "Quantidade ofertada maior que a disponivel.");
        require(_precoOfertado >= ofertas[_produtor].precoPorKWh, "Preco ofertado menor que o preco minimo.");

        ofertas[_produtor].ofertasCompradores[msg.sender] = _precoOfertado;

        emit OfertaRealizada(msg.sender, _produtor, _quantidade, _precoOfertado);
    }

    function recusarOferta(address _produtor) public {
        require(ofertas[_produtor].quantidade > 0, "O produtor nao possui uma oferta cadastrada.");

        emit OfertaRecusada(_produtor, msg.sender, ofertas[_produtor].quantidade, ofertas[_produtor].precoPorKWh);
    }
}
