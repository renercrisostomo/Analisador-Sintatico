# Trabalho: Parser recursivo-descendente (sem lexer) + AST + modo pânico

## 1. Objetivo

Implementar (a partir de um código base inicial fornecido pelo professor) um parser recursivo-descendente que:

- Consome tokens prontos (não há lexer);
- Constrói a AST para expressões e statements;
- Possui modo pânico para continuar analisando após erros;
- Gera PNGs da árvore sintática de cada statement.

## 2. Código base fornecido

Você receberá um repositório/arquivo com:

- `Token` (dataclass) e tipos de token padronizados;
- Runner com 12 casos (5 válidos, 6 inválidos) e suporte a desenho de árvores (matplotlib).

## 3. Regras de uso do código base

- Pode ampliar casos de teste (recomendado), mas não remova os fornecidos.

## 4. Mensagens de erro & modo pânico

- Use `expect`/`expect_any` para padronizar mensagens, por exemplo:
  - Esperado `')'`
  - Esperado `'='`
  - Esperado um de: número, `true`, `false`, identificador, `'('`

- **Modo pânico**: ao errar, avance até um sincronizador `{ ';', 'EOL', '}', 'EOF' }` e consuma `;` ou `}` se estiver sobre eles, para não travar antes do `EOL`.

- O parser deve prosseguir após um erro e reportar múltiplos erros quando ocorrerem na mesma linha.

## 5. Como testar

Execute o runner: ele imprime para cada caso:

- `[RESULTADO] OK` — AST construída (e salva PNGs se habilitado); ou
- `[RESULTADO] ERROS SINTÁTICOS` com todas as mensagens `@ linha:col`.

## 6. O que entregar

- **Identificação**: No início do vídeo, deve constar o nome do(s) aluno(s) envolvido(s).
- **Formato da entrega**: A entrega consistirá em um vídeo de apresentação do trabalho, contendo:
  - Explicação completa do funcionamento do código desenvolvido;
  - Apresentação dos fundamentos teóricos relacionados;
  - Demonstração da execução do programa com os exemplos indicados.
- **Duração**: O vídeo deve ter cerca de 10 minutos.
- **Publicação**: O vídeo deve ser publicado no YouTube e o link disponibilizado no Classroom.
- **Código-fonte**: Além do vídeo, é obrigatório enviar o código-fonte utilizado no Google Colab.
- **Prazo de entrega**: Até o dia 26/09.
- **Forma de realização**: O trabalho pode ser feito individualmente ou em dupla.
