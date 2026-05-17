"""Payload mínimo válido para `POST /safra/proposal` (testes)."""


def minimal_safra_proposal_payload() -> dict:
    return {
        'contatos': [
            {'ddd': 11, 'telefone': '988771100', 'email': 'a@example.com'},
        ],
        'dadosBancarios': {
            'agencia': 1234,
            'banco': 76,
            'conta': '12345-6',
            'tipoConta': 'Corrente',
        },
        'dadosOcupacao': {},
        'dadosPessoais': {},
        'dadosProposta': {
            'idConvenio': 1,
            'idTabelaJuros': 2,
            'isCotacao': False,
            'valorParcela': 350.50,
            'prazo': 60,
            'valorPrincipal': 15000.0,
            'cpfAgenteCertificado': 12345678901,
            'dataPrimeiroVencimento': '2026-06-05T12:00:00Z',
        },
        'endereco': {
            'logradouro': 'Rua Teste',
            'numero': '42',
            'cep': '01310-100',
            'cidade': 'São Paulo',
            'uf': 'sp',
            'bairro': 'Centro',
            'complemento': 'Bloco A',
        },
        'submeter': False,
        'dadosBancariosAverbacao': {},
    }
